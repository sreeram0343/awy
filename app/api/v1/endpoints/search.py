from fastapi import APIRouter, Depends
from app.schemas.health import APIEnvelope
from app.schemas.search import HybridSearchRequest, HybridSearchResponse

router = APIRouter()


@router.post("", response_model=APIEnvelope[HybridSearchResponse])
async def search_vehicles(payload: HybridSearchRequest):
    """
    Hybrid (dense vector + sparse BM25) search endpoint with strict filter enforcement.
    """
    # Baseline stub response for Phase 0
    response_data = HybridSearchResponse(
        total_matches=0,
        query=payload.query,
        applied_filters=payload.filters.model_dump() if payload.filters else {},
        results=[]
    )
    return APIEnvelope[HybridSearchResponse](data=response_data)
