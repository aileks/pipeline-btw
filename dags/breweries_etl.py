from airflow.sdk import dag, task
from pendulum import datetime

from pipeline_btw.extract.breweries import extract_data
from pipeline_btw.load.postgres import load_data
from pipeline_btw.transform.breweries import transform_data


@dag(
    dag_id="breweries_etl",
    schedule="@daily",
    start_date=datetime(2026, 9, 1, tz="UTC"),
    catchup=False,
)
def breweries_etl():
    @task
    def extract() -> list[dict]:
        return extract_data(5000, 200)

    @task
    def transform(raw: list[dict]) -> list[dict]:
        return transform_data(raw)

    @task
    def load(cleaned: list[dict]) -> None:
        load_data(cleaned)

    load(transform(extract()))


breweries_etl()
