from pipeline_btw.extract.breweries import extract_data
from pipeline_btw.load.postgres import load_data
from pipeline_btw.transform.breweries import transform_data

raw_data = extract_data(5000)
cleaned_data = transform_data(raw_data)
try:
    load_data(cleaned_data)
    print("Data loaded successfully!")
except Exception as e:
    print(f"Data loading failed: {e}")
    raise
