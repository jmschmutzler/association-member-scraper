import json
import anthropic
from dataclasses import dataclass

EXTRACTION_PROMPT = """You are a data extraction assistant. Extract all member companies from the HTML below.

Return ONLY a valid JSON array of objects with these exact fields:
- name (string, required)
- website (string or null)
- email (string or null)
- phone (string or null)
- address (string or null)
- industry (string or null)
- description (string or null)

Rules:
- Only extract data explicitly present in the HTML. Do not infer or hallucinate.
- If a field is not present for a company, use null.
- If there are no companies, return an empty array: []
- Return ONLY the JSON array, no explanation or surrounding text.

HTML:
{html}"""


@dataclass
class Company:
    name: str
    website: str | None
    email: str | None
    phone: str | None
    address: str | None
    industry: str | None
    description: str | None


def extract_companies(html: str, api_key: str) -> list[Company]:
    """Send rendered HTML to Claude and return a list of Company dataclasses.

    Returns an empty list on malformed JSON or empty response.
    """
    client = anthropic.Anthropic(api_key=api_key)
    truncated = html[:100_000]

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=8096,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.replace("{html}", truncated)}],
    )

    raw = message.content[0].text.strip()

    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:])
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [
        Company(
            name=item.get("name", ""),
            website=item.get("website"),
            email=item.get("email"),
            phone=item.get("phone"),
            address=item.get("address"),
            industry=item.get("industry"),
            description=item.get("description"),
        )
        for item in data
        if item.get("name")
    ]
