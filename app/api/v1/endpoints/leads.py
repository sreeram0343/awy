from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.lead import Lead
from app.schemas.health import APIEnvelope
from app.schemas.lead import LeadCreate, LeadResponse

router = APIRouter()


@router.post("/dispatch", response_model=APIEnvelope[LeadResponse])
async def dispatch_lead(req: LeadCreate, db: AsyncSession = Depends(get_db)):
    """
    Dispatch qualified lead to dealer CRM with explicit PII consent validation.
    """
    if not req.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead dispatch requires explicit user consent (consent_given must be true)"
        )

    lead = Lead(
        variant_id=req.variant_id,
        user_name=req.user_name,
        user_email=req.user_email,
        user_phone=req.user_phone,
        state_code=req.state_code,
        dealership_id=req.dealership_id,
        computed_on_road_price=req.computed_on_road_price,
        status="sent",
        consent_given=True,
        consent_timestamp=datetime.now(timezone.utc)
    )

    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return APIEnvelope[LeadResponse](data=LeadResponse.model_validate(lead))
