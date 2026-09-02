from pipeline_btw.client.api import fetch_data


def extract_data(row_limit=200):
    print("Extracting data...")
    page = 1
    breweries = []
    params = {"per_page": 200, "page": page}
    while len(breweries) < row_limit:
        try:
            data = fetch_data(params)
            if not data:
                break
            breweries.extend(data)
            page += 1
            params["page"] = page
        except Exception as e:
            print(f"\nSomething went wrong: {e}\n")
            raise
    return breweries[:row_limit]
