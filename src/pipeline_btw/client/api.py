import httpx

BREWERY_API_URL = "https://api.openbrewerydb.org/v1/breweries"


def fetch_data(params: str):
    response = httpx.get(f"{BREWERY_API_URL}?{params}")
    response.raise_for_status()
    return response.json()
