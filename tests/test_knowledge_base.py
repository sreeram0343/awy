import os
import time
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from qdrant_client.http import models as rest_models

from app.models.vehicle import Vehicle
from app.models.variant import Variant
from app.models.spec import Spec
from app.models.review import Review
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.services.ingestion_service import ingestion_service
from app.db.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_structured_spec_lookup_latency_under_20ms():
    """
    Acceptance Criteria:
    Given a vehicle+variant, structured spec lookup returns in <20ms from DB.
    """
    async with AsyncSessionLocal() as session:
        # Fetch an arbitrary vehicle ID
        res = await session.execute(select(Vehicle.id).limit(1))
        vehicle_id = res.scalar_one_or_none()
        assert vehicle_id is not None, "Vehicle database must be populated"

        # Benchmark query latency with eager loading of variants, specs, and price history
        times = []
        for _ in range(5):
            t0 = time.perf_counter()
            stmt = (
                select(Vehicle)
                .where(Vehicle.id == vehicle_id)
                .options(
                    selectinload(Vehicle.variants).selectinload(Variant.spec),
                    selectinload(Vehicle.variants).selectinload(Variant.price_histories),
                )
            )
            result = await session.execute(stmt)
            vehicle = result.scalar_one()
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            times.append(elapsed_ms)

        avg_latency_ms = sum(times) / len(times)
        min_latency_ms = min(times)
        print(f"\nSpec lookup latency: min={min_latency_ms:.2f}ms, avg={avg_latency_ms:.2f}ms")

        assert vehicle is not None
        assert len(vehicle.variants) > 0
        assert vehicle.variants[0].spec is not None
        # Strict latency budget: must be well below 20ms
        assert min_latency_ms < 20.0, f"Lookup took {min_latency_ms:.2f}ms, expected < 20ms"


@pytest.mark.asyncio
async def test_semantic_search_retrieval_and_metadata():
    """
    Acceptance Criteria:
    Given a free-text query, top-k semantic matches from Qdrant return
    relevant review chunks with correct metadata.
    """
    qdrant_client = await qdrant_service.get_async_client()

    # Query 1: Luxury rear seat comfort
    comfort_query = "luxurious rear seats with ottoman leg rest and limousine space"
    comfort_vec = embedding_service.embed_text(comfort_query)

    search_res = await qdrant_client.query_points(
        collection_name=qdrant_service.collection_name,
        query=comfort_vec,
        limit=3,
        with_payload=True,
    )

    assert len(search_res.points) > 0
    top_hit = search_res.points[0]
    payload = top_hit.payload

    assert payload is not None
    assert "vehicle_id" in payload
    assert "topic" in payload
    assert "make" in payload
    assert "model" in payload
    # Top match should be Innova Hycross or Windsor EV or City
    assert payload["model"] in {"Innova Hycross", "Windsor EV", "City"}
    assert payload["topic"] == "comfort"

    # Query 2: Electric scooter acceleration
    scooter_query = "fast acceleration in warp mode electric scooter"
    scooter_vec = embedding_service.embed_text(scooter_query)

    search_scooter = await qdrant_client.query_points(
        collection_name=qdrant_service.collection_name,
        query=scooter_vec,
        limit=3,
        with_payload=True,
    )

    top_scooter = search_scooter.points[0]
    assert top_scooter.payload["model"] == "450X"
    assert top_scooter.payload["make"] == "Ather"
    assert top_scooter.payload["category"] == "2W"
    assert top_scooter.payload["topic"] == "performance"


@pytest.mark.asyncio
async def test_ingestion_idempotency_and_no_duplicate_vectors():
    """
    Acceptance Criteria:
    No duplicate vectors or review records on re-ingestion.
    """
    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pilot_vehicles.json")
    
    async with AsyncSessionLocal() as session:
        # Count existing reviews before run
        res_before = await session.execute(select(Review.id))
        count_before = len(res_before.scalars().all())

        # Re-run ingestion
        stats = await ingestion_service.ingest_dataset(data_file, session)

        # Count reviews after run
        res_after = await session.execute(select(Review.id))
        count_after = len(res_after.scalars().all())

        assert stats["reviews_ingested"] == 0, "No new reviews should be ingested on repeat run"
        assert stats["vectors_upserted"] == 0, "No new vectors should be upserted on repeat run"
        assert stats["reviews_skipped_duplicate"] == 80, "All 80 reviews should be recognized as duplicates"
        assert count_before == count_after, "Total reviews count in database must remain constant"
