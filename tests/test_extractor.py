import json
from unittest.mock import MagicMock, patch
from extractor import extract_companies, Company

SAMPLE_COMPANIES = [
    {
        "name": "Acme Corp",
        "website": "https://acme.com",
        "email": "info@acme.com",
        "phone": "555-1234",
        "address": "123 Main St",
        "industry": "Tech",
        "description": "A tech company",
    }
]
SAMPLE_JSON = json.dumps(SAMPLE_COMPANIES)


def _make_mock_client(response_text: str):
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_extract_companies_returns_list_of_company():
    with patch("extractor.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value = _make_mock_client(SAMPLE_JSON)
        result = extract_companies("<html>Acme Corp</html>", api_key="test")
    assert len(result) == 1
    assert isinstance(result[0], Company)
    assert result[0].name == "Acme Corp"
    assert result[0].website == "https://acme.com"
    assert result[0].industry == "Tech"


def test_extract_companies_strips_markdown_code_fences():
    fenced = f"```json\n{SAMPLE_JSON}\n```"
    with patch("extractor.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value = _make_mock_client(fenced)
        result = extract_companies("<html></html>", api_key="test")
    assert len(result) == 1
    assert result[0].name == "Acme Corp"


def test_extract_companies_returns_empty_list_for_empty_array():
    with patch("extractor.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value = _make_mock_client("[]")
        result = extract_companies("<html></html>", api_key="test")
    assert result == []


def test_extract_companies_skips_entries_without_name():
    bad_json = json.dumps([{"name": "", "website": None, "email": None,
                            "phone": None, "address": None, "industry": None, "description": None}])
    with patch("extractor.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value = _make_mock_client(bad_json)
        result = extract_companies("<html></html>", api_key="test")
    assert result == []


def test_extract_companies_returns_empty_list_on_malformed_json():
    with patch("extractor.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value = _make_mock_client("not valid json at all")
        result = extract_companies("<html></html>", api_key="test")
    assert result == []


def test_extract_companies_null_fields_become_none():
    data = json.dumps([{"name": "Beta LLC", "website": None, "email": None,
                        "phone": None, "address": None, "industry": None, "description": None}])
    with patch("extractor.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value = _make_mock_client(data)
        result = extract_companies("<html></html>", api_key="test")
    assert result[0].website is None
