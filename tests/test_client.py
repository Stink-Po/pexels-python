import pytest
import src.client as client_module
from src.client import Client


class MockResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = {}

    def json(self):
        return self._json_data


def test_client_init():
    c = Client("test-key")
    assert c.api_key == "test-key"


def test_search_photos_success(monkeypatch):
    fake_response = MockResponse(200, json_data={"photos": []})

    # Patching requests and the internal analyzer
    monkeypatch.setattr(client_module.requests, "get", lambda url, headers=None, params=None: fake_response)
    monkeypatch.setattr(client_module.ResponseAnalyzer, "analyze", lambda self: {"status": "ok", "photos": []})

    c = Client("test-key")
    result = c.search_photos(query="nature")
    assert result == {"status": "ok", "photos": []}


def test_search_photos_validation_error(capsys):
    c = Client("test-key")
    # This should trigger Pydantic validation error inside search_photos
    result = c.search_photos(query="nature", color="invalid-color")

    assert result["status"] == "error"
    assert "Validation Error" in capsys.readouterr().out
