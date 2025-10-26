# GCP Data Engineering Mini Projects

This repository contains a collection of mini projects focused on data engineering using Google Cloud Platform (GCP) services. Each project demonstrates different aspects of data engineering, including data storage, processing, and analysis using various GCP tools and services.

## Prerequisites

- Google Cloud Platform account
- Python 3.7 or higher
- Virtual environment setup

### Setting Up Google Credentials

#### Google Cloud Credentials

1. **Create a Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

2. **Enable APIs:**
   - Enable the necessary APIs for your project, such as BigQuery, Cloud Storage, and Dataproc.

3. **Create Service Account:**
   - Navigate to the "IAM & Admin" section and select "Service Accounts".
   - Create a new service account and grant it the necessary roles (e.g., BigQuery Admin, Storage Admin).

4. **Generate Key File:**
   - After creating the service account, generate a new JSON key file and download it.

5. **Set Up Credentials:**
   - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to the downloaded JSON key file:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
     ```


#### Clone the repository:
   ```bash
   git clone https://github.com/your-username/gcp-dataengineering-mini-projects.git
   cd gcp-dataengineering-mini-projects
   ```

## Projects

### 1. **[Event Driven File Processing](./1.event-driven-file-processing/)**
🛠 **Project 1/50** | **Tools:** Cloud Functions, GCS, BigQuery

This project deploys a Google Cloud Function that triggers when a file is uploaded to a GCS bucket and loads it into a BigQuery table automatically.

**Features:**
- Automatic CSV file processing on GCS upload
- Schema auto-detection in BigQuery
- Event-driven serverless architecture

---

### 2. **[Real-time Data Ingestion](./2.realtime-data-ingestion/)**
🛠 **Project 2/50** | **Tools:** Pub/Sub, Dataflow (Apache Beam), BigQuery

Real-time data processing pipeline using Pub/Sub for message ingestion, Dataflow for stream processing, and BigQuery for analytics.

**Features:**
- Pub/Sub message streaming
- Apache Beam pipeline processing
- Real-time data insertion to BigQuery
- Support for both local testing and cloud deployment

---

### 3. **[Weather Data Pipeline](./3.weather-batch-processing/)**
🛠 **Project 3/50** | **Tools:** Cloud Functions, Cloud Scheduler, BigQuery, Open-Meteo API

Automated weather data collection system that fetches live weather data every 15 minutes and stores it in BigQuery for analysis.

**Features:**
- Scheduled data collection (15-minute intervals)
- Open-Meteo API integration (no API key required)
- Historical weather data accumulation
- UTC timestamp handling

---

### 4. **[Batch Processing with Spark](./4.dataproc-spark-processing/)**
🛠 **Project 4/50** | **Tools:** Dataproc, PySpark, BigQuery External Tables, GCS

Process historical order data using PySpark on Dataproc, write partitioned Parquet files to GCS, and create BigQuery External tables for reporting.

**Features:**
- PySpark data processing on Dataproc
- Partitioned Parquet file output
- BigQuery External table integration
- Automated cluster management

---

### 5. **[Data Quality Checks Framework](./5.data-quality-checks-framework/)**
🛠 **Project 5/50** | **Tools:** Cloud Functions, BigQuery, Cloud Scheduler, PyYAML

Automated data quality validation framework that runs configurable checks on BigQuery tables with scheduled monitoring.

**Features:**
- Configurable data quality checks (null, duplicate, range validation)
- Partition-based quality assessment
- Automated scheduling with Cloud Scheduler
- Quality metrics reporting and tracking

---

### 6. **[Medallion Architecture with Iceberg](./6.dataproc-spark-iceberg-medallion/)**
🛠 **Project 6/50** | **Tools:** Dataproc, Apache Spark, Apache Iceberg, BigQuery, Dataproc Metastore

Complete medallion architecture (Bronze-Silver-Gold) implementation using Dataproc Spark, Apache Iceberg, and BigQuery external tables.

**Features:**
- Three-tier medallion architecture (Bronze/Silver/Gold layers)
- Apache Iceberg ACID transactions and time travel
- Schema evolution capabilities
- BigQuery external table integration
- Dataproc Metastore for metadata management

---

### 7. **[Lambda Architecture with Iceberg & BigQuery](./7.iceberg-bigquery-lambda-architecture/)**
🛠 **Project 7/50** | **Tools:** Pub/Sub, Dataflow, BigQuery, Apache Iceberg, Dataproc Serverless, GCS

Advanced Lambda Architecture implementation with both real-time (speed layer) and batch processing layers for comprehensive data processing.

**Features:**
- **Speed Layer:** Pub/Sub → Dataflow → BigQuery (real-time analytics)
- **Batch Layer:** Pub/Sub → Dataflow → GCS → Spark → Iceberg (comprehensive analysis)
- **Serving Layer:** BigQuery for real-time queries, Iceberg for complex analytics
- Apache Iceberg for ACID transactions and time travel
- Dataproc Serverless for batch processing
- End-to-end monitoring and observability

---

### 8. **[Natural Language to BigQuery with Vertex AI](./8.bigquery-vertexai-mcp-connection/)**
🛠 **Project 8/50** | **Tools:** Cloud Run, Streamlit, Vertex AI (Gemini), BigQuery, FastAPI

Natural language interface to query BigQuery using Vertex AI for SQL generation and MCP (Model Context Protocol) pattern for secure execution.

**Features:**
- Natural language to SQL conversion using Vertex AI Gemini models
- Secure query execution using MCP pattern
- Interactive web interface with Streamlit
- Automated input validation and query optimization
- AI-powered result summaries
- Service-to-service authentication with Cloud Run

---

## Architecture Progression

This collection demonstrates a progression from simple to complex data engineering architectures:

1. **Event-driven** (Project 1) → **Streaming** (Project 2) → **Scheduled** (Project 3)
2. **Batch Processing** (Project 4) → **Data Quality** (Project 5)
3. **Medallion Architecture** (Project 6) → **Lambda Architecture** (Project 7)
4. **AI-Powered Analytics** (Project 8) - Natural language interfaces with Generative AI

Each project builds upon concepts from previous ones while introducing new GCP services and architectural patterns.

## Follow for Updates

I am planning to add 50 such projects to this repository every week. Keep following my [LinkedIn](https://www.linkedin.com/in/manojvsj/) for updates.