from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.vehicle import Vehicle
from app.models.variant import Variant
from app.models.spec import Spec
from app.models.pricing import PriceHistory
from app.schemas.health import APIEnvelope
from app.schemas.vehicle import VehicleResponse, VehicleSpecDetailResponse

router = APIRouter()


@router.get("/{id}/specs", response_model=APIEnvelope[VehicleSpecDetailResponse])
async def get_vehicle_specs(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get structured vehicle specifications by vehicle ID.
    Sub-20ms latency target.
    """
    query = (
        select(Vehicle)
        .where(Vehicle.id == id)
        .options(
            selectinload(Vehicle.variants)
            .selectinload(Variant.spec),
            selectinload(Vehicle.variants)
            .selectinload(Variant.price_histories)
        )
    )
    result = await db.execute(query)
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID '{id}' not found"
        )

    return APIEnvelope[VehicleSpecDetailResponse](
        data=VehicleSpecDetailResponse.model_validate(vehicle)
    )


@router.get("/compare", response_model=APIEnvelope[List[VehicleSpecDetailResponse]])
async def compare_vehicles(ids: str, db: AsyncSession = Depends(get_db)):
    """
    Side-by-side spec comparison matrix JSON given comma-separated vehicle UUIDs.
    """
    try:
        uuid_list = [UUID(raw_id.strip()) for raw_id in ids.split(",") if raw_id.strip()]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format in 'ids' query parameter"
        )

    if not uuid_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parameter 'ids' cannot be empty"
        )

    query = (
        select(Vehicle)
        .where(Vehicle.id.in_(uuid_list))
        .options(
            selectinload(Vehicle.variants).selectinload(Variant.spec),
            selectinload(Vehicle.variants).selectinload(Variant.price_histories)
        )
    )
    result = await db.execute(query)
    vehicles = result.scalars().all()

    return APIEnvelope[List[VehicleSpecDetailResponse]](
        data=[VehicleSpecDetailResponse.model_validate(v) for v in vehicles]
    )
