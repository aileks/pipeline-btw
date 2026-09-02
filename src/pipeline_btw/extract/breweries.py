import logging

from pipeline_btw.client.api import fetch_data

logger = logging.getLogger(__name__)


def extract_data(row_limit: int = 200, rows_per_page: int = 50):
    logger.info("Extracting data...")
    page = 1
    breweries = []
    params = {"per_page": rows_per_page, "page": page}
    while len(breweries) < row_limit:
        logger.info("Fetching page %d", page)
        data = fetch_data(params)
        if not data:
            break
        breweries.extend(data)
        page += 1
        params["page"] = page

    breweries = breweries[:row_limit]
    logger.info("Fetched %d total rows", len(breweries))
    return breweries
