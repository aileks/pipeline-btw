import httpx

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


weather = get_forecast("Los Angeles, CA")

for k, v in weather.items():
    if k == "hourly":
        for kk, vv in v.items():
            print(f"{kk}: {vv}\n")
    else:
        print(f"{k}: {v}\n")
