import pytest


@pytest.mark.asyncio
async def test_health_check_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "success"
    assert "data" in json_data
    assert "database" in json_data["data"]
    assert "qdrant" in json_data["data"]
    assert json_data["data"]["database"]["status"] == "healthy"
    assert "generated_at" in json_data["meta"]
