import json

from pipeline_btw.client.api import fetch_data

data = fetch_data("?page=1&per_page=50")

print(json.dumps(data, indent=2))
