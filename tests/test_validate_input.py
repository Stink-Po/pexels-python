import pytest
from pydantic import ValidationError
from src.validate_input import (
    PexelsSearchParameters,
    PexelsVideoSearchParameters,
    PexelsVideosParameters,
    PexelsCollectionParameters,
)

class TestPexelsSearchParameters:
    def test_valid_search_params_with_named_color_lowercase(self):
        params = PexelsSearchParameters(query="nature", color="red")
        assert params.color == "red"

    def test_valid_search_params_with_hex_color(self):
        params = PexelsSearchParameters(query="nature", color="#ABC123")
        assert params.color == "#abc123"

    def test_invalid_color_raises_validation_error(self):
        with pytest.raises(ValidationError):
            PexelsSearchParameters(query="nature", color="not-a-color")

    def test_page_bounds(self):
        with pytest.raises(ValidationError):
            PexelsSearchParameters(query="nature", page=0)

class TestPexelsVideoSearchParameters:
    def test_video_search_does_not_accept_color(self):
        with pytest.raises(ValidationError):
            PexelsVideoSearchParameters(query="ocean", color="red")
