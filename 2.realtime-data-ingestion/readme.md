# 🛠 Project 2/50: Streaming Data with Pub/Sub, Dataflow, and BigQuery


# Real-Time Streaming Pipeline on Google Cloud

This project sets up a real-time data pipeline using:

- **Pub/Sub** for message ingestion
- **Dataflow (Apache Beam)** for stream processing
- **BigQuery** for storage and analytics

---

## 🗂 Project Structure
.
├── publisher.py # Publishes test JSON events to Pub/Sub
├── streaming_pipeline.py # Apache Beam pipeline: Pub/Sub → BigQuery
├── requirements.txt # Python dependencies
└── README.md # Setup instructions

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

## 🛠 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/gcp-streaming-pipeline.git
cd gcp-streaming-pipeline

2. Install Dependencies
```
pip install -r requirements.txt
```

3. Create Pub/Sub Topic & Subscription
```
gcloud pubsub topics create your-topic-id
gcloud pubsub subscriptions create your-sub-id --topic=your-topic-id
```

4. Create BigQuery Dataset and Table
Replace with your actual project and dataset names.

sql
Copy
Edit
CREATE TABLE `your-project-id.your_dataset.your_table` (
  user_id INT64,
  action STRING,
  timestamp FLOAT64
);
5. Create GCS Bucket (for Dataflow staging)
bash
Copy
Edit
gsutil mb gs://your-bucket-name/
🚀 Run the Publisher
Edit publisher.py to fill in:

project_id

topic_id

Run it:

bash
Copy
Edit
python publisher.py
🧪 Test Dataflow Pipeline Locally
Edit streaming_pipeline.py and use DirectRunner to run locally:

bash
Copy
Edit
python streaming_pipeline.py
This is for testing purposes only.

☁️ Run on Google Cloud (Dataflow)
Update these options in streaming_pipeline.py:

options.view_as(StandardOptions).runner = "DataflowRunner"
options.view_as(GoogleCloudOptions).project = "your-project-id"
options.view_as(GoogleCloudOptions).region = "us-central1"
options.view_as(GoogleCloudOptions).staging_location = "gs://your-bucket-name/staging"
options.view_as(GoogleCloudOptions).temp_location = "gs://your-bucket-name/temp"

Then run:

python streaming_pipeline.py


