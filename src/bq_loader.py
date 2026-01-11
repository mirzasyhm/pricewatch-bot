import os
import logging
from google.cloud import bigquery
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BigQueryLoader:
    def __init__(self, dataset_name='price_watch_dw'):
        self.client = bigquery.Client()
        self.dataset_name = dataset_name
        self.project_id = self.client.project
        self.dataset_ref = f"{self.project_id}.{self.dataset_name}"

    def create_dataset(self):
        try:
            # We use 'US' (multi-region) as it is the most standard location.
            # NOTE: Your GCS bucket MUST also be in the US region for this to work.
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US" 
            dataset = self.client.create_dataset(dataset, exists_ok=True)
            logging.info(f"Dataset {self.dataset_ref} ready.")
        except Exception as e:
            logging.error(f"Failed to create dataset: {e}")

    def load_staging_table(self, gcs_uri):
        """Loads JSON from GCS into the staging table"""
        table_id = f"{self.dataset_ref}.staging_products"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # Replace staging every run
            autodetect=True # Simplification for this project, ideally use schema json
        )

        try:
            load_job = self.client.load_table_from_uri(
                gcs_uri, table_id, job_config=job_config
            )
            load_job.result()  # Waits for the job to complete.
            logging.info(f"Loaded {load_job.output_rows} rows into {table_id}.")
            return True
        except Exception as e:
            logging.error(f"BigQuery Load Failed: {e}")
            return False

    def run_transformation(self):
        """Reads SQL file and executes it to populate Star Schema"""
        try:
            with open('sql/transform.sql', 'r') as f:
                sql_template = f.read()
            
            # Inject variable table names
            sql = sql_template.format(project_id=self.project_id, dataset=self.dataset_name)
            
            query_job = self.client.query(sql)
            query_job.result() # Wait for completion
            logging.info("Transformation SQL executed successfully.")
        except Exception as e:
            logging.error(f"Transformation Failed: {e}")

if __name__ == "__main__":
    # Example Trigger
    bucket_name = os.getenv("GCP_RAW_BUCKET")
    if not bucket_name:
        logging.error("GCP_RAW_BUCKET env var missing")
        exit(1)

    loader = BigQueryLoader()
    loader.create_dataset()
    
    # Construct GCS URI for today's file (Assuming default path from gcs_loader.py)
    today = datetime.now().strftime('%Y-%m-%d')
    gcs_uri = f"gs://{bucket_name}/raw/books/{today}_books.json"
    
    logging.info(f"Attempting to load: {gcs_uri}")
    
    if loader.load_staging_table(gcs_uri):
        loader.run_transformation()
