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

1. **Simple Event driven file processing**
   This project deploys a Google Cloud Function that triggers when a file is uploaded to a GCS bucket and loads it into a BigQuery table automatically

2. **Data Processing with Realtime pipeline**
   - Use Google Cloud dataflow to stream data using Apache beam.
   - Create fake data to publish on pubsub
   - Stream data to pubsub to Bigquery using dataflow stream job



## Follow for Updates

I am planning to add 50 such projects to this repository every week. Keep following my [LinkedIn](https://www.linkedin.com/in/manojvsj/) for updates.