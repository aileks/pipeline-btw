import logging

from pipeline_btw.client.api import fetch_data

logger = logging.getLogger(__name__)


def extract_data(row_limit: int = 200):
    logger.info("Extracting data...")
    page = 1
    breweries = []
    params = {"per_page": 200, "page": page}
    while len(breweries) < row_limit:
        try:
            data = fetch_data(params)
            if not data:
                break
            breweries.extend(data)
            page += 1
            params["page"] = page
        except Exception as e:
            logger.exception("Failed while extracting")
            raise
    return breweries[:row_limit]
