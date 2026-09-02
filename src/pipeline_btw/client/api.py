import logging
import time

import httpx

from pipeline_btw.client.errors import (
    RETRYABLE_HTTP_ERRORS,
    RETRYABLE_STATUS_CODES,
)

logger = logging.getLogger(__name__)

BREWERY_API_URL = "https://api.openbrewerydb.org/v1/breweries"


def fetch_data(params: dict, max_retries: int = 3):
    for attempt in range(max_retries + 1):
        try:
            response = httpx.get(BREWERY_API_URL, params=params)
            response.raise_for_status()
            return response.json()

        except RETRYABLE_HTTP_ERRORS:
            if attempt == max_retries:
                raise

            delay = 2**attempt
            logger.warning(
                "Request failed. Retrying attempt %d/%d",
                attempt + 1,
                max_retries,
            )
            time.sleep(delay)

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in RETRYABLE_STATUS_CODES:
                raise

            if attempt == max_retries:
                raise

            delay = 2**attempt
            logger.warning(
                "Request failed. Retrying attempt %d/%d in %d seconds",
                attempt + 1,
                max_retries,
                delay,
            )
            time.sleep(delay)
