## 🛠 Project 2/50: Streaming Data with Pub/Sub, Dataflow, and BigQuery


## Real-Time Streaming Pipeline on Google Cloud

This project sets up a real-time data pipeline using:

- **Pub/Sub** for message ingestion
- **Dataflow (Apache Beam)** for stream processing
- **BigQuery** for storage and analytics

---

## 🗂 Project Structure
```
.
├── publisher.py # Publishes test JSON events to Pub/Sub
├── streaming_pipeline.py # Apache Beam pipeline: Pub/Sub → BigQuery
├── requirements.txt # Python dependencies
└── README.md # Setup instructions
└── setup.sh # Setup GCP environment scripts
```
---

## ✅ Prerequisites

- Python 3.7+
- Google Cloud SDK installed (`gcloud init`)
- Google Cloud account with billing enabled
- Enable the following APIs:
  - Pub/Sub
  - BigQuery
  - Dataflow
- Create or use an existing GCP project

---

### 🛠 Setup Instructions

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/gcp-dataengineering-mini-projects.git
cd gcp-dataengineering-mini-projects/2.realtime-data-ingestion
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Fill the config details in the setup.sh script
```
PROJECT_ID="your-project-id"
TOPIC_ID="your-topic-id"
SUBSCRIPTION_ID="your-sub-id"
BQ_DATASET="your_dataset"
BQ_TABLE="your_table"
GCS_BUCKET="your-bucket-name"
REGION="us-central1"
```

#### Run the setup.sh to create the pubsub topic, gcs bucket and BQ objects
```
. ./setup.sh
```
Now your GCP Environment is Ready !!!!



#### 🚀 Run the Publisher
Edit publisher.py to fill in:
```
project_id
topic_id
```

Run it:
```
python publisher.py
```

NOTE: Open in another terminal and run the dataflow pipeline locally

Edit streaming_pipeline.py to fill in:
```
  project_id = ""
  dataset_id = ""
  table = ""
  subscription_id = ""
```

#### 🧪 Test Dataflow Pipeline Locally

use DirectRunner to run locally:

```
python streaming_pipeline.py
```

This is for testing purposes only.


#### ☁️ Run on Google Cloud (Dataflow)
Update these options in streaming_pipeline.py:
```
options.view_as(StandardOptions).runner = "DataflowRunner"
options.view_as(GoogleCloudOptions).project = "your-project-id"
options.view_as(GoogleCloudOptions).region = "us-central1"
options.view_as(GoogleCloudOptions).staging_location = "gs://your-bucket-name/staging"
options.view_as(GoogleCloudOptions).temp_location = "gs://your-bucket-name/temp"
```

Then run:
```
python streaming_pipeline.py
```

