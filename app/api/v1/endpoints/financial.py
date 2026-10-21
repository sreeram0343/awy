from typing import Dict, Any
from fastapi import APIRouter
from app.schemas.health import APIEnvelope
from app.schemas.financial import (
    OnRoadPriceRequest,
    InsuranceQuoteRequest,
    EMIRequest,
    EMISummary,
)
from app.services.financial.on_road_price_engine import on_road_price_engine
from app.services.financial.insurance_engine import insurance_engine
from app.services.financial.emi_engine import emi_engine

router = APIRouter()


@router.post("/on-road-price", response_model=APIEnvelope[Dict[str, Any]])
async def calculate_on_road_price(req: OnRoadPriceRequest):
    """
    Deterministic, state-wise, itemized on-road price calculation for 4W and 2W vehicles
    including RTO road taxes, IRDAI insurance mandates, and incidental charges.
    """
    result = on_road_price_engine.calculate_on_road_price(
        state_code=req.state_code,
        category=req.category,
        fuel_type=req.fuel_type,
        ex_showroom_price=req.ex_showroom_price,
        engine_capacity_cc=req.engine_capacity_cc,
        motor_power_kw=req.motor_power_kw,
        length_mm=req.length_mm,
        ground_clearance_mm=req.ground_clearance_mm,
        optional_accessories=req.optional_accessories,
        extended_warranty=req.extended_warranty,
        zero_dep_insurance=req.zero_dep_insurance,
        include_fastag=req.include_fastag,
    )
    return APIEnvelope[Dict[str, Any]](data=result)


@router.post("/insurance", response_model=APIEnvelope[Dict[str, Any]])
async def calculate_insurance(req: InsuranceQuoteRequest):
    """
    IRDAI-mandated insurance premium quotation engine (OD + Multi-year TP + Add-ons).
    """
    result = insurance_engine.compute_insurance(
        category=req.category,
        fuel_type=req.fuel_type,
        ex_showroom_price=req.ex_showroom_price,
        engine_capacity_cc=req.engine_capacity_cc,
        motor_power_kw=req.motor_power_kw,
        zero_dep=req.zero_dep,
        engine_protect=req.engine_protect,
        return_to_invoice=req.return_to_invoice,
        roadside_assist=req.roadside_assist,
        cpa_cover=req.cpa_cover,
    )
    return APIEnvelope[Dict[str, Any]](data=result)


@router.post("/emi", response_model=APIEnvelope[EMISummary])
async def calculate_emi(req: EMIRequest):
    """
    Standard reducing-balance vehicle loan EMI calculation with optional
    full month-by-month amortization schedule.
    """
    result = emi_engine.calculate_emi(
        total_price=req.total_price,
        down_payment=req.down_payment,
        down_payment_percent=req.down_payment_percent,
        tenure_months=req.tenure_months,
        annual_interest_rate=req.annual_interest_rate,
        include_schedule=req.include_schedule,
    )
    return APIEnvelope[EMISummary](data=EMISummary.model_validate(result))
