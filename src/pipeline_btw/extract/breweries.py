import json

from pipeline_btw.client.api import fetch_data

params = {"page": 1, "per_page": 50}
data = fetch_data(params)
print(json.dumps(data, indent=2))
