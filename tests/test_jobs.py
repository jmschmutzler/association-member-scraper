import pytest
from jobs import create_job, get_job


def test_create_job_assigns_id():
    job = create_job(["https://example.com"])
    assert job.id


def test_create_job_initializes_url_results():
    job = create_job(["https://a.com", "https://b.com"])
    assert "https://a.com" in job.url_results
    assert "https://b.com" in job.url_results


def test_create_job_url_status_starts_pending():
    job = create_job(["https://example.com"])
    assert job.url_results["https://example.com"].status == "pending"


def test_create_job_url_result_defaults():
    job = create_job(["https://example.com"])
    result = job.url_results["https://example.com"]
    assert result.companies_found == 0
    assert result.error is None
    assert result.directory_url is None


def test_get_job_returns_none_for_unknown():
    assert get_job("nonexistent-id") is None


def test_get_job_returns_job_by_id():
    job = create_job(["https://example.com"])
    retrieved = get_job(job.id)
    assert retrieved is job


def test_create_job_raises_on_empty_urls():
    with pytest.raises(ValueError, match="urls must not be empty"):
        create_job([])
