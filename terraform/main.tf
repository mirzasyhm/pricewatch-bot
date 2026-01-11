provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. GCS Bucket (Data Lake)
resource "google_storage_bucket" "data_lake" {
  name          = var.bucket_name
  location      = "US" # Multi-region
  force_destroy = true # Allows deleting bucket even if it has files (Useful for testing)

  uniform_bucket_level_access = true
}

# 2. BigQuery Dataset (Data Warehouse)
resource "google_bigquery_dataset" "data_warehouse" {
  dataset_id                  = "price_watch_dw"
  friendly_name               = "Price Watch Data Warehouse"
  description                 = "Star Schema for E-commerce Price Watch"
  location                    = "US" # Must match Bucket location (Multi-region)
  default_table_expiration_ms = null

  labels = {
    env = "production"
  }
}
