from fastapi import APIRouter
from app.schemas.health import APIEnvelope
from app.schemas.search import HybridSearchRequest, HybridSearchResponse
from app.services.hybrid_search_service import hybrid_search_service

router = APIRouter()


@router.post("", response_model=APIEnvelope[HybridSearchResponse])
async def search_vehicles(payload: HybridSearchRequest):
    """
    Production-grade hybrid search endpoint combining dense vectors (Qdrant)
    with sparse BM25 keyword matching and strict hard-constraint enforcement.
    """
    response_data = await hybrid_search_service.search(payload)
    return APIEnvelope[HybridSearchResponse](data=response_data)
