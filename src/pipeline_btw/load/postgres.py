import logging
import re
from typing import Literal
from uuid import UUID

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ValidationError,
    field_serializer,
    field_validator,
    model_validator,
)

from pipeline_btw.db.connection import get_connection

logger = logging.getLogger(__name__)


class Brewery(BaseModel):
    id: UUID
    brewery_type: Literal[
        "micro",
        "nano",
        "regional",
        "brewpub",
        "large",
        "planning",
        "bar",
        "contract",
        "proprietor",
        "closed",
        "taproom",
        "cidery",
        "beergarden",
    ]
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
    website_url: AnyHttpUrl | None = None

    @model_validator(mode="before")
    @classmethod
    def convert_empty_strings_to_none(cls, data: dict) -> dict:
        """Globally converts empty strings to None across all fields."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.strip() == "":
                    data[key] = None
                elif value == "null":
                    data[key] = None
        return data

    @field_serializer("website_url")
    def serialize_url(self, website_url: AnyHttpUrl | None, _info):
        """Converts URL back into a plain Python string for database loading"""
        return str(website_url) if website_url else None

    @field_validator("phone", mode="before")
    @classmethod
    def clean_phone(cls, val):
        """Strips everything except digits (e.g., '(123) 456-7890' -> '1234567890')"""
        if val is None:
            return val
        cleaned = re.sub(r"\D", "", str(val))
        return cleaned if cleaned else None

    @field_validator("longitude", "latitude", mode="before")
    @classmethod
    def clean_coordinates(cls, val):
        """Ensures bad string nulls don't crash flaot parsing."""
        if val is None:
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
