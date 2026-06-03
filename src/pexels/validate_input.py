"""
validate_input.py
-----------------
Pydantic models used to validate all request parameters before they are sent
to the Pexels API.  Every field mirrors the exact parameter name, type, and
constraint documented at https://www.pexels.com/api/documentation/.

Note: the original file was named ``validate_input.py`` (typo). The correct
name is ``validate_input.py``; update the import in ``client.py`` accordingly.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Optional
import re


# ---------------------------------------------------------------------------
# Shared locale type
# ---------------------------------------------------------------------------
# All supported locale codes as listed in the Pexels API documentation.
# Used by both photo search and video search endpoints.
_LocaleType = Optional[Literal[
    "en-US", "pt-BR", "es-ES", "ca-ES", "de-DE", "it-IT", "fr-FR", "sv-SE",
    "id-ID", "pl-PL", "ja-JP", "zh-TW", "zh-CN", "ko-KR", "th-TH", "nl-NL",
    "hu-HU", "vi-VN", "cs-CZ", "da-DK", "fi-FI", "uk-UA", "el-GR", "ro-RO",
    "nb-NO", "sk-SK", "tr-TR", "ru-RU"
]]


class PexelsSearchParameters(BaseModel):
    """
    Validated parameters for the **Search Photos** endpoint.

    API reference: GET https://api.pexels.com/v1/search

    All optional fields default to ``None`` so that ``model_dump(exclude_none=True)``
    produces a clean query-string dict with only the parameters that were
    explicitly provided by the caller.

    Fields
    ------
    query : str
        Required. The search term (e.g. "ocean", "tigers", "pears").
    orientation : str, optional
        Desired photo orientation. Accepted values: ``landscape``, ``portrait``,
        ``square``.
    size : str, optional
        Minimum photo size. Accepted values: ``large`` (24 MP), ``medium``
        (12 MP), ``small`` (4 MP).
    color : str, optional
        Desired photo colour. Accepted values: named colours
        (``red``, ``orange``, ``yellow``, ``green``, ``turquoise``, ``blue``,
        ``violet``, ``pink``, ``brown``, ``black``, ``gray``, ``white``) or
        any hexadecimal colour code (e.g. ``#ffffff``).

        .. note::
            The ``color`` parameter is supported by **photo** search only.
            It is intentionally absent from :class:`PexelsVideoSearchParameters`.
    locale : str, optional
        The locale used to localise the search results.
    page : int, optional
        The page number to request. Must be ≥ 1. Defaults to ``1``.
    per_page : int, optional
        Number of results per page. Must be between 1 and 80 inclusive.
        Defaults to ``15``.
    """
    model_config = ConfigDict(extra='forbid')
    query: str = Field(
        ...,
        description="The search query. Ocean, Tigers, Pears, etc."
    )

    orientation: Optional[Literal["landscape", "portrait", "square"]] = Field(
        None,
        description=(
            "Desired photo orientation. "
            "Supported values: landscape, portrait, square."
        )
    )

    size: Optional[Literal["large", "medium", "small"]] = Field(
        None,
        description=(
            "Minimum photo size. "
            "Supported values: large (24MP), medium (12MP), small (4MP)."
        )
    )

    color: Optional[str] = Field(
        None,
        description=(
            "Desired photo colour. Supported values: red, orange, yellow, "
            "green, turquoise, blue, violet, pink, brown, black, gray, white, "
            "or any hexadecimal colour code (e.g. #ffffff). "
            "NOTE: supported by photo search only, not video search."
        )
    )

    locale: _LocaleType = Field(
        None,
        description="The locale of the search results."
    )

    page: Optional[int] = Field(
        1,
        description="The page number you are requesting. Default: 1.",
        ge=1
    )

    per_page: Optional[int] = Field(
        15,
        description=(
            "The number of results per page. Default: 15. Max: 80."
        ),
        ge=1,
        le=80
    )

    # ------------------------------------------------------------------
    # Custom validator for the ``color`` field
    # ------------------------------------------------------------------
    @field_validator("color")
    @classmethod
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Validates the ``color`` parameter against the list of accepted named
        colours and hex colour codes documented by the Pexels API.

        Accepted named colours
        ----------------------
        red, orange, yellow, green, turquoise, blue, violet,
        pink, brown, black, gray, white

        Accepted hex codes
        ------------------
        Any 3- or 6-digit hexadecimal colour code prefixed with ``#``
        (e.g. ``#fff``, ``#ffffff``).

        Raises
        ------
        ValueError
            If the supplied value does not match a named colour or a valid
            hex colour code.
        """
        if v is None:
            return v

        supported_named_colors = [
            "red", "orange", "yellow", "green", "turquoise", "blue",
            "violet", "pink", "brown", "black", "gray", "white",
        ]

        if v.lower() in supported_named_colors:
            return v.lower()
        elif re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", v):
            return v.lower()
        else:
            raise ValueError(
                "Invalid color. Must be one of the supported color names "
                "(red, orange, yellow, green, turquoise, blue, violet, pink, "
                "brown, black, gray, white) or a valid hexadecimal color code "
                "(e.g. #ffffff)."
            )


class PexelsVideoSearchParameters(BaseModel):
    """
    Validated parameters for the **Search Videos** endpoint.

    API reference: GET https://api.pexels.com/v1/videos/search

    .. important::
        This model is intentionally **separate** from
        :class:`PexelsSearchParameters` because the video search endpoint does
        **not** support the ``color`` filter. Using
        :class:`PexelsSearchParameters` for video search would allow a ``color``
        value to be silently sent in the request, which the API ignores but
        which misleads callers.

    Fields
    ------
    query : str
        Required. The search term.
    orientation : str, optional
        Desired video orientation. Accepted values: ``landscape``, ``portrait``,
        ``square``.
    size : str, optional
        Minimum video size. Accepted values: ``large`` (4K), ``medium``
        (Full HD), ``small`` (HD).
    locale : str, optional
        The locale used to localise the search results.
    page : int, optional
        Page number to request. Must be ≥ 1. Defaults to ``1``.
    per_page : int, optional
        Number of results per page. Must be between 1 and 80. Defaults to
        ``15``.
    """
    model_config = ConfigDict(extra='forbid')

    query: str = Field(
        ...,
        description="The search query. Ocean, Tigers, Pears, etc."
    )

    orientation: Optional[Literal["landscape", "portrait", "square"]] = Field(
        None,
        description=(
            "Desired video orientation. "
            "Supported values: landscape, portrait, square."
        )
    )

    size: Optional[Literal["large", "medium", "small"]] = Field(
        None,
        description=(
            "Minimum video size. "
            "Supported values: large (4K), medium (Full HD), small (HD)."
        )
    )

    # NOTE: ``color`` is deliberately omitted — the video search endpoint
    # does not support it.  See the Pexels API documentation for details.

    locale: _LocaleType = Field(
        None,
        description="The locale of the search results."
    )

    page: Optional[int] = Field(
        1,
        description="The page number you are requesting. Default: 1.",
        ge=1
    )

    per_page: Optional[int] = Field(
        15,
        description="The number of results per page. Default: 15. Max: 80.",
        ge=1,
        le=80
    )


class PexelsVideosParameters(BaseModel):
    """
    Validated parameters for the **Popular Videos** endpoint.

    API reference: GET https://api.pexels.com/v1/videos/popular

    Fields
    ------
    min_width : int, optional
        The minimum width in pixels of the returned videos.
    min_height : int, optional
        The minimum height in pixels of the returned videos.
    min_duration : int, optional
        The minimum duration in seconds of the returned videos.
    max_duration : int, optional
        The maximum duration in seconds of the returned videos.
    page : int, optional
        Page number to request. Must be ≥ 1. Defaults to ``1``.
    per_page : int, optional
        Number of results per page. Must be between 1 and 80. Defaults to
        ``15``.
    """
    model_config = ConfigDict(extra='forbid')

    min_width: Optional[int] = Field(
        None,
        description="The minimum width in pixels of the returned videos."
    )
    min_height: Optional[int] = Field(
        None,
        description="The minimum height in pixels of the returned videos."
    )
    min_duration: Optional[int] = Field(
        None,
        description="The minimum duration in seconds of the returned videos."
    )
    max_duration: Optional[int] = Field(
        None,
        description="The maximum duration in seconds of the returned videos."
    )
    page: Optional[int] = Field(
        1,
        description="The page number you are requesting. Default: 1.",
        ge=1
    )
    per_page: Optional[int] = Field(
        15,
        description="The number of results per page. Default: 15. Max: 80.",
        ge=1,
        le=80
    )


class PexelsCollectionParameters(BaseModel):
    """
    Validated parameters for the **Collection Media** endpoint.

    API reference: GET https://api.pexels.com/v1/collections/:id

    Fields
    ------
    type : str, optional
        The type of media to return. Accepted values: ``photos``, ``videos``.
        If omitted (or if an unsupported value is given), all media types are
        returned.
    sort : str, optional
        Sort order of items in the collection. Accepted values: ``asc``,
        ``desc``. Defaults to ``asc``.
        Added to the API on 2023-11-22 (see Pexels API changelog).
    page : int, optional
        Page number to request. Must be ≥ 1. Defaults to ``1``.
    per_page : int, optional
        Number of results per page. Must be between 1 and 80. Defaults to
        ``15``.
    """
    model_config = ConfigDict(extra='forbid')

    type: Optional[Literal["photos", "videos"]] = Field(
        None,
        description=(
            "The type of media to return. Supported values: 'photos', "
            "'videos'. If not specified, all media types are returned."
        )
    )
    sort: Optional[Literal["asc", "desc"]] = Field(
        "asc",
        description=(
            "Sort order of items. Supported values: 'asc', 'desc'. "
            "Default: 'asc'."
        )
    )
    page: Optional[int] = Field(
        1,
        description="The page number you are requesting. Default: 1.",
        ge=1
    )
    per_page: Optional[int] = Field(
        15,
        description="The number of results per page. Default: 15. Max: 80.",
        ge=1,
        le=80
    )