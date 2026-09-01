from pipeline_btw.client.api import fetch_data


def extract_data():
    params = {"page": 1, "per_page": 5}
    return fetch_data(params)
