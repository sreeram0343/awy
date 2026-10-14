from fastapi import APIRouter
from app.api.v1.endpoints import health, vehicles, search, financial, leads, voice

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(financial.router, prefix="/calculate", tags=["Financial"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
