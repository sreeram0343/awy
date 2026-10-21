from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from app.core.logging import logger

router = APIRouter()

# Verified Automotive Seed Inventory (Apex Motors Catalog)
VERIFIED_INVENTORY = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "make": "Tata",
        "model": "Nexon",
        "variant": "Fearless Plus S",
        "category": "SUV",
        "body_type": "SUV",
        "fuel_type": "Petrol",
        "transmission": "7-Speed DCA",
        "ex_showroom_price": 1349000.0,
        "ncap_rating": 5,
        "mileage_kpl": 17.44,
        "ev_range_km": None,
        "seating_capacity": 5,
        "engine_capacity_cc": 1199,
        "airbags_count": 6,
        "ground_clearance_mm": 208,
        "boot_space_litres": 382,
        "warranty_years": 3,
        "key_features": ["360 Degree Camera", "Ventilated Front Seats", "Voice-assisted Sunroof", "Wireless Android Auto / Apple CarPlay", "Air Purifier with AQI Display"],
        "verified_source": "Apex Motors Verified Catalog 2026",
        "image_url": "/vehicles/tata_nexon.webp"
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "make": "Hyundai",
        "model": "Creta",
        "variant": "SX (O) 1.5 Turbo",
        "category": "SUV",
        "body_type": "SUV",
        "fuel_type": "Petrol",
        "transmission": "7-Speed DCT",
        "ex_showroom_price": 1999000.0,
        "ncap_rating": 4,
        "mileage_kpl": 18.4,
        "ev_range_km": None,
        "seating_capacity": 5,
        "engine_capacity_cc": 1482,
        "airbags_count": 6,
        "ground_clearance_mm": 190,
        "boot_space_litres": 433,
        "warranty_years": 3,
        "key_features": ["Level 2 ADAS (19 Features)", "Dual-zone Climate Control", "Bose Premium 8-Speaker Audio", "Panoramic Sunroof", "Blind View Monitor"],
        "verified_source": "Apex Motors Verified Catalog 2026",
        "image_url": "/vehicles/hyundai_creta.webp"
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "make": "Tata",
        "model": "Nexon EV",
        "variant": "Empowered Plus Long Range",
        "category": "SUV",
        "body_type": "Electric SUV",
        "fuel_type": "Electric",
        "transmission": "Single-Speed Automatic",
        "ex_showroom_price": 1699000.0,
        "ncap_rating": 5,
        "mileage_kpl": None,
        "ev_range_km": 465.0,
        "seating_capacity": 5,
        "battery_capacity_kwh": 40.5,
        "airbags_count": 6,
        "ground_clearance_mm": 190,
        "boot_space_litres": 350,
        "warranty_years": 8,
        "key_features": ["V2V & V2L Charging", "12.3-inch Cinematic Touchscreen", "Paddle Shifters for Multi-mode Regen", "Arcade.ev App Suite", "Fast DC Charging (10-80% in 56 min)"],
        "verified_source": "Apex Motors Verified Catalog 2026",
        "image_url": "/vehicles/tata_nexon_ev.webp"
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "make": "Mahindra",
        "model": "XUV700",
        "variant": "AX7 L AWD",
        "category": "SUV",
        "body_type": "7-Seater SUV",
        "fuel_type": "Diesel",
        "transmission": "6-Speed Automatic",
        "ex_showroom_price": 2399000.0,
        "ncap_rating": 5,
        "mileage_kpl": 16.57,
        "ev_range_km": None,
        "seating_capacity": 7,
        "engine_capacity_cc": 2198,
        "airbags_count": 7,
        "ground_clearance_mm": 200,
        "boot_space_litres": 450,
        "warranty_years": 3,
        "key_features": ["Sony 3D 12-Speaker Sound", "Smart Door Handles", "Personalized Safety Alerts", "Custom Drive Modes (Zip, Zap, Zoom)", "Dual HD Super-screen Displays"],
        "verified_source": "Apex Motors Verified Catalog 2026",
        "image_url": "/vehicles/mahindra_xuv700.webp"
    },
    {
        "id": "55555555-5555-5555-5555-555555555555",
        "make": "Maruti Suzuki",
        "model": "Grand Vitara",
        "variant": "Alpha Plus Strong Hybrid",
        "category": "SUV",
        "body_type": "Hybrid SUV",
        "fuel_type": "Hybrid",
        "transmission": "e-CVT",
        "ex_showroom_price": 1993000.0,
        "ncap_rating": 4,
        "mileage_kpl": 27.97,
        "ev_range_km": None,
        "seating_capacity": 5,
        "engine_capacity_cc": 1490,
        "airbags_count": 6,
        "ground_clearance_mm": 210,
        "boot_space_litres": 373,
        "warranty_years": 3,
        "key_features": ["Strong Hybrid Self-charging", "Head-Up Display (HUD)", "Panoramic Sunroof", "EV Only Drive Mode", "Wireless Phone Charging"],
        "verified_source": "Apex Motors Verified Catalog 2026",
        "image_url": "/vehicles/grand_vitara.webp"
    },
    {
        "id": "66666666-6666-6666-6666-666666666666",
        "make": "Tata",
        "model": "Punch",
        "variant": "Creative Flagship DT",
        "category": "Compact SUV",
        "body_type": "Compact SUV",
        "fuel_type": "Petrol",
        "transmission": "5-Speed AMT",
        "ex_showroom_price": 980000.0,
        "ncap_rating": 5,
        "mileage_kpl": 18.82,
        "ev_range_km": None,
        "seating_capacity": 5,
        "engine_capacity_cc": 1199,
        "airbags_count": 2,
        "ground_clearance_mm": 187,
        "boot_space_litres": 366,
        "warranty_years": 3,
        "key_features": ["90-degree Door Opening", "5-Star Global NCAP", "Traction Pro Mode", "Harman Infotainment", "Dual Tone Roof"],
        "verified_source": "Apex Motors Verified Catalog 2026",
        "image_url": "/vehicles/tata_punch.webp"
    }
]


@router.get("", response_model=APIEnvelope[List[Dict[str, Any]]])
async def list_vehicles(
    query: Optional[str] = Query(None, description="Search keyword for make, model, or variant"),
    make: Optional[str] = Query(None, description="Filter by automotive brand"),
    category: Optional[str] = Query(None, description="Filter by body type / category"),
    fuel_type: Optional[str] = Query(None, description="Petrol, Diesel, Electric, Hybrid, CNG"),
    transmission: Optional[str] = Query(None, description="Manual, Automatic, etc."),
    min_price: Optional[float] = Query(None, description="Minimum ex-showroom price in INR"),
    max_price: Optional[float] = Query(None, description="Maximum ex-showroom price in INR"),
    min_ncap: Optional[int] = Query(None, description="Minimum NCAP safety rating (1-5)"),
):
    """
    Search and filter verified automotive inventory with deterministic filters.
    """
    results = []
    q_lower = query.lower().strip() if query else None

    for v in VERIFIED_INVENTORY:
        if q_lower:
            text_corpus = f"{v['make']} {v['model']} {v['variant']} {v['category']} {v['fuel_type']}".lower()
            if q_lower not in text_corpus:
                continue

        if make and v["make"].lower() != make.lower():
            continue

        if category and category.lower() not in v["category"].lower() and category.lower() not in v["body_type"].lower():
            continue

        if fuel_type and v["fuel_type"].lower() != fuel_type.lower():
            continue

        if transmission and transmission.lower() not in v["transmission"].lower():
            continue

        if min_price is not None and v["ex_showroom_price"] < min_price:
            continue

        if max_price is not None and v["ex_showroom_price"] > max_price:
            continue

        if min_ncap is not None and (v.get("ncap_rating") or 0) < min_ncap:
            continue

        results.append(v)

    return APIEnvelope[List[Dict[str, Any]]](data=results)


@router.get("/{id}", response_model=APIEnvelope[Dict[str, Any]])
async def get_vehicle_by_id(id: str):
    """
    Get detailed specifications for a specific vehicle by ID.
    """
    for v in VERIFIED_INVENTORY:
        if v["id"] == id:
            return APIEnvelope[Dict[str, Any]](data=v)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Vehicle with ID '{id}' not found in verified inventory"
    )


@router.get("/compare/matrix", response_model=APIEnvelope[List[Dict[str, Any]]])
async def compare_vehicles_matrix(ids: str):
    """
    Side-by-side spec comparison matrix given comma-separated vehicle IDs.
    """
    id_list = [raw_id.strip() for raw_id in ids.split(",") if raw_id.strip()]
    if not id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parameter 'ids' cannot be empty"
        )

    matched = [v for v in VERIFIED_INVENTORY if v["id"] in id_list]
    return APIEnvelope[List[Dict[str, Any]]](data=matched)
