import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.schemas.health import APIEnvelope
from app.schemas.lead import LeadCreate, LeadResponse
from app.core.logging import logger

router = APIRouter()

# In-memory CRM Lead & Appointment Store (synced with DB when available)
IN_MEMORY_LEADS: List[Dict[str, Any]] = [
    {
        "id": "a1b2c3d4-1111-4444-9999-000000000001",
        "variant_id": "11111111-1111-1111-1111-111111111111",
        "vehicle_name": "Tata Nexon Fearless Plus S",
        "user_name": "Rahul Nambiar",
        "user_email": "rahul.nambiar@example.com",
        "user_phone": "+91 98471 23456",
        "state_code": "KL",
        "dealership_id": "apex-kerala-01",
        "computed_on_road_price": 1587850.0,
        "status": "test_drive_booked",
        "consent_given": True,
        "consent_timestamp": "2026-10-20T10:15:00Z",
        "notes": "Interested in DCA automatic transmission. Prefers weekend morning slot.",
        "created_at": "2026-10-20T10:15:00Z",
        "updated_at": "2026-10-20T11:00:00Z"
    },
    {
        "id": "a1b2c3d4-2222-4444-9999-000000000002",
        "variant_id": "33333333-3333-3333-3333-333333333333",
        "vehicle_name": "Tata Nexon EV Empowered Plus",
        "user_name": "Ananya Menon",
        "user_email": "ananya.menon@example.com",
        "user_phone": "+91 94470 98765",
        "state_code": "KL",
        "dealership_id": "apex-kerala-01",
        "computed_on_road_price": 1785400.0,
        "status": "contacted",
        "consent_given": True,
        "consent_timestamp": "2026-10-20T14:30:00Z",
        "notes": "Inquired about home EV charger installation and Kerala EV subsidy eligibility.",
        "created_at": "2026-10-20T14:30:00Z",
        "updated_at": "2026-10-20T15:10:00Z"
    },
    {
        "id": "a1b2c3d4-3333-4444-9999-000000000003",
        "variant_id": "22222222-2222-2222-2222-222222222222",
        "vehicle_name": "Hyundai Creta SX (O) 1.5 Turbo",
        "user_name": "Suresh Kumar",
        "user_email": "suresh.k@example.com",
        "user_phone": "+91 97455 11223",
        "state_code": "KL",
        "dealership_id": "apex-kerala-01",
        "computed_on_road_price": 2335350.0,
        "status": "new",
        "consent_given": True,
        "consent_timestamp": "2026-10-21T08:45:00Z",
        "notes": "Calculated EMI for ₹15 Lakh loan over 5 years. Requested callback regarding trade-in.",
        "created_at": "2026-10-21T08:45:00Z",
        "updated_at": "2026-10-21T08:45:00Z"
    }
]

IN_MEMORY_APPOINTMENTS: List[Dict[str, Any]] = [
    {
        "id": "apt-001",
        "lead_id": "a1b2c3d4-1111-4444-9999-000000000001",
        "customer_name": "Rahul Nambiar",
        "phone": "+91 98471 23456",
        "vehicle": "Tata Nexon Fearless Plus S",
        "dealership": "Apex Motors Kochi Central",
        "date": "2026-10-22",
        "time_slot": "10:30 AM",
        "status": "confirmed",
        "sales_executive": "Jithin George",
        "created_at": "2026-10-20T11:00:00Z"
    },
    {
        "id": "apt-002",
        "lead_id": "a1b2c3d4-2222-4444-9999-000000000002",
        "customer_name": "Ananya Menon",
        "phone": "+91 94470 98765",
        "vehicle": "Tata Nexon EV Long Range",
        "dealership": "Apex Motors Kochi Central",
        "date": "2026-10-23",
        "time_slot": "03:00 PM",
        "status": "scheduled",
        "sales_executive": "Priya Nair",
        "created_at": "2026-10-20T15:10:00Z"
    }
]


class AppointmentCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: str = Field(min_length=10, max_length=15)
    customer_email: Optional[str] = None
    vehicle_model: str
    dealership_location: str = "Apex Motors Kochi Central"
    preferred_date: str
    preferred_time_slot: str
    notes: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


@router.post("/dispatch", response_model=APIEnvelope[LeadResponse])
async def dispatch_lead(req: LeadCreate):
    """
    Dispatch qualified lead to dealer CRM with explicit PII consent validation.
    """
    if not req.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead dispatch requires explicit user consent (consent_given must be true)"
        )

    now = datetime.now(timezone.utc)
    new_lead_id = uuid.uuid4()
    
    lead_entry = {
        "id": str(new_lead_id),
        "variant_id": str(req.variant_id),
        "vehicle_name": "Customer Selected Vehicle",
        "user_name": req.user_name,
        "user_email": req.user_email,
        "user_phone": req.user_phone,
        "state_code": req.state_code,
        "dealership_id": req.dealership_id,
        "computed_on_road_price": req.computed_on_road_price,
        "status": "sent",
        "consent_given": True,
        "consent_timestamp": now.isoformat(),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "notes": f"Online inquiry via AWY Voice Agent for State {req.state_code}"
    }

    IN_MEMORY_LEADS.insert(0, lead_entry)

    # Return valid LeadResponse
    resp = LeadResponse(
        id=new_lead_id,
        variant_id=req.variant_id,
        user_name=req.user_name,
        user_email=req.user_email,
        user_phone=req.user_phone,
        state_code=req.state_code,
        dealership_id=req.dealership_id,
        computed_on_road_price=req.computed_on_road_price,
        status="sent",
        consent_given=True,
        consent_timestamp=now,
        created_at=now,
        updated_at=now
    )
    return APIEnvelope[LeadResponse](data=resp)


@router.get("", response_model=APIEnvelope[List[Dict[str, Any]]])
async def list_leads(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None
):
    """
    List CRM leads for dealership operations dashboard.
    """
    results = IN_MEMORY_LEADS
    if status_filter:
        results = [l for l in results if l["status"] == status_filter]
    if search:
        s_lower = search.lower()
        results = [
            l for l in results
            if s_lower in l["user_name"].lower()
            or s_lower in l["user_phone"].lower()
            or s_lower in l.get("vehicle_name", "").lower()
        ]
    return APIEnvelope[List[Dict[str, Any]]](data=results)


@router.patch("/{lead_id}/status", response_model=APIEnvelope[Dict[str, Any]])
async def update_lead_status(lead_id: str, update: LeadStatusUpdate):
    """
    Update lead status and executive notes in dealership pipeline.
    """
    for l in IN_MEMORY_LEADS:
        if l["id"] == lead_id:
            l["status"] = update.status
            if update.notes:
                l["notes"] = update.notes
            l["updated_at"] = datetime.now(timezone.utc).isoformat()
            return APIEnvelope[Dict[str, Any]](data=l)

    raise HTTPException(status_code=404, detail="Lead not found")


@router.post("/appointments", response_model=APIEnvelope[Dict[str, Any]])
async def create_appointment(apt: AppointmentCreate):
    """
    Schedule a test drive appointment.
    """
    apt_id = f"apt-{str(uuid.uuid4())[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    appointment_entry = {
        "id": apt_id,
        "customer_name": apt.customer_name,
        "phone": apt.customer_phone,
        "email": apt.customer_email,
        "vehicle": apt.vehicle_model,
        "dealership": apt.dealership_location,
        "date": apt.preferred_date,
        "time_slot": apt.preferred_time_slot,
        "status": "confirmed",
        "notes": apt.notes or "Scheduled via AWY Digital Concierge",
        "sales_executive": "Jithin George",
        "created_at": now
    }

    IN_MEMORY_APPOINTMENTS.insert(0, appointment_entry)
    return APIEnvelope[Dict[str, Any]](data=appointment_entry)


@router.get("/appointments", response_model=APIEnvelope[List[Dict[str, Any]]])
async def list_appointments():
    """
    List all test drive appointments for dealership calendar.
    """
    return APIEnvelope[List[Dict[str, Any]]](data=IN_MEMORY_APPOINTMENTS)
