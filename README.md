# Competitor Price Watch: Serverless E-commerce Data Pipeline

A professional end-to-end data engineering pipeline built on Google Cloud Platform (GCP). This project scrapes e-commerce data, enriches it with real-time currency rates, and orchestrates the ELT (Extract, Load, Transform) process into a BigQuery Data Warehouse using Airflow.

## 🏗️ Architecture
1.  **Extract:** Python scripts (BeautifulSoup) scrape product data and fetch USD/EUR rates via API.
2.  **Load (Raw):** JSON files are saved locally in NDJSON format and uploaded to **Google Cloud Storage (GCS)**.
3.  **Transform & Load (Warehouse):** **Airflow** triggers jobs to load raw data into **BigQuery** staging tables and executes SQL (Star Schema) to populate production Fact and Dimension tables.
4.  **Orchestration:** Managed by **Apache Airflow** running in Docker.
5.  **CI/CD:** Automated testing and linting via **GitHub Actions**.

---

## 🚀 Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- A GCP Project with a Service Account (Storage Admin & BigQuery Admin permissions)
- A GCS Bucket in the `US` region.

### 2. Environment Setup
1. Clone the repository and create a `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and fill in your details:
   - `GCP_RAW_BUCKET`: Your US-based GCS bucket name.
   - `AIRFLOW_FERNET_KEY`: (Provided in example, or generate your own).

3. Place your GCP Service Account JSON key in the root and rename it to `service-account-key.json`.

### 3. Initialize & Start Pipeline
Initialize the Airflow database and create the admin user:
```bash
docker-compose up airflow-init
```

Start all services (Airflow Webserver, Scheduler, and Postgres):
```bash
docker-compose up -d
```

### 4. Running the Pipeline
1. Open the Airflow UI: [http://localhost:8080](http://localhost:8080) (Login: `admin` / `admin`).
2. Find the `price_watch_pipeline` DAG.
3. Toggle it to **Unpause** and click **Trigger DAG**.

### 5. (Optional) Infrastructure as Code
Instead of creating resources manually, you can use Terraform:
1. Install [Terraform](https://developer.hashicorp.com/terraform/downloads).
2. Navigate to the folder: `cd terraform`
3. Initialize: `terraform init`
4. Apply:
   ```bash
   terraform apply -var="project_id=YOUR_PROJECT_ID" -var="bucket_name=YOUR_BUCKET_NAME"
   ```

---

## 🛠️ Tech Stack
- **Language:** Python 3.11 (Modular OOP)
- **Ingestion:** Requests, BeautifulSoup, REST API
- **Storage:** Google Cloud Storage (GCS)
- **Data Warehouse:** BigQuery (SQL Star Schema)
- **Orchestration:** Apache Airflow
- **Containerization:** Docker & Docker Compose
- **Testing:** Pytest & Unittest

---

## 📈 Data Model (Star Schema)
The pipeline transforms raw JSON into a structured analytical model:
- `dim_products`: Contains product metadata (ID, Title, Rating).
- `fact_prices`: Contains time-series price data and currency information.

---

## ✅ Quality & CI/CD
- **Unit Tests:** Run locally with `pytest tests/`.
- **Linting:** Flake8 for PEP8 compliance.
- **GitHub Actions:** Automatically runs tests on every push to `main`.