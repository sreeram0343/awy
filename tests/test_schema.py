import pytest
from datetime import date, datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.vehicle import Vehicle
from app.models.variant import Variant
from app.models.spec import Spec
from app.models.pricing import PriceHistory
from app.models.review import Review
from app.models.lead import Lead


@pytest.mark.asyncio
async def test_vehicle_and_variant_creation(test_db):
    # 1. Create Vehicle
    vehicle = Vehicle(make="Hyundai", model="Creta", category="4W", body_type="SUV")
    test_db.add(vehicle)
    await test_db.flush()

    assert vehicle.id is not None

    # 2. Create Variant
    variant = Variant(
        vehicle_id=vehicle.id,
        name="SX (O) 1.5 Turbo DCT",
        fuel_type="Petrol",
        transmission="Automatic",
        engine_capacity_cc=1482.0,
    )
    test_db.add(variant)
    await test_db.flush()

    # 3. Create Spec
    spec = Spec(
        variant_id=variant.id,
        seating_capacity=5,
        mileage_kpl=18.4,
        ncap_rating=5,
        airbags_count=6,
        abs_type="Dual-Channel",
        extra_features={"panoramic_sunroof": True, "adas_level": 2},
    )
    test_db.add(spec)

    # 4. Create PriceHistory
    price = PriceHistory(
        variant_id=variant.id,
        state_code="DL",
        ex_showroom_price=2000000.0,
        effective_date=date(2026, 1, 1),
        source_version="v1.0",
    )
    test_db.add(price)

    # 5. Create Review
    review = Review(
        vehicle_id=vehicle.id,
        variant_id=variant.id,
        topic="performance",
        content="The 1.5 DCT is responsive and quick off the line.",
        source="Test Review",
        rating=4.5,
        chunk_hash="abc123hash",
    )
    test_db.add(review)

    # 6. Create Lead
    lead = Lead(
        variant_id=variant.id,
        user_name="John Doe",
        user_email="john@example.com",
        user_phone="9876543210",
        state_code="DL",
        dealership_id="DLR-101",
        computed_on_road_price=2300000.0,
        status="created",
        consent_given=True,
        consent_timestamp=datetime.now(timezone.utc),
    )
    test_db.add(lead)

    await test_db.commit()

    # Query back & verify relationships
    stmt = (
        select(Vehicle)
        .where(Vehicle.id == vehicle.id)
        .options(
            selectinload(Vehicle.variants).selectinload(Variant.spec)
        )
    )
    res = await test_db.execute(stmt)
    fetched_vehicle = res.scalar_one()

    assert fetched_vehicle.make == "Hyundai"
    assert fetched_vehicle.model == "Creta"
    assert len(fetched_vehicle.variants) == 1
    assert fetched_vehicle.variants[0].name == "SX (O) 1.5 Turbo DCT"
    assert fetched_vehicle.variants[0].spec.abs_type == "Dual-Channel"
    assert fetched_vehicle.variants[0].spec.extra_features["adas_level"] == 2
