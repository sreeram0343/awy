from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class OnRoadPriceRequest(BaseModel):
    state_code: str = Field(min_length=2, max_length=5, description="Indian state code e.g. DL, MH, KA, TN, HR")
    category: str = Field(default="4W", description="'4W' or '2W'")
    fuel_type: str = Field(default="Petrol", description="Petrol, Diesel, EV, Hybrid, CNG")
    ex_showroom_price: float = Field(gt=0.0, description="Ex-showroom price in INR")
    engine_capacity_cc: Optional[float] = Field(default=None, description="Engine displacement in cc")
    motor_power_kw: Optional[float] = Field(default=None, description="Electric motor power in kW")
    length_mm: Optional[float] = Field(default=None, description="Overall length in mm")
    ground_clearance_mm: Optional[float] = Field(default=None, description="Ground clearance in mm")
    optional_accessories: float = Field(default=0.0, ge=0.0)
    extended_warranty: float = Field(default=0.0, ge=0.0)
    zero_dep_insurance: bool = Field(default=True)
    include_fastag: bool = Field(default=True)


class InsuranceQuoteRequest(BaseModel):
    category: str = Field(default="4W", description="'4W' or '2W'")
    fuel_type: str = Field(default="Petrol", description="Petrol, Diesel, EV, Hybrid")
    ex_showroom_price: float = Field(gt=0.0)
    engine_capacity_cc: Optional[float] = None
    motor_power_kw: Optional[float] = None
    zero_dep: bool = True
    engine_protect: bool = True
    return_to_invoice: bool = False
    roadside_assist: bool = True
    cpa_cover: bool = True


class EMIRequest(BaseModel):
    total_price: float = Field(gt=0.0, description="On-road or ex-showroom price to finance")
    down_payment: Optional[float] = Field(default=None, ge=0.0)
    down_payment_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    tenure_months: int = Field(default=60, ge=1, le=120)
    annual_interest_rate: float = Field(default=9.5, ge=0.0, le=50.0)
    include_schedule: bool = Field(default=False, description="Whether to generate full monthly amortization schedule")


class AmortizationScheduleItem(BaseModel):
    month: int
    opening_balance: float
    emi: float
    principal: float
    interest: float
    closing_balance: float


class EMISummary(BaseModel):
    principal_loan_amount: float
    down_payment: float
    down_payment_percent: float
    tenure_months: int
    annual_interest_rate: float
    monthly_emi: float
    total_interest_payable: float
    total_loan_repayment: float
    total_cost_with_downpayment: float
    amortization_schedule: Optional[List[AmortizationScheduleItem]] = None
