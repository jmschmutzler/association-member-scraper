import pytest
from unittest.mock import AsyncMock, patch
from renderer import render_all_pages


@pytest.mark.asyncio
async def test_render_all_pages_returns_html_list():
    with patch("renderer._render_with_browser", AsyncMock(return_value=["<html>page1</html>"])):
        result = await render_all_pages("https://example.com/members")
    assert result == ["<html>page1</html>"]


@pytest.mark.asyncio
async def test_render_retries_once_on_failure():
    call_count = 0

    async def flaky(url, max_pages):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise TimeoutError("first attempt timed out")
        return ["<html>success</html>"]

    with patch("renderer._render_with_browser", side_effect=flaky):
        result = await render_all_pages("https://example.com/members")

    assert result == ["<html>success</html>"]
    assert call_count == 2


@pytest.mark.asyncio
async def test_render_raises_after_two_failures():
    with patch("renderer._render_with_browser", AsyncMock(side_effect=TimeoutError("always fails"))):
        with pytest.raises(TimeoutError):
            await render_all_pages("https://example.com/members")


@pytest.mark.asyncio
async def test_render_returns_multiple_pages():
    pages = ["<html>page1</html>", "<html>page2</html>", "<html>page3</html>"]
    with patch("renderer._render_with_browser", AsyncMock(return_value=pages)):
        result = await render_all_pages("https://example.com/members")
    assert len(result) == 3
