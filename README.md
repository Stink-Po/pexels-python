# Pexels API Python Wrapper

[![PyPI version](https://img.shields.io/pypi/v/pexels-api-wrapper.svg)](https://pypi.org/project/pexels-api-wrapper/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pexels-api-wrapper.svg)](https://pypi.org/project/pexels-api-wrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An elegant, developer-friendly Python client library for interacting seamlessly with the **Pexels REST API**. 

Unlike naive wrappers, this package uses **Pydantic v2** to perform robust client-side validation on your parameters *before* hitting the network—saving you latency, bandwidth, and unhandled remote API errors.

---

## Features

- **Pydantic-powered Validation**: Caught invalid page bounds, dimensions, orientations, or hexadecimal colors locally before triggering HTTP requests.
- **Clean Interface**: Consistent method signatures exposing Photo, Video, and Curated/Featured Collection endpoints.
- **Fail-Safe Response Analysis**: Safe management of common HTTP statuses (`400`, `401`, `404`) with programmatic reporting.
- **Transparent Rate Limiting**: Automatic tracking and console reporting of monthly quotas (`X-Ratelimit-*`) parsed exclusively from successful hits.

---

## Installation

Install the package via `pip`:

```bash
pip install pexels-api-wrapper


Quick Start
1. Initializing the Client

Obtain an API key from the Pexels API Documentation portal.


from pexels import Client

# Note: Pexels uses raw keys. The client automatically manages 
# the header authorization for you without a "Bearer" prefix.
client = Client(api_key="YOUR_PEXELS_API_KEY")