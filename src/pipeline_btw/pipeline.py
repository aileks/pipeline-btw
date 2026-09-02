import logging

from pipeline_btw.extract.breweries import extract_data
from pipeline_btw.load.postgres import load_data
from pipeline_btw.transform.breweries import transform_data

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    try:
        logger.info("Pipeline started")

        raw_data = extract_data(5000)
        cleaned_data = transform_data(raw_data)
        load_data(cleaned_data)

        logger.info("Pipeline completed successfully")

    except Exception:
        logger.exception("Pipeline failed")
        raise
