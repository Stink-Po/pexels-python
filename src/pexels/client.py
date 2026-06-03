"""
client.py
---------
Main entry point for interacting with the Pexels REST API.

The :class:`Client` class exposes one method per API endpoint.  All
parameters are validated via Pydantic models defined in
``validate_input.py`` before the HTTP request is dispatched, and every
response is inspected by :class:`~response_analyzer.ResponseAnalyzer`.

Pexels API base URLs
--------------------
Photos  : https://api.pexels.com/v1/
Videos  : https://api.pexels.com/v1/videos/

.. note::
    The legacy ``https://api.pexels.com/videos/`` base URL is deprecated
    by Pexels.  All video requests use the ``/v1/videos/`` path.

Attribution requirement (Pexels guidelines)
-------------------------------------------
Whenever you display content obtained via this API you **must** show a
prominent link back to Pexels, for example::

    Photos provided by <a href="https://www.pexels.com">Pexels</a>

and credit the photographer when possible::

    Photo by <photographer name> on
    <a href="<photo_url>">Pexels</a>
"""

from typing import Literal, Optional

import requests

# BUG FIX: the original file imported from 'validat_input' (typo).
# The corrected module name is 'validate_input'.
from .validate_input import (
    PexelsSearchParameters,
    PexelsVideoSearchParameters,   # NEW — see search_for_videos()
    PexelsVideosParameters,
    PexelsCollectionParameters,
)
from .response_analyzer import ResponseAnalyzer


class Client:
    """
    HTTP client for the Pexels API.

    Parameters
    ----------
    api_key : str
        Your Pexels API key.  Anyone with a Pexels account can request a key
        at https://www.pexels.com/api/.  The key is sent in the
        ``Authorization`` header on every request — **without** a ``Bearer``
        prefix (Pexels does not use the Bearer scheme).

    Attributes
    ----------
    api_key : str
        The stored API key.
    headers : dict
        Default HTTP headers sent with every request.
    video_end_point : str
        Base URL for all video endpoints.
    picture_end_point : str
        Base URL for all photo and collection endpoints.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key

        # Authorization: the Pexels API expects the raw API key in the
        # Authorization header — no "Bearer" prefix is used.
        # Reference: https://www.pexels.com/api/documentation/#authorization
        self._headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
        }

        # Base URLs as defined in the Pexels API documentation.
        # Note: the legacy https://api.pexels.com/videos/ is deprecated;
        # use /v1/videos/ for all video requests.
        self._video_end_point = "https://api.pexels.com/v1/videos/"
        self._picture_end_point = "https://api.pexels.com/v1/"

    # ------------------------------------------------------------------
    # Photo endpoints
    # ------------------------------------------------------------------

    def search_photos(
        self,
        query: str,
        orientation: Optional[Literal["landscape", "portrait", "square"]] = None,
        size: Optional[Literal["large", "medium", "small"]] = None,
        color: Optional[str] = None,
        locale: Optional[Literal[
            "en-US", "pt-BR", "es-ES", "ca-ES", "de-DE", "it-IT", "fr-FR",
            "sv-SE", "id-ID", "pl-PL", "ja-JP", "zh-TW", "zh-CN", "ko-KR",
            "th-TH", "nl-NL", "hu-HU", "vi-VN", "cs-CZ", "da-DK", "fi-FI",
            "uk-UA", "el-GR", "ro-RO", "nb-NO", "sk-SK", "tr-TR", "ru-RU",
        ]] = None,
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Search for photos on Pexels.

        API reference: GET https://api.pexels.com/v1/search

        Parameters
        ----------
        query : str
            Required. The search term (e.g. "ocean", "tigers", "pears").
        orientation : str, optional
            Desired photo orientation. Accepted: ``landscape``, ``portrait``,
            ``square``.
        size : str, optional
            Minimum photo size. Accepted: ``large`` (24 MP), ``medium``
            (12 MP), ``small`` (4 MP).
        color : str, optional
            Desired photo colour.  Accepted named colours: ``red``,
            ``orange``, ``yellow``, ``green``, ``turquoise``, ``blue``,
            ``violet``, ``pink``, ``brown``, ``black``, ``gray``, ``white``.
            Alternatively, any hexadecimal colour code (e.g. ``#ffffff``).
        locale : str, optional
            Locale used to localise the search results.
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with ``total_results``, ``page``,
            ``per_page``, ``photos`` (list), and optionally ``next_page`` /
            ``prev_page``.
            On failure: an error dict from :class:`ResponseAnalyzer`.
        """
        try:
            # Validate all parameters with the Pydantic model before sending.
            validated_params = PexelsSearchParameters(
                query=query,
                orientation=orientation,
                size=size,
                color=color,
                locale=locale,
                page=page,
                per_page=per_page,
            )
            # exclude_none=True ensures only explicitly supplied params are
            # included in the query string.
            params_dict = validated_params.model_dump(exclude_none=True)

            api_url = self.picture_end_point + "search"
            results = requests.get(api_url, headers=self.headers, params=params_dict)
            return ResponseAnalyzer(results).analyze()

        except Exception as e:
            # Pydantic raises ValidationError when a parameter value is
            # outside its allowed range or type.
            print(f"Validation Error: {e}")
            return {"status": "error", "message": str(e)}

    def curated_photos(
        self,
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Retrieve real-time photos curated by the Pexels team.

        API reference: GET https://api.pexels.com/v1/curated

        The curated list is updated with at least one new photo per hour,
        ensuring a continuously changing selection of trending content.

        Parameters
        ----------
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with ``page``, ``per_page``,
            ``total_results``, ``photos`` (list), and optionally
            ``next_page`` / ``prev_page``.
            On failure: an error dict from :class:`ResponseAnalyzer`.

        Notes
        -----
        BUG FIX: The original method was named ``curated_photo`` (singular)
        and used ``pydantic.Field(...)`` as default argument values in the
        function signature.  ``Field`` is a Pydantic model-field descriptor
        and has no effect when used as a plain function default — the
        validation constraints (``ge``, ``le``) were silently ignored.
        Plain integer defaults are used here instead.
        """
        # BUG FIX: removed incorrect use of pydantic.Field() as function
        # parameter defaults.  Plain integer defaults are sufficient; the
        # API will reject out-of-range values with a 400 response anyway.
        api_url = self.picture_end_point + "curated"
        results = requests.get(
            api_url,
            headers=self.headers,
            params={"per_page": per_page, "page": page},
        )
        response = ResponseAnalyzer(results).analyze()
        if response:
            return response
        print("No curated photos found.")
        return None

    def get_a_photo(self, photo_id: int):
        """
        Retrieve a single photo by its Pexels ID.

        API reference: GET https://api.pexels.com/v1/photos/:id

        Parameters
        ----------
        photo_id : int
            The unique integer ID of the photo to retrieve.

        Returns
        -------
        dict or None
            On success: a Photo resource dict containing ``id``, ``width``,
            ``height``, ``url``, ``photographer``, ``photographer_url``,
            ``photographer_id``, ``avg_color``, ``src``, ``liked``, and
            ``alt``.
            On failure: an error dict from :class:`ResponseAnalyzer`, or
            ``None`` if the photo was not found.

        Notes
        -----
        BUG FIX: The original code built the path as ``f"photos/:{photo_id}"``
        which produced a literal colon in the URL
        (e.g. ``/v1/photos/:12345``).  REST path parameters must be
        substituted directly — the colon is a documentation convention, not
        part of the actual URL.  Corrected to ``f"photos/{photo_id}"``.
        """
        # BUG FIX: was f"photos/:{photo_id}" — the colon is NOT part of the
        # actual URL path.  The correct endpoint is /v1/photos/{photo_id}.
        api_url = self.picture_end_point + f"photos/{photo_id}"
        results = requests.get(api_url, headers=self.headers)
        response = ResponseAnalyzer(results).analyze()
        if response:
            return response
        print(f"Photo with id={photo_id} not found.")
        return None

    # ------------------------------------------------------------------
    # Video endpoints
    # ------------------------------------------------------------------

    def search_for_videos(
        self,
        query: str,
        orientation: Optional[Literal["landscape", "portrait", "square"]] = None,
        size: Optional[Literal["large", "medium", "small"]] = None,
        locale: Optional[Literal[
            "en-US", "pt-BR", "es-ES", "ca-ES", "de-DE", "it-IT", "fr-FR",
            "sv-SE", "id-ID", "pl-PL", "ja-JP", "zh-TW", "zh-CN", "ko-KR",
            "th-TH", "nl-NL", "hu-HU", "vi-VN", "cs-CZ", "da-DK", "fi-FI",
            "uk-UA", "el-GR", "ro-RO", "nb-NO", "sk-SK", "tr-TR", "ru-RU",
        ]] = None,
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Search for videos on Pexels.

        API reference: GET https://api.pexels.com/v1/videos/search

        Parameters
        ----------
        query : str
            Required. The search term.
        orientation : str, optional
            Desired video orientation. Accepted: ``landscape``, ``portrait``,
            ``square``.
        size : str, optional
            Minimum video size. Accepted: ``large`` (4K), ``medium``
            (Full HD), ``small`` (HD).
        locale : str, optional
            Locale used to localise the search results.
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with ``total_results``, ``page``,
            ``per_page``, ``url``, ``videos`` (list), and optionally
            ``next_page`` / ``prev_page``.
            On failure: an error dict from :class:`ResponseAnalyzer`.

        Notes
        -----
        BUG FIX: The original implementation reused ``PexelsSearchParameters``
        (the photo-search validator) which includes the ``color`` field.  The
        Pexels Video Search endpoint does **not** support ``color`` — sending
        it was silently ignored by the API but was semantically wrong and
        could mislead callers.  This method now uses the dedicated
        ``PexelsVideoSearchParameters`` model which has no ``color`` field,
        and the ``color`` parameter has been removed from the signature.
        """
        try:
            # BUG FIX: use PexelsVideoSearchParameters (no color field)
            # instead of PexelsSearchParameters (which includes color).
            validated_params = PexelsVideoSearchParameters(
                query=query,
                orientation=orientation,
                size=size,
                locale=locale,
                page=page,
                per_page=per_page,
            )
            params_dict = validated_params.model_dump(exclude_none=True)

            api_url = self.video_end_point + "search"
            results = requests.get(api_url, headers=self.headers, params=params_dict)
            return ResponseAnalyzer(results).analyze()

        except Exception as e:
            print(f"Validation Error: {e}")
            return {"status": "error", "message": str(e)}

    def popular_videos(
        self,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Retrieve the current popular videos on Pexels.

        API reference: GET https://api.pexels.com/v1/videos/popular

        Parameters
        ----------
        min_width : int, optional
            Minimum video width in pixels.
        min_height : int, optional
            Minimum video height in pixels.
        min_duration : int, optional
            Minimum video duration in seconds.
        max_duration : int, optional
            Maximum video duration in seconds.
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with ``page``, ``per_page``,
            ``total_results``, ``url``, ``videos`` (list), and optionally
            ``next_page`` / ``prev_page``.
            On failure: an error dict from :class:`ResponseAnalyzer`.
        """
        try:
            validated_params = PexelsVideosParameters(
                min_width=min_width,
                min_height=min_height,
                min_duration=min_duration,
                max_duration=max_duration,
                page=page,
                per_page=per_page,
            )
            params_dict = validated_params.model_dump(exclude_none=True)

            api_url = self.video_end_point + "popular"
            results = requests.get(api_url, headers=self.headers, params=params_dict)
            return ResponseAnalyzer(results).analyze()

        except Exception as e:
            print(f"Validation Error: {e}")
            return {"status": "error", "message": str(e)}

    def get_a_video(self, video_id: int):
        """
        Retrieve a single video by its Pexels ID.

        API reference: GET https://api.pexels.com/v1/videos/:id

        Parameters
        ----------
        video_id : int
            The unique integer ID of the video to retrieve.

        Returns
        -------
        dict or None
            On success: a Video resource dict containing ``id``, ``width``,
            ``height``, ``url``, ``image``, ``duration``, ``user``,
            ``video_files``, and ``video_pictures``.
            On failure: an error dict from :class:`ResponseAnalyzer`, or
            ``None`` if the video was not found.

        Notes
        -----
        BUG FIX (1): The original code used a static path ``"videos/:id"``
        and passed the ID as a query parameter (``params={"id": video_id}``).
        The Pexels API expects the video ID embedded directly in the URL path,
        not in the query string.  The correct URL is
        ``/v1/videos/{video_id}``.

        BUG FIX (2): ``pydantic.Field(...)`` was used as the default value
        for ``video_id`` in the original function signature.  ``Field`` is a
        Pydantic model-field descriptor; using it as a plain function default
        does nothing — the type annotation ``int`` already enforces the type.
        """
        # BUG FIX: the ID must be part of the URL path, not a query param.
        # video_end_point = "https://api.pexels.com/v1/videos/"
        # so this produces "https://api.pexels.com/v1/videos/{video_id}"
        api_url = self.video_end_point + str(video_id)
        results = requests.get(api_url, headers=self.headers)
        response = ResponseAnalyzer(results).analyze()
        if response:
            return response
        print(f"Video with id={video_id} not found.")
        return None

    # ------------------------------------------------------------------
    # Collection endpoints
    # ------------------------------------------------------------------

    def featured_collections(
        self,
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Retrieve collections featured by the Pexels team.

        API reference: GET https://api.pexels.com/v1/collections/featured

        Parameters
        ----------
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with ``collections`` (list of Collection
            objects), ``page``, ``per_page``, ``total_results``, and
            optionally ``next_page`` / ``prev_page``.
            On failure: an error dict, or ``None``.

        Notes
        -----
        BUG FIX: Removed incorrect use of ``pydantic.Field()`` as function
        parameter defaults (same issue as :meth:`curated_photos`).
        """
        api_url = self.picture_end_point + "collections/featured"
        results = requests.get(
            api_url,
            headers=self.headers,
            params={"page": page, "per_page": per_page},
        )
        response = ResponseAnalyzer(results).analyze()
        if response:
            return response
        print("No featured collections found.")
        return None

    def my_collections(
        self,
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Retrieve the collections belonging to the authenticated user.

        API reference: GET https://api.pexels.com/v1/collections

        The authenticated user is identified by the ``Authorization`` header
        (i.e. the API key supplied to :class:`Client`).

        Parameters
        ----------
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with ``collections`` (list), ``page``,
            ``per_page``, ``total_results``, and optionally ``next_page``
            / ``prev_page``.
            On failure: an error dict, or ``None``.

        Notes
        -----
        BUG FIX: Removed incorrect use of ``pydantic.Field()`` as function
        parameter defaults.
        """
        api_url = self.picture_end_point + "collections"
        results = requests.get(
            api_url,
            headers=self.headers,
            params={"page": page, "per_page": per_page},
        )
        response = ResponseAnalyzer(results).analyze()
        if response:
            return response
        print("No collections found.")
        return None

    def collection_media(
        self,
        collection_id: int,
        collection_type: Optional[str] = None,
        sort: Optional[str] = "asc",
        page: int = 1,
        per_page: int = 15,
    ):
        """
        Retrieve the media (photos and/or videos) inside a specific collection.

        API reference: GET https://api.pexels.com/v1/collections/:id

        The collection must either be a featured collection or belong to the
        authenticated user identified by the API key.

        Parameters
        ----------
        collection_id : int
            Required. The unique integer ID of the collection.
        collection_type : str, optional
            Filter by media type. Accepted: ``"photos"``, ``"videos"``.
            If omitted or an unsupported value is given, all media types are
            returned.
        sort : str, optional
            Sort order of items. Accepted: ``"asc"``, ``"desc"``.
            Default ``"asc"``.  (Added to the API on 2023-11-22.)
        page : int, optional
            Page number to return. Must be ≥ 1. Default ``1``.
        per_page : int, optional
            Number of results per page. Range 1–80. Default ``15``.

        Returns
        -------
        dict or None
            On success: a dict with the collection ``id``, ``media``
            (list of Photo and/or Video objects), ``page``, ``per_page``,
            ``total_results``, and optionally ``next_page`` / ``prev_page``.
            On failure: an error dict from :class:`ResponseAnalyzer`.

        Notes
        -----
        BUG FIX (1): The original code built the path as
        ``f"collections/:{collection_id}/media"`` which produced a literal
        colon in the URL (e.g. ``/v1/collections/:42/media``).  Corrected to
        ``f"collections/{collection_id}/media"``.

        BUG FIX (2): Removed incorrect use of ``pydantic.Field()`` as
        function parameter defaults for ``collection_type`` and ``sort``.
        """
        # BUG FIX: was f"collections/:{collection_id}/media" — the colon is
        # NOT part of the actual URL; it is only a documentation convention
        # for denoting path parameters.
        path = f"collections/{collection_id}/media"
        try:
            validated_params = PexelsCollectionParameters(
                type=collection_type,
                sort=sort,
                page=page,
                per_page=per_page,
            )
            params_dict = validated_params.model_dump(exclude_none=True)

            api_url = self.picture_end_point + path
            results = requests.get(api_url, headers=self.headers, params=params_dict)
            return ResponseAnalyzer(results).analyze()

        except Exception as e:
            print(f"Validation Error: {e}")
            return {"status": "error", "message": str(e)}