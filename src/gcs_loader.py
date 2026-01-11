import logging
from google.cloud import storage
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GCSLoader:
    def __init__(self, bucket_name, service_account_key_path=None):
        """
        Initialize the GCS Loader.
        :param bucket_name: Name of the GCS bucket.
        :param service_account_key_path: Optional path to service account JSON key. 
                                         If None, uses default environment authentication.
        """
        self.bucket_name = bucket_name
        
        if service_account_key_path:
            self.client = storage.Client.from_service_account_json(service_account_key_path)
        else:
            # Falls back to GOOGLE_APPLICATION_CREDENTIALS env var or gcloud auth
            self.client = storage.Client()
            
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, source_file_name, destination_blob_name):
        """
        Uploads a file to the bucket.
        :param source_file_name: Local path to the file.
        :param destination_blob_name: path in GCS (e.g., 'raw/2023-10-27/data.json')
        """
        try:
            blob = self.bucket.blob(destination_blob_name)
            
            logging.info(f"Uploading {source_file_name} to gs://{self.bucket_name}/{destination_blob_name}...")
            blob.upload_from_filename(source_file_name)
            
            logging.info(f"File {source_file_name} uploaded to {destination_blob_name}.")
            return True
        except Exception as e:
            logging.error(f"Failed to upload {source_file_name}: {e}")
            return False

if __name__ == "__main__":
    import sys
    
    # Read bucket name from environment variable
    bucket_name = os.getenv("GCP_RAW_BUCKET")
    
    if not bucket_name:
        logging.error("Environment variable GCP_RAW_BUCKET is not set.")
        print("\n[ERROR] Please set your bucket name first:")
        print("PowerShell: $env:GCP_RAW_BUCKET=' price-watch-raw-data-mirzaus'")
        print("Bash: export GCP_RAW_BUCKET=' price-watch-raw-data-mirzaus'\n")
        sys.exit(1)
        
    loader = GCSLoader(bucket_name)
    
    # Upload Scraper Data
    if os.path.exists("data/books_data.json"):
        loader.upload_file("data/books_data.json", f"raw/books/{datetime.now().strftime('%Y-%m-%d')}_books.json")
    else:
        logging.warning("data/books_data.json not found. Run scraper.py first.")

    # Upload Currency Data
    if os.path.exists("data/currency_rate.json"):
        loader.upload_file("data/currency_rate.json", f"raw/currency/{datetime.now().strftime('%Y-%m-%d')}_rate.json")
    else:
        logging.warning("data/currency_rate.json not found. Run currency_api.py first.")
