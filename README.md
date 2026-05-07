# Association Member Scraper

> **Note:** This tool is still in development. Expect rough edges and incomplete features.

Extracts company listings from association member directories. Exports CSV and Excel.

## Known Issues

- **Borlabs cookie consent dialog blocks "Load more" button** on some sites — fix pending.

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install chromium
```

## Configure

```bash
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
```

## Run

```bash
uvicorn main:app --reload --port 8000
# Open http://localhost:8000
```

## Test

```bash
pytest
```
