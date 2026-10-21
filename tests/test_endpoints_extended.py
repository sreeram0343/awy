import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_vehicles_catalog():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vehicles")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert len(data["data"]) >= 5
        # Verify first vehicle has verified specs
        v1 = data["data"][0]
        assert "make" in v1
        assert "model" in v1
        assert "ex_showroom_price" in v1
        assert v1["ncap_rating"] is not None


@pytest.mark.asyncio
async def test_filter_vehicles_by_fuel():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vehicles?fuel_type=Electric")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
        assert all(v["fuel_type"] == "Electric" for v in data)


@pytest.mark.asyncio
async def test_get_vehicle_by_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vehicles/11111111-1111-1111-1111-111111111111")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["model"] == "Nexon"


@pytest.mark.asyncio
async def test_agent_feedback_and_evaluation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Submit feedback
        fb_resp = await ac.post("/api/v1/voice/feedback", json={
            "query": "What is the price of Creta?",
            "response_text": "Ex-showroom starts at 19.99 Lakh",
            "rating": "positive",
            "category": "accuracy"
        })
        assert fb_resp.status_code == 200

        # Retrieve evaluation metrics
        eval_resp = await ac.get("/api/v1/voice/evaluation")
        assert eval_resp.status_code == 200
        metrics = eval_resp.json()["data"]
        assert "benchmark_score" in metrics
        assert metrics["spec_verification_rate"] == 100.0


@pytest.mark.asyncio
async def test_appointment_booking():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        apt_resp = await ac.post("/api/v1/leads/appointments", json={
            "customer_name": "Test Driver",
            "customer_phone": "+91 99999 88888",
            "customer_email": "driver@test.com",
            "vehicle_model": "Tata Nexon",
            "dealership_location": "Apex Motors Kochi Central",
            "preferred_date": "2026-10-25",
            "preferred_time_slot": "11:00 AM"
        })
        assert apt_resp.status_code == 200
        apt_data = apt_resp.json()["data"]
        assert apt_data["status"] == "confirmed"

        # List appointments
        list_resp = await ac.get("/api/v1/leads/appointments")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["data"]) >= 1
