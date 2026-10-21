import json
import uuid
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.http import models as rest_models

from app.models.vehicle import Vehicle
from app.models.variant import Variant
from app.models.spec import Spec
from app.models.pricing import PriceHistory
from app.models.review import Review
from app.services.chunking_service import ReviewChunker, ReviewChunk
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.core.logging import logger


class IngestionService:
    def __init__(self, source_version: str = "v2026.10.1"):
        self.source_version = source_version

    async def ingest_dataset(
        self,
        dataset_path: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Idempotently ingest automotive dataset containing structured specs,
        pricing history, and unstructured review chunks into PostgreSQL and Qdrant.
        """
        with open(dataset_path, "r", encoding="utf-8") as f:
            data: List[Dict[str, Any]] = json.load(f)

        logger.info(f"Loaded {len(data)} vehicles from '{dataset_path}' for ingestion...")

        # Ensure Qdrant collection is ready
        await qdrant_service.init_collection()
        qdrant_client = await qdrant_service.get_async_client()

        stats = {
            "vehicles_processed": 0,
            "vehicles_created": 0,
            "variants_created": 0,
            "prices_recorded": 0,
            "reviews_ingested": 0,
            "reviews_skipped_duplicate": 0,
            "vectors_upserted": 0,
        }

        for v_data in data:
            stats["vehicles_processed"] += 1
            make = v_data["make"].strip()
            model = v_data["model"].strip()
            category = v_data["category"].strip()
            body_type = v_data["body_type"].strip()

            # 1. Idempotently get or create Vehicle
            stmt = select(Vehicle).where(Vehicle.make == make, Vehicle.model == model)
            res = await db.execute(stmt)
            vehicle = res.scalar_one_or_none()

            if not vehicle:
                vehicle = Vehicle(
                    make=make,
                    model=model,
                    category=category,
                    body_type=body_type,
                )
                db.add(vehicle)
                await db.flush()
                stats["vehicles_created"] += 1
            else:
                vehicle.category = category
                vehicle.body_type = body_type
                vehicle.updated_at = datetime.now(timezone.utc)
                await db.flush()

            # Process variants
            first_variant = None
            first_spec = None
            min_price: Optional[float] = None
            max_price: Optional[float] = None

            for var_data in v_data.get("variants", []):
                var_name = var_data["name"].strip()
                fuel_type = var_data["fuel_type"].strip()
                transmission = var_data["transmission"].strip()

                stmt = select(Variant).where(
                    Variant.vehicle_id == vehicle.id,
                    Variant.name == var_name
                )
                res = await db.execute(stmt)
                variant = res.scalar_one_or_none()

                if not variant:
                    variant = Variant(
                        vehicle_id=vehicle.id,
                        name=var_name,
                        fuel_type=fuel_type,
                        transmission=transmission,
                        engine_capacity_cc=var_data.get("engine_capacity_cc"),
                        motor_power_kw=var_data.get("motor_power_kw"),
                        battery_capacity_kwh=var_data.get("battery_capacity_kwh"),
                        is_active=True,
                    )
                    db.add(variant)
                    await db.flush()
                    stats["variants_created"] += 1
                else:
                    variant.fuel_type = fuel_type
                    variant.transmission = transmission
                    variant.engine_capacity_cc = var_data.get("engine_capacity_cc")
                    variant.motor_power_kw = var_data.get("motor_power_kw")
                    variant.battery_capacity_kwh = var_data.get("battery_capacity_kwh")
                    await db.flush()

                if first_variant is None:
                    first_variant = variant

                # Process Variant Specs
                spec_data = var_data.get("spec")
                if spec_data:
                    stmt = select(Spec).where(Spec.variant_id == variant.id)
                    res = await db.execute(stmt)
                    spec = res.scalar_one_or_none()

                    if not spec:
                        spec = Spec(
                            variant_id=variant.id,
                            seating_capacity=spec_data.get("seating_capacity"),
                            mileage_kpl=spec_data.get("mileage_kpl"),
                            ev_range_km=spec_data.get("ev_range_km"),
                            ncap_rating=spec_data.get("ncap_rating"),
                            airbags_count=spec_data.get("airbags_count", 2),
                            abs_type=spec_data.get("abs_type"),
                            ground_clearance_mm=spec_data.get("ground_clearance_mm"),
                            length_mm=spec_data.get("length_mm"),
                            width_mm=spec_data.get("width_mm"),
                            height_mm=spec_data.get("height_mm"),
                            wheelbase_mm=spec_data.get("wheelbase_mm"),
                            boot_space_litres=spec_data.get("boot_space_litres"),
                            extra_features=spec_data.get("extra_features"),
                        )
                        db.add(spec)
                        await db.flush()
                    else:
                        spec.seating_capacity = spec_data.get("seating_capacity")
                        spec.mileage_kpl = spec_data.get("mileage_kpl")
                        spec.ev_range_km = spec_data.get("ev_range_km")
                        spec.ncap_rating = spec_data.get("ncap_rating")
                        spec.airbags_count = spec_data.get("airbags_count", 2)
                        spec.abs_type = spec_data.get("abs_type")
                        spec.ground_clearance_mm = spec_data.get("ground_clearance_mm")
                        spec.length_mm = spec_data.get("length_mm")
                        spec.width_mm = spec_data.get("width_mm")
                        spec.height_mm = spec_data.get("height_mm")
                        spec.wheelbase_mm = spec_data.get("wheelbase_mm")
                        spec.boot_space_litres = spec_data.get("boot_space_litres")
                        spec.extra_features = spec_data.get("extra_features")
                        await db.flush()

                    if first_spec is None:
                        first_spec = spec

                # Process Pricing
                for p_entry in var_data.get("prices", []):
                    st_code = p_entry["state_code"].strip().upper()
                    ex_price = float(p_entry["ex_showroom_price"])
                    eff_date = datetime.strptime(p_entry["effective_date"], "%Y-%m-%d").date()

                    if min_price is None or ex_price < min_price:
                        min_price = ex_price
                    if max_price is None or ex_price > max_price:
                        max_price = ex_price

                    stmt = select(PriceHistory).where(
                        PriceHistory.variant_id == variant.id,
                        PriceHistory.state_code == st_code,
                        PriceHistory.effective_date == eff_date,
                    )
                    res = await db.execute(stmt)
                    existing_price = res.scalar_one_or_none()

                    if not existing_price:
                        ph = PriceHistory(
                            variant_id=variant.id,
                            state_code=st_code,
                            ex_showroom_price=ex_price,
                            effective_date=eff_date,
                            source_version=self.source_version,
                        )
                        db.add(ph)
                        await db.flush()
                        stats["prices_recorded"] += 1
                    else:
                        existing_price.ex_showroom_price = ex_price
                        existing_price.source_version = self.source_version
                        await db.flush()

            # Process Unstructured Review Chunks
            for r_data in v_data.get("reviews", []):
                topic = r_data["topic"]
                content = r_data["content"]
                source = r_data.get("source", "Automotive Editorial")
                rating = r_data.get("rating")

                # Generate chunk with SHA-256 hash
                chunk: ReviewChunk = ReviewChunker.chunk_structured_review(
                    vehicle_id=str(vehicle.id),
                    variant_id=str(first_variant.id) if first_variant else None,
                    topic=topic,
                    content=content,
                    source=source,
                    rating=rating,
                    source_version=self.source_version,
                    extra_metadata={
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "category": vehicle.category,
                        "body_type": vehicle.body_type,
                        "abs_type": first_spec.abs_type if first_spec else None,
                        "ncap_rating": first_spec.ncap_rating if first_spec else None,
                        "airbags_count": first_spec.airbags_count if first_spec else 0,
                        "fuel_type": first_variant.fuel_type if first_variant else None,
                        "min_price": min_price,
                        "max_price": max_price,
                    }
                )

                # Check PostgreSQL idempotency
                stmt = select(Review).where(Review.chunk_hash == chunk.chunk_hash)
                res = await db.execute(stmt)
                existing_review = res.scalar_one_or_none()

                if existing_review:
                    # Refresh payload in Qdrant with any new metadata fields
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_hash))
                    await qdrant_client.set_payload(
                        collection_name=qdrant_service.collection_name,
                        payload=chunk.metadata,
                        points=[point_id],
                    )
                    stats["reviews_skipped_duplicate"] += 1
                    continue

                # Generate vector embedding using FastEmbed (BGE model)
                vector = embedding_service.embed_text(chunk.content)

                # Generate deterministic Qdrant point UUID from chunk_hash
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_hash))

                # Upsert into Qdrant vector store
                await qdrant_client.upsert(
                    collection_name=qdrant_service.collection_name,
                    points=[
                        rest_models.PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=chunk.metadata | {
                                "content": chunk.content,
                                "ingested_at": datetime.now(timezone.utc).isoformat(),
                            }
                        )
                    ]
                )
                stats["vectors_upserted"] += 1

                # Save Review record in Postgres
                review_record = Review(
                    vehicle_id=vehicle.id,
                    variant_id=first_variant.id if first_variant else None,
                    topic=chunk.topic,
                    content=chunk.content,
                    source=chunk.source,
                    rating=chunk.rating,
                    chunk_hash=chunk.chunk_hash,
                    vector_id=point_id,
                    source_version=self.source_version,
                    ingested_at=datetime.now(timezone.utc),
                )
                db.add(review_record)
                await db.flush()
                stats["reviews_ingested"] += 1

        await db.commit()
        logger.info(f"Ingestion complete: {stats}")
        return stats


ingestion_service = IngestionService()
