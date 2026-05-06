import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

# conftest.py already sets ANTHROPIC_API_KEY before this import
from main import app


@pytest.mark.asyncio
async def test_post_jobs_returns_job_id():
    with patch("main._run_job", new=AsyncMock()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/jobs", json={"urls": ["https://example.com"]})
    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_job_404_for_unknown():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/jobs/does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_returns_url_results():
    with patch("main._run_job", new=AsyncMock()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post("/jobs", json={"urls": ["https://example.com"]})
            job_id = create_resp.json()["id"]
            status_resp = await client.get(f"/jobs/{job_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert "url_results" in data
    assert "https://example.com" in data["url_results"]
    assert data["url_results"]["https://example.com"]["status"] == "pending"


@pytest.mark.asyncio
async def test_get_job_includes_total_companies():
    with patch("main._run_job", new=AsyncMock()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post("/jobs", json={"urls": ["https://example.com"]})
            job_id = create_resp.json()["id"]
            status_resp = await client.get(f"/jobs/{job_id}")
    assert "total_companies" in status_resp.json()


@pytest.mark.asyncio
async def test_download_csv_404_for_unknown_job():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/jobs/does-not-exist/csv")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_xlsx_404_for_unknown_job():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/jobs/does-not-exist/xlsx")
    assert response.status_code == 404
