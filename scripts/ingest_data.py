import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.services.ingestion_service import ingestion_service
from app.core.logging import logger


async def main():
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pilot_vehicles.json")
    if not os.path.exists(data_file):
        logger.error(f"Data file not found at '{data_file}'")
        sys.exit(1)

    logger.info(f"Starting ingestion from '{data_file}'...")
    async with AsyncSessionLocal() as session:
        stats = await ingestion_service.ingest_dataset(data_file, session)

    logger.info("=" * 60)
    logger.info("INGESTION RUN SUMMARY:")
    for k, v in stats.items():
        logger.info(f"  {k}: {v}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
