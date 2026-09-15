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


def transform_data(raw_data: list[dict]):
    logger.info("Validating %d rows", len(raw_data))

    validated_data = []
    for row in raw_data:
        try:
            brewery = Brewery(**row)
            validated_data.append(brewery.model_dump())
        except ValidationError as e:
            logger.error(
                "Skipping row due to validation error on brewery ID %s: %s", row.get("id"), e
            )
            continue

    logger.info("Transforming %d rows", len(validated_data))

    data_cleaned = [
        {
            "id": brewery["id"],
            "brewery_type": brewery["brewery_type"],
            "name": brewery["name"],
            "address_1": brewery["address_1"],
            "address_2": brewery["address_2"],
            "address_3": brewery["address_3"],
            "city": brewery["city"],
            "state_province": brewery["state_province"],
            "postal_code": brewery["postal_code"],
            "country": brewery["country"],
            "longitude": (
                float(brewery["longitude"]) if brewery["longitude"] is not None else None
            ),
            "latitude": (float(brewery["latitude"]) if brewery["latitude"] is not None else None),
            "phone": brewery["phone"],
            "website_url": brewery["website_url"],
        }
        for brewery in validated_data
    ]
    return data_cleaned
