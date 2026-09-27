from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.schemas.health import APIEnvelope

router = APIRouter()


class OnRoadPriceRequest(BaseModel):
    variant_id: str
    state_code: str
    ex_showroom_price: float


class OnRoadPriceBreakdown(BaseModel):
    ex_showroom_price: float
    rto_tax: float
    gst_cess: float
    insurance_premium: float
    handling_logistics: float
    on_road_price: float
    state_code: str


class EMIRequest(BaseModel):
    on_road_price: float
    down_payment: float
    tenure_months: int
    interest_rate_annual: float


class EMISummary(BaseModel):
    loan_amount: float
    monthly_emi: float
    total_interest: float
    total_payment: float


@router.post("/on-road-price", response_model=APIEnvelope[OnRoadPriceBreakdown])
async def calculate_on_road_price(req: OnRoadPriceRequest):
    """
    Deterministic state-wise on-road price calculation.
    """
    # Placeholder stub for Phase 0 - full financial module in Phase 3
    breakdown = OnRoadPriceBreakdown(
        ex_showroom_price=req.ex_showroom_price,
        rto_tax=req.ex_showroom_price * 0.12,
        gst_cess=req.ex_showroom_price * 0.03,
        insurance_premium=35000.0,
        handling_logistics=1500.0,
        on_road_price=req.ex_showroom_price * 1.15 + 36500.0,
        state_code=req.state_code
    )
    return APIEnvelope[OnRoadPriceBreakdown](data=breakdown)


@router.post("/emi", response_model=APIEnvelope[EMISummary])
async def calculate_emi(req: EMIRequest):
    """
    Reducing balance EMI calculation engine.
    """
    loan_amount = req.on_road_price - req.down_payment
    monthly_rate = (req.interest_rate_annual / 12) / 100
    if monthly_rate > 0:
        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** req.tenure_months) / (((1 + monthly_rate) ** req.tenure_months) - 1)
    else:
        emi = loan_amount / req.tenure_months

    total_payment = emi * req.tenure_months
    total_interest = total_payment - loan_amount

    summary = EMISummary(
        loan_amount=round(loan_amount, 2),
        monthly_emi=round(emi, 2),
        total_interest=round(total_interest, 2),
        total_payment=round(total_payment, 2)
    )
    return APIEnvelope[EMISummary](data=summary)
