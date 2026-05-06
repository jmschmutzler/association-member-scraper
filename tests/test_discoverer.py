import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from discoverer import discover_directory_url, _looks_like_directory


def test_looks_like_directory_members():
    assert _looks_like_directory("https://example.com/members") is True


def test_looks_like_directory_directory():
    assert _looks_like_directory("https://example.com/directory") is True


def test_looks_like_directory_find_a_member():
    assert _looks_like_directory("https://example.com/find-a-member") is True


def test_looks_like_directory_homepage_is_false():
    assert _looks_like_directory("https://example.com") is False


def test_looks_like_directory_about_page_is_false():
    assert _looks_like_directory("https://example.com/about") is False


def test_looks_like_directory_our_members():
    assert _looks_like_directory("https://example.com/our-members") is True


def test_looks_like_directory_member_directory():
    assert _looks_like_directory("https://example.com/member-directory") is True


def test_looks_like_directory_membership_directory():
    assert _looks_like_directory("https://example.com/membership-directory") is True


def test_looks_like_directory_search_members():
    assert _looks_like_directory("https://example.com/search-members") is True


def test_looks_like_directory_member_search():
    assert _looks_like_directory("https://example.com/member-search") is True


def test_looks_like_directory_member_list():
    assert _looks_like_directory("https://example.com/member-list") is True


def test_looks_like_directory_no_false_positive_on_suffix():
    assert _looks_like_directory("https://example.com/our-members-only") is False
    assert _looks_like_directory("https://example.com/member-directory-old") is False


@pytest.mark.asyncio
async def test_discover_returns_original_if_already_directory():
    url = "https://example.com/members"
    result = await discover_directory_url(url)
    assert result == url


@pytest.mark.asyncio
async def test_discover_finds_member_link_in_homepage():
    html = '<html><body><a href="/members">Member Directory</a></body></html>'
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("discoverer.httpx.AsyncClient", return_value=mock_client):
        result = await discover_directory_url("https://example.com")

    assert result == "https://example.com/members"


@pytest.mark.asyncio
async def test_discover_falls_back_to_original_when_no_match():
    html = '<html><body><a href="/about">About Us</a></body></html>'
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("discoverer.httpx.AsyncClient", return_value=mock_client):
        result = await discover_directory_url("https://example.com")

    assert result == "https://example.com"


@pytest.mark.asyncio
async def test_discover_falls_back_on_request_error():
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(side_effect=Exception("connection refused"))

    with patch("discoverer.httpx.AsyncClient", return_value=mock_client):
        result = await discover_directory_url("https://example.com")

    assert result == "https://example.com"
