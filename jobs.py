import uuid
from dataclasses import dataclass, field
from typing import Literal

UrlStatus = Literal["pending", "running", "done", "failed"]

_jobs: dict[str, "Job"] = {}


@dataclass
class UrlResult:
    url: str
    status: UrlStatus = "pending"
    directory_url: str | None = None
    companies_found: int = 0
    error: str | None = None


@dataclass
class Job:
    id: str
    urls: list[str]
    url_results: dict[str, UrlResult] = field(default_factory=dict)

    def __post_init__(self):
        for url in self.urls:
            self.url_results[url] = UrlResult(url=url)


def create_job(urls: list[str]) -> Job:
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, urls=urls)
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)
