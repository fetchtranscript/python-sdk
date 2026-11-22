"""Shared test fixtures."""

import pytest
import respx
import httpx


@pytest.fixture
def base_url():
    return "https://api.fetchtranscript.com"


@pytest.fixture
def api_key():
    return "yt_test_key_for_unit_tests"


@pytest.fixture
def mock_api(base_url):
    with respx.mock(base_url=base_url) as mock:
        yield mock
