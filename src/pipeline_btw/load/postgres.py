import logging

from pydantic import BaseModel, Field, ValidationError, field_validator

from pipeline_btw.db.connection import get_connection

logger = logging.getLogger(__name__)


class Brewery(BaseModel):
    id: str
    brewery_type: str
    name: str
    address_1: str | None = None
    address_2: str | None = None
    address_3: str | None = None
    city: str
    state_province: str
    postal_code: str
    country: str
    longitude: float | None = None
    latitude: float | None = None
    phone: str | None = None
    website_url: str | None = None

    @field_validator("longitude", "latitude", mode="before")
    @classmethod
    def clean_coordinates(cls, val):
        if val == "" or val == "null" or val is None:
            return None
        return val


def load_data(data: list[dict]):
    logger.info("Validating %d rows", len(data))

    validated_data = []
    for row in data:
        try:
            brewery = Brewery(**row)
            validated_data.append(brewery.model_dump())
        except ValidationError as e:
            logger.error(
                "Skipping row due to validation error on brewery ID %s: %s", row.get("id"), e
            )
            continue

    logger.info("Loading %d rows", len(validated_data))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO breweries (
                    id,
                    brewery_type,
                    name,
                    address_1,
                    address_2,
                    address_3,
                    city,
                    state_province,
                    postal_code,
                    country,
                    longitude,
                    latitude,
                    phone,
                    website_url
                )
                VALUES (
                    %(id)s,
                    %(brewery_type)s,
                    %(name)s,
                    %(address_1)s,
                    %(address_2)s,
                    %(address_3)s,
                    %(city)s,
                    %(state_province)s,
                    %(postal_code)s,
                    %(country)s,
                    %(longitude)s,
                    %(latitude)s,
                    %(phone)s,
                    %(website_url)s
                )
                ON CONFLICT (id)
                DO UPDATE SET
                    brewery_type=Excluded.brewery_type,
                    name=Excluded.name,
                    address_1=Excluded.address_1,
                    address_2=Excluded.address_2,
                    address_3=Excluded.address_3,
                    city=Excluded.city,
                    state_province=Excluded.state_province,
                    postal_code=Excluded.postal_code,
                    country=Excluded.country,
                    longitude=Excluded.longitude,
                    latitude=Excluded.latitude,
                    phone=Excluded.phone,
                    website_url=Excluded.website_url,
                    updated_at=CURRENT_TIMESTAMP
            """,
                validated_data,
            )

    logger.info("Processed %d rows", len(validated_data))
