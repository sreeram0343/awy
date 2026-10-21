import time
from typing import List, Dict, Any, Optional, Set
from qdrant_client.http import models as rest_models

from app.services.query_parser import QueryParser, ExtractedConstraints
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.services.bm25_service import bm25_service
from app.schemas.search import (
    HybridSearchRequest,
    HybridSearchResponse,
    SearchMatchItem,
    FilterConstraint,
)
from app.core.logging import logger


class HybridSearchService:
    def __init__(self, rrf_k: int = 60, dense_weight: float = 0.6, sparse_weight: float = 0.4):
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def build_qdrant_filter(self, constraints: ExtractedConstraints) -> Optional[rest_models.Filter]:
        """Convert extracted hard constraints into Qdrant Filter conditions."""
        must_conditions = []

        if constraints.category:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="category",
                    match=rest_models.MatchValue(value=constraints.category)
                )
            )

        if constraints.fuel_type:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="fuel_type",
                    match=rest_models.MatchValue(value=constraints.fuel_type)
                )
            )

        if constraints.body_type:
            body = constraints.body_type.lower()
            matching_types = []
            if "scooter" in body:
                matching_types = ["Scooter", "Electric Scooter"]
            elif "suv" in body:
                matching_types = ["SUV", "Micro SUV", "Compact SUV", "CUV"]
            elif "hatch" in body:
                matching_types = ["Hatchback"]
            elif "sedan" in body:
                matching_types = ["Sedan"]
            elif "cruiser" in body:
                matching_types = ["Cruiser", "Roadster"]
            elif "streetfighter" in body or "naked" in body:
                matching_types = ["Streetfighter", "Naked Streetfighter"]
            elif "commuter" in body:
                matching_types = ["Commuter", "Sports Commuter"]
            elif "mpv" in body or "7 seater" in body:
                matching_types = ["MPV", "SUV"]
            else:
                matching_types = [constraints.body_type]

            if len(matching_types) > 1:
                must_conditions.append(
                    rest_models.Filter(
                        should=[
                            rest_models.FieldCondition(
                                key="body_type",
                                match=rest_models.MatchValue(value=bt)
                            )
                            for bt in matching_types
                        ]
                    )
                )
            else:
                must_conditions.append(
                    rest_models.FieldCondition(
                        key="body_type",
                        match=rest_models.MatchValue(value=matching_types[0])
                    )
                )

        if constraints.abs_type:
            if constraints.abs_type == "Dual-Channel":
                # Matches either Dual-Channel or Cornering ABS
                must_conditions.append(
                    rest_models.Filter(
                        should=[
                            rest_models.FieldCondition(
                                key="abs_type",
                                match=rest_models.MatchValue(value="Dual-Channel")
                            ),
                            rest_models.FieldCondition(
                                key="abs_type",
                                match=rest_models.MatchValue(value="Cornering ABS")
                            ),
                        ]
                    )
                )
            else:
                must_conditions.append(
                    rest_models.FieldCondition(
                        key="abs_type",
                        match=rest_models.MatchValue(value=constraints.abs_type)
                    )
                )

        if constraints.min_ncap_rating is not None:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="ncap_rating",
                    range=rest_models.Range(gte=float(constraints.min_ncap_rating))
                )
            )

        if constraints.min_airbags is not None:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="airbags_count",
                    range=rest_models.Range(gte=float(constraints.min_airbags))
                )
            )

        if constraints.max_price is not None:
            # Vehicle minimum ex-showroom price must be within ceiling
            must_conditions.append(
                rest_models.FieldCondition(
                    key="min_price",
                    range=rest_models.Range(lte=float(constraints.max_price))
                )
            )

        if constraints.min_price is not None:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="max_price",
                    range=rest_models.Range(gte=float(constraints.min_price))
                )
            )

        if not must_conditions:
            return None

        return rest_models.Filter(must=must_conditions)

    async def search(self, request: HybridSearchRequest) -> HybridSearchResponse:
        t_start = time.perf_counter()

        # Ensure BM25 index is loaded
        if not bm25_service.is_indexed:
            await bm25_service.build_index()

        # 1. Natural Language Query Understanding & Hard Constraint Extraction
        constraints = QueryParser.parse_query(
            query=request.query,
            explicit_category=request.vehicle_type,
            explicit_filters=request.filters,
        )

        qdrant_filter = self.build_qdrant_filter(constraints)
        qdrant_client = await qdrant_service.get_async_client()

        # 2. Retrieve Filter-Compliant Points
        # If filters exist, scroll matching IDs so both dense and sparse BM25 are hard-constrained
        allowed_point_ids: Optional[Set[str]] = None
        if qdrant_filter is not None:
            scroll_res, _ = await qdrant_client.scroll(
                collection_name=qdrant_service.collection_name,
                scroll_filter=qdrant_filter,
                limit=500,
                with_payload=False,
                with_vectors=False,
            )
            allowed_point_ids = {str(p.id) for p in scroll_res}
            if not allowed_point_ids:
                # No candidates satisfy the hard constraints
                return HybridSearchResponse(
                    total_matches=0,
                    query=request.query,
                    applied_filters={k: v for k, v in constraints.model_dump().items() if v is not None and k != "clean_query"},
                    results=[]
                )

        # 3. Dense Vector Search (Qdrant)
        fetch_k = max(request.top_k * 3, 20)
        query_vector = embedding_service.embed_text(request.query)

        dense_search_res = await qdrant_client.query_points(
            collection_name=qdrant_service.collection_name,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=fetch_k,
            with_payload=True,
        )

        dense_ranks: Dict[str, int] = {}
        payloads: Dict[str, Dict[str, Any]] = {}
        for rank, point in enumerate(dense_search_res.points, start=1):
            pid = str(point.id)
            dense_ranks[pid] = rank
            payloads[pid] = point.payload or {}

        # 4. Sparse BM25 Keyword Search
        bm25_matches = bm25_service.search(
            query=request.query,
            top_k=fetch_k,
            allowed_ids=allowed_point_ids,
        )

        sparse_ranks: Dict[str, int] = {}
        for rank, (doc_id, bm_score, p_data) in enumerate(bm25_matches, start=1):
            sparse_ranks[doc_id] = rank
            if doc_id not in payloads:
                payloads[doc_id] = p_data

        # 5. Reciprocal Rank Fusion (RRF)
        all_candidate_ids = set(dense_ranks.keys()) | set(sparse_ranks.keys())
        rrf_scores: Dict[str, float] = {}

        for doc_id in all_candidate_ids:
            dense_rank = dense_ranks.get(doc_id, 999)
            sparse_rank = sparse_ranks.get(doc_id, 999)

            score = (
                self.dense_weight / (self.rrf_k + dense_rank)
                + self.sparse_weight / (self.rrf_k + sparse_rank)
            )
            rrf_scores[doc_id] = score

        # Sort by final RRF score descending
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        # Normalize top score to 1.0 scale if scores exist
        max_rrf = sorted_candidates[0][1] if sorted_candidates else 1.0

        results: List[SearchMatchItem] = []
        for doc_id, raw_score in sorted_candidates[:request.top_k]:
            payload = payloads.get(doc_id, {})
            normalized_score = round(raw_score / max_rrf, 4)

            item = SearchMatchItem(
                chunk_id=doc_id,
                vehicle_id=str(payload.get("vehicle_id", "")),
                variant_id=str(payload.get("variant_id", "")) if payload.get("variant_id") else None,
                vehicle_make=str(payload.get("make", "")),
                vehicle_model=str(payload.get("model", "")),
                topic=str(payload.get("topic", "")),
                content=str(payload.get("content", "")),
                score=normalized_score,
                metadata=payload,
            )
            results.append(item)

        elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
        logger.info(
            f"Hybrid search '{request.query}' completed in {elapsed_ms}ms with {len(results)} matches"
        )

        applied_filters_dict = {
            k: v for k, v in constraints.model_dump().items()
            if v is not None and k != "clean_query"
        }

        return HybridSearchResponse(
            total_matches=len(results),
            query=request.query,
            applied_filters=applied_filters_dict,
            results=results,
        )


hybrid_search_service = HybridSearchService()
