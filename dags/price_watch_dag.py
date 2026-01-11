from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'price_watch_pipeline',
    default_args=default_args,
    description='Serverless E-commerce Data Pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2026, 1, 6),
    catchup=False,
    tags=['portfolio', 'etl'],
) as dag:

    # Task 1: Scrape Data
    scrape_books = BashOperator(
        task_id='scrape_books',
        bash_command='python src/scraper.py',
        cwd='/opt/airflow' # Standard Airflow Docker path, adjust if running locally
    )

    # Task 2: Fetch Currency
    fetch_currency = BashOperator(
        task_id='fetch_currency',
        bash_command='python src/currency_api.py',
        cwd='/opt/airflow'
    )

    # Task 3: Upload to GCS
    upload_to_gcs = BashOperator(
        task_id='upload_to_gcs',
        bash_command='python src/gcs_loader.py',
        cwd='/opt/airflow'
    )

    # Task 4: Load to BigQuery & Transform
    load_to_bq = BashOperator(
        task_id='load_to_bq',
        bash_command='python src/bq_loader.py',
        cwd='/opt/airflow'
    )

    # Dependencies
    [scrape_books, fetch_currency] >> upload_to_gcs >> load_to_bq
