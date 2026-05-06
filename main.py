import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

from discoverer import discover_directory_url
from extractor import extract_companies
from jobs import Job, UrlResult, create_job, get_job
from renderer import render_all_pages
from writer import CompanyRow, company_to_row, deduplicate, write_csv, write_xlsx

load_dotenv()
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

UI_PATH = Path(__file__).parent / "static" / "index.html"

app = FastAPI()

# Per-job accumulated data: rows and errors
_job_data: dict[str, dict] = {}


class CreateJobRequest(BaseModel):
    urls: list[str]


@app.post("/jobs")
async def post_jobs(req: CreateJobRequest):
    job = create_job(req.urls)
    _job_data[job.id] = {"rows": [], "errors": []}
    asyncio.create_task(_run_job(job))
    return {"id": job.id}


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "url_results": {
            url: {
                "status": r.status,
                "companies_found": r.companies_found,
                "error": r.error,
                "directory_url": r.directory_url,
            }
            for url, r in job.url_results.items()
        },
        "total_companies": sum(r.companies_found for r in job.url_results.values()),
        "done": all(r.status in ("done", "failed") for r in job.url_results.values()),
    }


@app.get("/jobs/{job_id}/csv")
async def download_csv(job_id: str):
    job = get_job(job_id)
    if not job or job_id not in _job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    rows: list[CompanyRow] = deduplicate(_job_data[job_id]["rows"])
    content = write_csv(rows)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=companies_{job_id[:8]}.csv"},
    )


@app.get("/jobs/{job_id}/xlsx")
async def download_xlsx(job_id: str):
    job = get_job(job_id)
    if not job or job_id not in _job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    rows: list[CompanyRow] = deduplicate(_job_data[job_id]["rows"])
    errors: list[dict] = _job_data[job_id]["errors"]
    content = write_xlsx(rows, errors)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=companies_{job_id[:8]}.xlsx"},
    )


@app.get("/")
async def serve_ui():
    return HTMLResponse(UI_PATH.read_text(encoding="utf-8"))


async def _run_job(job: Job) -> None:
    for url in job.urls:
        result: UrlResult = job.url_results[url]
        result.status = "running"
        try:
            directory_url = await discover_directory_url(url)
            result.directory_url = directory_url

            pages_html = await render_all_pages(directory_url)

            for html in pages_html:
                companies = extract_companies(html, API_KEY)
                new_rows = [company_to_row(c, directory_url) for c in companies]
                _job_data[job.id]["rows"].extend(new_rows)
                result.companies_found += len(new_rows)

            result.status = "done"
        except Exception as exc:
            result.status = "failed"
            result.error = str(exc)
            _job_data[job.id]["errors"].append({"url": url, "reason": str(exc)})
