import httpx

BREWERY_API_URL = "https://api.openbrewerydb.org/v1/breweries"


def fetch_data(params: dict):
    response = httpx.get(BREWERY_API_URL, params=params)
    response.raise_for_status()
    return response.json()
