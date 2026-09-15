import os

# config.py reads DB_URL at import time, and importing the load module for its Brewery model pulls that in
os.environ.setdefault("DB_URL", "postgresql://localhost:5432/pipeline_btw_test")
