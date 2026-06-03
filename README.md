# Pexels API Python Wrapper

[![PyPI version](https://img.shields.io/pypi/v/pexels-api.svg)](https://pypi.org/project/pexels-api/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pexels-api.svg)](https://pypi.org/project/pexels-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An elegant, developer-friendly Python client library for interacting seamlessly with the **Pexels REST API**.

Unlike naive wrappers, this package uses **Pydantic v2** to perform robust client-side validation on your parameters
*before* hitting the network—saving you latency, bandwidth, and unhandled remote API errors.

---

## Features

- **Pydantic-powered Validation**: Caught invalid page bounds, dimensions, orientations, or hexadecimal colors locally
  before triggering HTTP requests.
- **Clean Interface**: Consistent method signatures exposing Photo, Video, and Curated/Featured Collection endpoints.
- **Fail-Safe Response Analysis**: Safe management of common HTTP statuses (`400`, `401`, `404`) with programmatic
  reporting.
- **Transparent Rate Limiting**: Automatic tracking and console reporting of monthly quotas (`X-Ratelimit-*`) parsed
  exclusively from successful hits.

---

## Installation

Install the package via `pip`:

```bash
pip install pexels-api
```

## Quick Start

### 1. Initializing the Client

Obtain an API key from the Pexels API Documentation portal.
```python
from pexels import Client

# Note: Pexels uses raw keys. The client automatically manages 
# the header authorization for you without a "Bearer" prefix.
client = Client(api_key="YOUR_PEXELS_API_KEY")
```


## Photo Endpoints

### Search Photos

Search for photos using a required query and optional filters such as orientation, size, color, locale, page, and per_page.
```python
search_results = client.search_photos(
query="nature",
orientation="landscape",
size="large",
page=1,
per_page=10
)

for photo in search_results["photos"]:
print(photo["photographer"])
print(photo["src"]["original"])
```


### Curated Photos

Retrieve curated photos from the Pexels curated feed.
```python
curated = client.curated_photos(page=1, per_page=10)

for photo in curated["photos"]:
print(photo["photographer"])
```


### Get a Single Photo

Fetch a specific photo by its unique ID.
```python
photo = client.get_a_photo(photo_id=2014422)
print(photo)
```


## Video Endpoints

### Search Videos

Search for videos using keyword-based filtering and supported video parameters.
```python
videos = client.search_for_videos(
query="mountains",
orientation="landscape",
size="large",
page=1,
per_page=10
)

for video in videos["videos"]:
print(video["user"]["name"])
```

### Popular Videos

Retrieve popular videos with optional dimension and duration filters.
```python
popular = client.popular_videos(
min_width=1280,
min_height=720,
min_duration=5,
max_duration=30,
page=1,
per_page=10
)

for video in popular["videos"]:
print(video["id"])
```


Get a Single Video

Fetch a specific video by its unique ID.

```python
video = client.get_a_video(video_id=123456)
print(video)
```

Collection Endpoints
Featured Collections

Get a list of featured collections.

```python
featured = client.featured_collections(page=1, per_page=10)

for collection in featured["collections"]:
print(collection["title"])
```


My Collections

Retrieve the authenticated user’s collections.

```python
collections = client.my_collections(page=1, per_page=10)

for collection in collections["collections"]:
print(collection["title"])
```

Collection Media

Get the media items inside a specific collection.

```python
media = client.collection_media(
collection_id=12345,
collection_type="photos",
sort="asc",
page=1,
per_page=10
)

print(media)
```

Validation

This package uses Pydantic v2 to validate input parameters before sending any HTTP request.

Invalid values are rejected locally, which helps reduce unnecessary network traffic and prevents avoidable API errors.

Examples of validation-covered parameters include:

    page bounds
    image dimensions
    orientations
    colors in hexadecimal format
    video duration filters

```python
from pydantic import ValidationError

try:
client.search_photos(query="city", page=-1)
except ValidationError as e:
print(f"Validation error: {e}")
```

Error Handling

The client includes a ResponseAnalyzer layer that inspects API responses and handles common HTTP statuses such as:

    400 Bad Request
    401 Unauthorized
    404 Not Found

This gives you a cleaner and more predictable error-handling flow.

```python
from pexels.exceptions import PexelsAPIError

try:
client.search_photos(query="ocean")
except PexelsAPIError as e:
print(f"API Error ({e.status_code}): {e.message}")
```

Rate Limiting

The client also tracks rate-limit information returned by Pexels headers such as:

    X-Ratelimit-Limit
    X-Ratelimit-Remaining
    X-Ratelimit-Reset

This makes quota usage more transparent during development and production use.

                                                                    
```python
client.search_photos(query="architecture")
print(client.rate_limit_remaining)
```

Project Highlights

    Pydantic-powered validation before API calls
    Clean endpoint coverage for photos, videos, and collections
    Safe response analysis for common HTTP failures
    Transparent quota awareness via rate-limit headers
    Simple authorization flow using raw Pexels API keys


Contributing

Contributions are welcome and appreciated.

    Fork the Project
    Create your Feature Branch:


```bash
git checkout -b feature/AmazingFeature
```



Commit your Changes:
```bash
git commit -m "Add some AmazingFeature"
```

Push to the Branch:
```bash
git push origin feature/AmazingFeature
```

License

Distributed under the MIT License. See the LICENSE file for more information.