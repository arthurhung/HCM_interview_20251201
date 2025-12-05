from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# 這裡直接從 /opt/airflow/app 裡 import
from crawler import HealthMythCrawler
from csv_helper import CSVHelper

CSV_PATH = "/opt/airflow/data/hpa_health_myths.csv"
FIELDNAMES = [
    "pid",
    "title",
    "url",
    "publish_date",
    "update_date",
    "content",
]


def run_hpa_crawler(**kwargs):
    storage = CSVHelper(path=CSV_PATH, fieldnames=FIELDNAMES)
    crawler = HealthMythCrawler(storage=storage)
    crawler.run(initial_n=10, max_pages=5)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="hpa_health_myths_crawler",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 3 * * *",  # 每天 03:00
    catchup=False,
    tags=["hpa", "crawler"],
) as dag:
    crawl_task = PythonOperator(
        task_id="run_hpa_crawler",
        python_callable=run_hpa_crawler,
    )
