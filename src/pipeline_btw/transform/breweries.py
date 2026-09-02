def transform_data(breweries_data_raw):
    print("Transforming data...")
    breweries_data_cleaned = [
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
        for brewery in breweries_data_raw
    ]
    return breweries_data_cleaned
