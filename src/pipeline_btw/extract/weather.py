import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "weather.db"
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
        "latitude": data["results"][0]["latitude"],
        "longitude": data["results"][0]["longitude"],
    }


def get_forecast(location):
    location_data = geocode(location)
    lat, long = location_data["latitude"], location_data["longitude"]

    response = httpx.get(
        FORECAST_API_URL,
        params={
            "latitude": lat,
            "longitude": long,
            "past_days": 0,
            "forecast_days": 1,
            "timezone": "auto",
            "temperature_unit": "fahrenheit",
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


def get_hourly_data(data):
    hourly = data["hourly"]

    rows = zip(
        hourly["time"],
        hourly["temperature_2m"],
        hourly["relative_humidity_2m"],
        hourly["precipitation"],
        hourly["weather_code"],
        hourly["wind_speed_10m"],
        strict=True,
    )

    rows = [
        (
            time,
            temperature,
            humidity,
            precipitation,
            weather_code,
            wind_speed,
        )
        for (
            time,
            temperature,
            humidity,
            precipitation,
            weather_code,
            wind_speed,
        ) in rows
    ]

    return rows


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather (
                id TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                time TEXT NOT NULL,
                temperature REAL,
                humidity INTEGER,
                precipitation REAL,
                weather_code INTEGER,
                wind_speed REAL,
                inserted_at TEXT NOT NULL
            )
            """
        )


def insert_record(record):
    location = record["location"]
    latitude = record["latitude"]
    longitude = record["longitude"]
    hourly_data = get_hourly_data(record)
    inserted_at = datetime.now(UTC).isoformat()

    rows = [
        (
            str(uuid.uuid4()),
            location,
            latitude,
            longitude,
            time,
            temperature,
            humidity,
            precipitation,
            weather_code,
            wind_speed,
            inserted_at,
        )
        for (
            time,
            temperature,
            humidity,
            precipitation,
            weather_code,
            wind_speed,
        ) in hourly_data
    ]

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            INSERT INTO weather (
                id,
                location,
                latitude,
                longitude,
                time,
                temperature,
                humidity,
                precipitation,
                weather_code,
                wind_speed,
                inserted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    return f"{len(rows)} records inserted"


init_db()
weather = get_forecast("Los Angeles, CA")
insert_record(weather)
