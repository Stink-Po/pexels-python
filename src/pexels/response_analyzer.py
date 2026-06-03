"""
response_analyzer.py
--------------------
Centralised HTTP-response handler for all Pexels API calls.

The :class:`ResponseAnalyzer` inspects the status code returned by the
Pexels API and either returns the parsed JSON payload (on success) or an
error dictionary (on failure).

Rate-limit note from the Pexels API documentation
--------------------------------------------------
"These response headers are only returned on successful (2xx) responses.
 They are not included with other responses, including 429 Too Many Requests."

Therefore :meth:`analyze_rate_limit_headers` is called **only** when the
response status is 200.  It must NOT be called for error responses (including
429) because the headers will simply not be present.
"""

from requests import exceptions


class ResponseAnalyzer:
    """
    Analyzes the HTTP response received from the Pexels API.

    Parameters
    ----------
    response : requests.Response
        The response object returned by the ``requests`` library after making
        a Pexels API call.
    """

    def __init__(self, response):
        """
        Stores the response object for subsequent analysis.

        Parameters
        ----------
        response : requests.Response
            A ``requests.Response`` object (or any compatible object that
            exposes ``.status_code``, ``.headers``, and ``.json()``).
        """
        self.response = response

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyze(self):
        """
        Inspects the HTTP status code and returns an appropriate result.

        Successful response (200 OK)
        ----------------------------
        - Logs the three rate-limit headers (``X-Ratelimit-Limit``,
          ``X-Ratelimit-Remaining``, ``X-Ratelimit-Reset``) that the Pexels
          API attaches to every successful response.
        - Returns the parsed JSON body as a Python dict.

        Error responses
        ---------------
        +---------+----------------------------------------------------------+
        | Code    | Meaning                                                  |
        +=========+==========================================================+
        | 400     | Bad Request — invalid parameters were sent.              |
        +---------+----------------------------------------------------------+
        | 401     | Unauthorised — the API key is missing or invalid.        |
        +---------+----------------------------------------------------------+
        | 404     | Not Found — the requested resource does not exist.       |
        +---------+----------------------------------------------------------+
        | 429     | Too Many Requests — the rate limit has been exceeded.    |
        |         | **No** rate-limit headers are returned by the API for    |
        |         | this status code.                                        |
        +---------+----------------------------------------------------------+
        | other   | Unexpected server-side or network error.                 |
        +---------+----------------------------------------------------------+

        Returns
        -------
        dict or None
            - Parsed JSON dict on success.
            - ``{"status": "error", "message": "..."}`` dict on failure.
            - ``{"status": "error", "message": "...", "details": ...}`` dict
              when the error body itself contains parseable JSON.
        """
        status = self.response.status_code

        if status == 200:
            # ----------------------------------------------------------------
            # Success path — rate-limit headers ARE present on 2xx responses.
            # Log them so callers can track their monthly quota.
            # ----------------------------------------------------------------
            self._log_rate_limit_headers()
            try:
                return self.response.json()
            except exceptions.JSONDecodeError:
                print(
                    "Error: Response was successful (200) but the body could "
                    "not be decoded as JSON."
                )
                return {"status": "error", "message": "Invalid JSON response"}

        elif status == 429:
            # ----------------------------------------------------------------
            # Rate limit exceeded.
            # IMPORTANT: The Pexels API documentation states explicitly that
            # rate-limit headers are NOT returned with 429 responses.  Do not
            # attempt to read or log them here.
            # ----------------------------------------------------------------
            print(
                "Error: Rate limit exceeded (HTTP 429). You have used all of "
                "your allocated requests for the current period. Check "
                "X-Ratelimit-Reset from your last successful response to know "
                "when the quota resets."
            )
            return {"status": "error", "message": "Rate limit exceeded"}

        elif status == 401:
            # ----------------------------------------------------------------
            # Authentication failed.
            # The Authorization header was missing, malformed, or the API key
            # is invalid / revoked.
            # ----------------------------------------------------------------
            print(
                "Error: Authentication failed (HTTP 401). Please verify that "
                "your Pexels API key is correct and that the Authorization "
                "header is set properly."
            )
            return {"status": "error", "message": "Authentication failed"}

        elif status == 404:
            # ----------------------------------------------------------------
            # Resource not found.
            # The photo, video, or collection ID supplied does not exist.
            # ----------------------------------------------------------------
            print(
                "Error: Resource not found (HTTP 404). The photo, video, or "
                "collection ID you requested does not exist."
            )
            return {"status": "error", "message": "Resource not found"}

        else:
            # ----------------------------------------------------------------
            # Unexpected status code.
            # Try to include any JSON details returned by the server.
            # Rate-limit headers are NOT logged here because the API only
            # guarantees them on 2xx responses.
            # ----------------------------------------------------------------
            error_message = (
                f"Request failed with unexpected status code {status}."
            )
            print(f"Error: {error_message}")
            try:
                error_details = self.response.json()
                return {
                    "status": "error",
                    "message": error_message,
                    "details": error_details,
                }
            except exceptions.JSONDecodeError:
                return {"status": "error", "message": error_message}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _log_rate_limit_headers(self):
        """
        Reads and prints the three rate-limit response headers that the Pexels
        API attaches to every **successful (2xx)** response.

        Response headers (from Pexels API documentation)
        -------------------------------------------------
        ``X-Ratelimit-Limit``
            Your total request limit for the current monthly period.
            Default limits: 200 requests/hour, 20 000 requests/month.
        ``X-Ratelimit-Remaining``
            How many requests remain within the current monthly period.
        ``X-Ratelimit-Reset``
            UNIX timestamp indicating when the current monthly period resets.

        .. warning::
            These headers are only present on successful (2xx) responses.
            This method must not be called for error responses.
        """
        limit = self.response.headers.get("X-Ratelimit-Limit")
        remaining = self.response.headers.get("X-Ratelimit-Remaining")
        reset_time = self.response.headers.get("X-Ratelimit-Reset")

        if limit:
            print(f"Rate Limit: Monthly limit = {limit}")
        if remaining:
            print(f"Rate Limit: Requests remaining this month = {remaining}")
        if reset_time:
            # reset_time is a UNIX timestamp (integer seconds since epoch).
            # Consider converting it to a human-readable datetime if needed.
            print(f"Rate Limit: Monthly rollover UNIX timestamp = {reset_time}")

    # ------------------------------------------------------------------
    # Kept for backwards compatibility — renamed to follow PEP 8 private
    # convention.  The old public name ``analyze_rate_limit_headers`` is
    # preserved as an alias so existing code does not break.
    # ------------------------------------------------------------------

    def analyze_rate_limit_headers(self):
        """
        Public alias for :meth:`_log_rate_limit_headers`.

        Kept for backwards compatibility. Prefer calling
        ``_log_rate_limit_headers`` internally.
        """
        self._log_rate_limit_headers()