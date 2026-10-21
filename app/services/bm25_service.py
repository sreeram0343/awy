import re
from typing import List, Dict, Any, Optional, Set, Tuple
from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.models.review import Review
from app.models.vehicle import Vehicle
from app.models.variant import Variant
from app.models.spec import Spec
from app.core.logging import logger


def tokenize(text: str) -> List[str]:
    """Simple alphanumeric lowercase tokenizer."""
    return [t for t in re.findall(r"\w+", text.lower()) if len(t) > 1]


class BM25SearchService:
    def __init__(self):
        self._bm25: Optional[BM25Okapi] = None
        self._doc_ids: List[str] = []
        self._doc_payloads: List[Dict[str, Any]] = []
        self._is_indexed = False

    @property
    def is_indexed(self) -> bool:
        return self._is_indexed

    async def build_index(self):
        """Index all reviews from the database into BM25 Okapi."""
        logger.info("Building BM25 sparse keyword index...")
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Review)
                .options(
                    selectinload(Review.vehicle),
                    selectinload(Review.variant).selectinload(Variant.spec),
                )
            )
            res = await session.execute(stmt)
            reviews = res.scalars().all()

        tokenized_corpus: List[List[str]] = []
        self._doc_ids = []
        self._doc_payloads = []

        for r in reviews:
            veh = r.vehicle
            var = r.variant
            spec = var.spec if var else None

            # Combine searchable technical tokens
            doc_text = f"{veh.make} {veh.model} {veh.category} {veh.body_type} {r.topic} {r.content} {r.source}"
            if var:
                doc_text += f" {var.name} {var.fuel_type} {var.transmission}"
            if spec:
                if spec.abs_type:
                    doc_text += f" {spec.abs_type} abs"
                if spec.ncap_rating:
                    doc_text += f" {spec.ncap_rating} star ncap safety"

            tokens = tokenize(doc_text)
            tokenized_corpus.append(tokens)

            point_id = r.vector_id or str(r.id)
            self._doc_ids.append(point_id)
            self._doc_payloads.append({
                "point_id": point_id,
                "vehicle_id": str(veh.id),
                "variant_id": str(var.id) if var else None,
                "make": veh.make,
                "model": veh.model,
                "category": veh.category,
                "body_type": veh.body_type,
                "fuel_type": var.fuel_type if var else None,
                "topic": r.topic,
                "content": r.content,
                "source": r.source,
                "rating": float(r.rating) if r.rating else None,
                "abs_type": spec.abs_type if spec else None,
                "ncap_rating": spec.ncap_rating if spec else None,
            })

        if tokenized_corpus:
            self._bm25 = BM25Okapi(tokenized_corpus)
            self._is_indexed = True
            logger.info(f"BM25 index built with {len(self._doc_ids)} documents.")
        else:
            logger.warning("No review records found to index for BM25.")

    def search(
        self,
        query: str,
        top_k: int = 20,
        allowed_ids: Optional[Set[str]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Execute BM25 keyword search.
        If allowed_ids is provided, filter candidates strictly to allowed IDs.
        Returns list of (point_id, bm25_score, payload).
        """
        if not self._bm25 or not self._doc_ids:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)
        results = []

        for idx, score in enumerate(scores):
            if score <= 0.0:
                continue
            doc_id = self._doc_ids[idx]
            if allowed_ids is not None and doc_id not in allowed_ids:
                continue
            results.append((doc_id, float(score), self._doc_payloads[idx]))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


bm25_service = BM25SearchService()
