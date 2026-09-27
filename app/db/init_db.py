import asyncio
from datetime import date, datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.models.vehicle import Vehicle
from app.models.variant import Variant
from app.models.spec import Spec
from app.models.pricing import PriceHistory
from app.core.logging import logger


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified / created successfully.")


async def seed_pilot_data(db: AsyncSession):
    """Seed initial pilot vehicles (4W and 2W) for verification."""
    result = await db.execute(select(Vehicle).limit(1))
    if result.scalar_one_or_none():
        logger.info("Database already seeded with vehicles.")
        return

    logger.info("Seeding pilot vehicles, variants, specs, and pricing...")

    # 1. Tata Nexon (4W - SUV)
    nexon = Vehicle(
        make="Tata",
        model="Nexon",
        category="4W",
        body_type="SUV",
    )
    db.add(nexon)
    await db.flush()

    nexon_creative = Variant(
        vehicle_id=nexon.id,
        name="Creative Plus 1.2 Petrol MT",
        fuel_type="Petrol",
        transmission="Manual",
        engine_capacity_cc=1199.0,
        is_active=True,
    )
    db.add(nexon_creative)
    await db.flush()

    nexon_spec = Spec(
        variant_id=nexon_creative.id,
        seating_capacity=5,
        mileage_kpl=17.44,
        ncap_rating=5,
        airbags_count=6,
        abs_type="Dual-Channel",
        ground_clearance_mm=208.0,
        length_mm=3995.0,
        width_mm=1804.0,
        height_mm=1620.0,
        wheelbase_mm=2498.0,
        boot_space_litres=382.0,
        extra_features={"sunroof": True, "touchscreen_in": 10.25, "ventilated_seats": False},
    )
    db.add(nexon_spec)

    nexon_price_mh = PriceHistory(
        variant_id=nexon_creative.id,
        state_code="MH",
        ex_showroom_price=1100000.00,
        effective_date=date(2026, 1, 1),
        source_version="v2026.09.1",
    )
    db.add(nexon_price_mh)

    # 2. Royal Enfield Classic 350 (2W - Cruiser)
    classic350 = Vehicle(
        make="Royal Enfield",
        model="Classic 350",
        category="2W",
        body_type="Cruiser",
    )
    db.add(classic350)
    await db.flush()

    re_dark = Variant(
        vehicle_id=classic350.id,
        name="Dark Stealth Black",
        fuel_type="Petrol",
        transmission="Manual",
        engine_capacity_cc=349.0,
        is_active=True,
    )
    db.add(re_dark)
    await db.flush()

    re_spec = Spec(
        variant_id=re_dark.id,
        seating_capacity=2,
        mileage_kpl=36.2,
        ncap_rating=None,
        airbags_count=0,
        abs_type="Dual-Channel",
        ground_clearance_mm=170.0,
        length_mm=2145.0,
        width_mm=785.0,
        height_mm=1090.0,
        wheelbase_mm=1390.0,
        extra_features={"alloy_wheels": True, "tripper_navigation": True},
    )
    db.add(re_spec)

    re_price_mh = PriceHistory(
        variant_id=re_dark.id,
        state_code="MH",
        ex_showroom_price=225000.00,
        effective_date=date(2026, 1, 1),
        source_version="v2026.09.1",
    )
    db.add(re_price_mh)

    await db.commit()
    logger.info("Pilot seed data committed successfully.")


if __name__ == "__main__":
    async def main():
        await init_db()
        async with AsyncSessionLocal() as session:
            await seed_pilot_data(session)

    asyncio.run(main())
