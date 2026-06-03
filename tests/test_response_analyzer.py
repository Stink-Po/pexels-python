import pytest
from src.response_analyzer import ResponseAnalyzer

class MockResponse:
    def __init__(self, status_code, json_data=None, json_raises=False):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = {}
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("Invalid JSON")
        return self._json_data

def test_analyze_200_success():
    response = MockResponse(200, json_data={"status": "ok"})
    analyzer = ResponseAnalyzer(response)
    result = analyzer.analyze()
    assert result == {"status": "ok"}

def test_analyze_429_rate_limit():
    response = MockResponse(429)
    analyzer = ResponseAnalyzer(response)
    result = analyzer.analyze()
    assert result == {"status": "error", "message": "Rate limit exceeded"}

def test_analyze_unexpected_status_with_json():
    response = MockResponse(500, json_data={"error": "oops"})
    analyzer = ResponseAnalyzer(response)
    result = analyzer.analyze()
    assert result["status"] == "error"
    assert "details" in result
