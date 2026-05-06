import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone

from openpyxl import Workbook

from extractor import Company

FIELDS = [
    "name", "website", "email", "phone",
    "address", "industry", "description",
    "source_url", "scraped_at",
]
ERROR_FIELDS = ["url", "reason"]


@dataclass
class CompanyRow:
    name: str
    website: str | None
    email: str | None
    phone: str | None
    address: str | None
    industry: str | None
    description: str | None
    source_url: str
    scraped_at: str


def company_to_row(company: Company, source_url: str) -> CompanyRow:
    return CompanyRow(
        name=company.name,
        website=company.website,
        email=company.email,
        phone=company.phone,
        address=company.address,
        industry=company.industry,
        description=company.description,
        source_url=source_url,
        scraped_at=datetime.now(timezone.utc).isoformat(),
    )


def deduplicate(rows: list[CompanyRow]) -> list[CompanyRow]:
    seen: dict[tuple[str, str], CompanyRow] = {}
    for row in rows:
        key = (row.name.lower().strip(), (row.website or "").lower().strip())
        seen[key] = row  # last-write wins
    return list(seen.values())


def write_csv(rows: list[CompanyRow]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    for row in rows:
        writer.writerow({f: getattr(row, f) for f in FIELDS})
    return output.getvalue()


def write_xlsx(rows: list[CompanyRow], errors: list[dict]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Companies"
    ws.append(FIELDS)
    for row in rows:
        ws.append([getattr(row, f) for f in FIELDS])

    err_ws = wb.create_sheet("_errors")
    err_ws.append(ERROR_FIELDS)
    for error in errors:
        err_ws.append([error.get("url"), error.get("reason")])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
