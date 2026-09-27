import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, database_url
from app.services.qdrant_service import qdrant_service
from app.schemas.health import APIEnvelope, SystemHealthData, DatabaseHealth, QdrantHealth
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=APIEnvelope[SystemHealthData])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint verifying:
    1. PostgreSQL database connectivity & query execution latency
    2. Qdrant vector database connectivity & collection status
    """
    # 1. Check DB connectivity
    db_start = time.perf_counter()
    db_status = "healthy"
    db_error = None
    try:
        await db.execute(text("SELECT 1"))
        db_latency_ms = round((time.perf_counter() - db_start) * 1000, 2)
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)
        db_latency_ms = round((time.perf_counter() - db_start) * 1000, 2)

    db_health = DatabaseHealth(
        status=db_status,
        engine="postgresql+asyncpg" if "postgresql" in database_url else "sqlite",
        latency_ms=db_latency_ms,
        error=db_error,
    )

    # 2. Check Qdrant connectivity
    qdrant_res = await qdrant_service.check_health()
    qdrant_health = QdrantHealth(
        status=qdrant_res.get("status", "unhealthy"),
        host=qdrant_res.get("host", settings.QDRANT_HOST),
        port=qdrant_res.get("port", settings.QDRANT_PORT),
        collection_exists=qdrant_res.get("collection_exists", False),
        collections=qdrant_res.get("collections"),
        error=qdrant_res.get("error"),
    )

    overall_status = (
        "healthy" if (db_status == "healthy" and qdrant_health.status == "healthy") else "degraded"
    )

    data = SystemHealthData(
        app_name=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        database=db_health,
        qdrant=qdrant_health,
        overall_status=overall_status,
    )

    return APIEnvelope[SystemHealthData](data=data)
