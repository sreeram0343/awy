import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_api_on_road_price_4w_delhi():
    """Verify on-road price calculation for a 4W petrol car in Delhi via FastAPI."""
    payload = {
        "state_code": "DL",
        "category": "4W",
        "fuel_type": "Petrol",
        "ex_showroom_price": 1000000.0,
        "engine_capacity_cc": 1199,
        "length_mm": 3995,
        "ground_clearance_mm": 208,
        "optional_accessories": 15000.0,
        "extended_warranty": 20000.0,
        "zero_dep_insurance": True,
        "include_fastag": True,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/calculate/on-road-price", json=payload)
        assert resp.status_code == 200
        res = resp.json()
        assert res["status"] == "success"
        data = res["data"]
        
        # Verify structure and versioning
        assert data["rule_version"] == "v2026.10.1"
        assert data["state_code"] == "DL"
        assert data["ex_showroom_price"] == 1000000.0

        # Delhi 4W Petrol 6-10L slab is 7% + 1000 fixed MCD fee = 71000
        rto = data["rto_charges"]
        assert rto["rate_percent"] == 7.0
        assert rto["fixed_fee"] == 1000.0
        assert rto["rto_tax_amount"] == 71000.0
        
        # Insurance
        ins = data["insurance_charges"]
        assert ins["total_insurance_premium"] > 0
        
        # On-road total must match sum of components
        expected_total = (
            data["ex_showroom_price"]
            + rto["rto_tax_amount"]
            + ins["total_insurance_premium"]
            + data["incidental_charges"]["total"]
            + data["optional_charges"]["total"]
        )
        assert pytest.approx(data["total_on_road_price"], 0.01) == expected_total


@pytest.mark.asyncio
async def test_api_on_road_price_ev_exemption():
    """Verify that an EV in Maharashtra gets 0% RTO tax rate."""
    payload = {
        "state_code": "MH",
        "category": "4W",
        "fuel_type": "Electric",
        "ex_showroom_price": 1500000.0,
        "motor_power_kw": 105,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/calculate/on-road-price", json=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["rto_charges"]["rate_percent"] == 0.0
        assert data["rto_charges"]["fixed_fee"] == 1500.0
        assert data["rto_charges"]["rto_tax_amount"] == 1500.0


@pytest.mark.asyncio
async def test_api_on_road_price_2w():
    """Verify 2W on-road price in Karnataka."""
    payload = {
        "state_code": "KA",
        "category": "2W",
        "fuel_type": "Petrol",
        "ex_showroom_price": 120000.0,
        "engine_capacity_cc": 125,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/calculate/on-road-price", json=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]
        # KA >1L slab is 18% + 500 fee = 22100.0
        assert data["rto_charges"]["rate_percent"] == 18.0
        assert data["rto_charges"]["rto_tax_amount"] == 22100.0


@pytest.mark.asyncio
async def test_api_insurance_endpoint():
    """Verify the dedicated insurance quotation endpoint."""
    payload = {
        "category": "4W",
        "fuel_type": "Petrol",
        "ex_showroom_price": 1200000.0,
        "engine_capacity_cc": 1498,
        "zero_dep": True,
        "engine_protect": True,
        "return_to_invoice": False,
        "roadside_assist": True,
        "cpa_cover": True,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/calculate/insurance", json=payload)
        assert resp.status_code == 200
        res = resp.json()
        assert res["status"] == "success"
        data = res["data"]
        assert data["idv"] == 1140000.0  # 95% of 1.2M
        assert data["addons_breakdown"]["zero_depreciation"] > 0
        assert data["addons_breakdown"]["engine_protection"] > 0
        assert data["cpa_cover"] == 375.0
        assert data["gst_amount"] > 0
        assert data["total_insurance_premium"] > 0
        assert data["tp_tenure_years"] == 3


@pytest.mark.asyncio
async def test_api_emi_endpoint():
    """Verify EMI endpoint with and without full amortization schedule."""
    # Without schedule
    payload_no_sched = {
        "total_price": 1000000.0,
        "down_payment_percent": 20.0,
        "tenure_months": 60,
        "annual_interest_rate": 9.5,
        "include_schedule": False,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/calculate/emi", json=payload_no_sched)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["principal_loan_amount"] == 800000.0
        assert data["down_payment"] == 200000.0
        assert data["monthly_emi"] == 16801.49
        assert pytest.approx(data["total_loan_repayment"], 0.1) == 1008089.4
        assert pytest.approx(data["total_interest_payable"], 0.1) == 208089.4
        assert data["amortization_schedule"] is None

    # With schedule
    payload_with_sched = {
        "total_price": 1000000.0,
        "down_payment": 200000.0,
        "tenure_months": 36,
        "annual_interest_rate": 8.5,
        "include_schedule": True,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/calculate/emi", json=payload_with_sched)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["monthly_emi"] > 0
        schedule = data["amortization_schedule"]
        assert len(schedule) == 36
        assert schedule[0]["month"] == 1
        assert schedule[-1]["month"] == 36
        assert schedule[-1]["closing_balance"] == 0.0


@pytest.mark.asyncio
async def test_financial_calculation_latency():
    """Benchmark the on-road price engine to confirm sub-millisecond execution."""
    from app.services.financial.on_road_price_engine import on_road_price_engine

    start = time.perf_counter()
    iterations = 500
    for _ in range(iterations):
        on_road_price_engine.calculate_on_road_price(
            state_code="DL",
            category="4W",
            fuel_type="Petrol",
            ex_showroom_price=1200000.0,
            engine_capacity_cc=1199,
            length_mm=3995,
            ground_clearance_mm=208,
            optional_accessories=10000.0,
            extended_warranty=15000.0,
            zero_dep_insurance=True,
            include_fastag=True,
        )
    total_time = time.perf_counter() - start
    avg_ms = (total_time / iterations) * 1000.0
    print(f"\nAverage calculation latency: {avg_ms:.4f} ms per computation")
    # Must comfortably be sub-millisecond (< 1.0 ms)
    assert avg_ms < 0.5
