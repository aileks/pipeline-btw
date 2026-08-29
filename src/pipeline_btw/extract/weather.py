import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx

DB_PATH = Path("../../data/weather.db")
GEOCODE_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"


def geocode(location):
    response = httpx.get(
        GEOCODE_API_URL,
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )

    response.raise_for_status()
    data = response.json()

    if not data.get("results"):
        raise ValueError(f"Location not found: {location}")

    return {
        "lat": data["results"][0]["latitude"],
        "long": data["results"][0]["longitude"],
    }


def get_forecast(location):
    location_data = geocode(location)
    lat, long = location_data["lat"], location_data["long"]

    response = httpx.get(
        FORECAST_API_URL,
        params={
            "latitude": lat,
            "longitude": long,
            "past_days": 0,
            "forecast_days": 1,
            "timezone": "auto",
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ],
        },
    )

    response.raise_for_status()
    data = response.json()

    return {"location": location, **data}


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather (
                id TEXT PRIMARY KEY,
                location TEXT,
                temperature REAL,
                inserted_at TEXT NOT NULL
            )
            """
        )
        conn.close()


def insert_data(record):
    location = record["location"]
    temperature = record["temperature_2m"]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO weather (id, location, temperature, inserted_at)
            VALUES(?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), location, temperature, datetime.now(UTC).isoformat()),
        )


weather = get_forecast("Los Angeles, CA")
