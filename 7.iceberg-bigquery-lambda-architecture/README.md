# 🏗️ Project 7/50: Lambda Architecture with GCP, Iceberg & BigQuery

![flow-diagram](architecture-diagram.png)

A **beginner-friendly** real-time streaming data pipeline implementing **Lambda Architecture** pattern using Google Cloud Platform.

---

## 🛠️ Tools Used
- **Pub/Sub** - Message ingestion and streaming
- **Dataflow (Apache Beam)** - Stream processing engine
- **BigQuery** - Real-time analytics and serving layer
- **Apache Iceberg** - Batch processing and data lake storage
- **Dataproc Serverless** - Spark jobs for batch processing
- **Cloud Storage (GCS)** - Data staging and storage
- **Dataproc Metastore** - Hive metastore service

---

## 🏛️ Architecture Overview

This project implements **Lambda Architecture** with two processing paths:

```
                   ┌─── Real-time Path ────┐
Pub/Sub ──→ Dataflow ├─── BigQuery (Speed Layer)
                   └─── GCS Files ────┐
                                      │
                   Spark Batch Jobs ──┴─── Iceberg Tables (Batch Layer)
```

### **Speed Layer** (Real-time)
- **Pub/Sub** → **Dataflow** → **BigQuery**
- Processes streaming data in real-time for immediate analytics
- Low latency queries and dashboards

### **Batch Layer** (Comprehensive)
- **Pub/Sub** → **Dataflow** → **GCS** → **Spark** → **Iceberg**
- Processes all historical data for comprehensive analysis
- ACID transactions, time travel, schema evolution

### **Serving Layer**
- **BigQuery**: Real-time queries and dashboards
- **Iceberg**: Complex analytics, historical analysis, ML features

---

## 📁 Project Structure

```
7.iceberg-bigquery-lambda-architecture/
├── README.md                    # This comprehensive guide
├── setup.sh                    # 🚀 Infrastructure setup (RUN FIRST)
├── cleanup.sh                  # 🧹 Resource cleanup (RUN LAST)
├── requirements.txt            # Python dependencies
├── main.py                     # Pipeline orchestrator (optional)
├── run_batch_job.sh           # Simple batch job runner
├── submit_batch_job.sh        # 📊 Batch processing jobs (RUN LAST)
├── config/
│   └── config.yaml            # ⚙️ Central configuration
├── dataflow_jobs/
│   ├── streaming_pipeline.py  # 🌊 Main Dataflow streaming job
│   └── run_example.sh         # Dataflow job launcher
├── pub_sub/
│   └── publisher.py           # 📤 Test data publisher
├── spark_jobs/
│   ├── iceberg_setup.py       # Iceberg table initialization
│   ├── gcs_to_iceberg_batch.py # Batch data loading
│   └── batch_analysis.py      # Analytics on Iceberg data
└── jars/
    └── iceberg-spark-runtime-3.5_2.13-1.9.2.jar
```

---

## ✅ Prerequisites

### 1. GCP Account Setup
- Google Cloud account with **billing enabled**
- Google Cloud SDK installed (`gcloud --version`)
- Authenticated with GCP (`gcloud auth login`)
- Project created with Owner/Editor permissions

### 2. Required APIs
The setup script will enable these, but ensure you have permissions:
- Pub/Sub API
- Dataflow API
- BigQuery API
- Dataproc API
- Cloud Storage API
- Dataproc Metastore API

### 3. Local Environment
```bash
# Check Python version (3.7+ required)
python3 --version

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Quick Start Guide

### **STEP 1: Infrastructure Setup** (⚠️ **RUN FIRST**)

```bash
# Navigate to project directory
cd 7.iceberg-bigquery-lambda-architecture/

# Make setup script executable
chmod +x setup.sh

# Edit configuration in setup.sh (REQUIRED!)
# Update these variables:
PROJECT_ID="your-gcp-project-id"        # ⚠️ CHANGE THIS
UNIQUE_KEY="your-unique-suffix"         # ⚠️ CHANGE THIS
REGION="your-preferred-region"          # Optional: default europe-west2

# Run infrastructure setup (takes 5-10 minutes)
./setup.sh
```

**What setup.sh does:**
- ✅ Enables required GCP APIs
- ✅ Creates GCS buckets for storage
- ✅ Creates Pub/Sub topics and subscriptions
- ✅ Sets up BigQuery datasets
- ✅ Creates Dataproc Metastore (Hive)
- ✅ Initializes Iceberg tables with sample data
- ✅ Uploads Spark scripts and JAR files
- ✅ Configures all connection strings

---

### **STEP 2: Start Real-time Streaming** (🌊 **Speed Layer**)

```bash
# In Terminal 1: Start Dataflow streaming pipeline
cd dataflow_jobs/
chmod +x run_dataflow.sh
./run_dataflow.sh

# Monitor at: https://console.cloud.google.com/dataflow
```

**What streaming does:**
- ✅ Reads messages from Pub/Sub
- ✅ Writes to BigQuery (real-time analytics)
- ✅ Writes to GCS (for batch processing)

---

### **STEP 3: Publish Test Data** (📤 **Data Source**)

```bash
# In Terminal 2: Run data publisher
cd pub_sub/
python3 publisher.py

# Choose option:
# 1 = continuous publishing (recommended)
# 2 = batch publishing
# 3 = single message test

# For testing, use: 50 messages with 2 second delay
```

**Sample data format:**
```json
{
  "event_id": "evt_123456",
  "event_type": "purchase",
  "user_id": "user_1234",
  "event_timestamp": "2024-01-01T10:00:00Z",
  "product": "laptop",
  "price": 999.99,
  "country": "UK"
}
```

---

### **STEP 4: Run Batch Processing** (📊 **Batch Layer**)

```bash
# In Terminal 3: Process batch data (after some streaming)
chmod +x submit_batch_job.sh

# Process today's data
./submit_batch_job.sh

# Or process specific date
./submit_batch_job.sh 2024-01-01
```

**What batch processing does:**
- ✅ Loads GCS files into Iceberg tables
- ✅ Runs analytics on Iceberg data
- ✅ Provides comprehensive historical analysis

---

## 📊 Monitoring & Verification

### **Real-time Layer (BigQuery)**
```sql
-- Check real-time data in BigQuery
SELECT
  event_type,
  COUNT(*) as event_count,
  AVG(price) as avg_price
FROM `your-project.streaming_analytics.events`
WHERE event_timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY event_type
ORDER BY event_count DESC;
```

### **Batch Layer (Iceberg)**
Access through Dataproc jobs or external tools that support Iceberg format.

### **Monitoring Dashboards**
- **Dataflow Jobs**: https://console.cloud.google.com/dataflow
- **Pub/Sub Messages**: https://console.cloud.google.com/cloudpubsub
- **BigQuery**: https://console.cloud.google.com/bigquery
- **Dataproc Batches**: https://console.cloud.google.com/dataproc/batches

---

## 🔧 Configuration

### **Central Config** (`config/config.yaml`)
```yaml
project:
  id: "your-gcp-project-id"
  region: "europe-west2"

pubsub:
  input_topic: "projects/your-project/topics/raw-data-stream"

bigquery:
  dataset: "streaming_analytics"
  table: "events"

iceberg:
  warehouse: "your-iceberg-bucket"
  database: "streaming_db"
  table: "events"
```

---

## 🧹 Resource Cleanup (💰 **IMPORTANT for Cost Control**)

### **STEP 5: Clean Up Resources** (⚠️ **RUN TO AVOID CHARGES**)

```bash
# Stop all running jobs first
# 1. Stop Dataflow job from console
# 2. Stop publisher script (Ctrl+C)

# Run cleanup script
chmod +x cleanup.sh
./cleanup.sh

# Verify cleanup in GCP Console
```

**What cleanup.sh removes:**
- ✅ Dataflow jobs (if running)
- ✅ Pub/Sub topics and subscriptions
- ✅ GCS buckets and all data
- ✅ BigQuery datasets
- ✅ Dataproc Metastore (expensive!)
- ✅ All created resources

⚠️ **IMPORTANT**: Metastore service costs ~$1/hour. Always run cleanup!

---

## 🎯 Learning Objectives

By completing this project, you'll understand:

1. **Lambda Architecture Pattern**
   - Speed vs Batch layer trade-offs
   - Serving layer design decisions

2. **Google Cloud Streaming**
   - Pub/Sub message patterns
   - Dataflow pipeline development
   - BigQuery streaming inserts

3. **Modern Data Lake**
   - Apache Iceberg table format
   - ACID transactions in data lakes
   - Schema evolution and time travel

4. **Production Considerations**
   - Error handling and monitoring
   - Cost optimization
   - Resource management

---

## 🚨 Troubleshooting

### **Common Issues**

**1. "Permission denied" errors**
```bash
# Ensure proper GCP authentication
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**2. "API not enabled" errors**
```bash
# Enable required APIs manually
gcloud services enable dataflow.googleapis.com
gcloud services enable pubsub.googleapis.com
```

**3. Dataflow job fails**
```bash
# Check logs in GCP Console → Dataflow → Job → Logs
# Common issue: config.yaml path problems
```

**4. No data in BigQuery**
```bash
# Check Pub/Sub subscription has messages
# Check Dataflow job is running
# Verify topic names match in config
```

**5. Metastore connection fails**
```bash
# Wait 5-10 minutes after setup for metastore to be ready
# Check metastore status in GCP Console
```

---

## 💡 Next Steps

### **Extend the Project**
1. **Add monitoring dashboards** (Data Studio/Looker)
2. **Implement data quality checks** (Great Expectations)
3. **Add machine learning** (Vertex AI integration)
4. **Scale testing** (higher message volumes)
5. **Add alerting** (Cloud Monitoring)

### **Production Enhancements**
1. **Error handling** (Dead letter queues)
2. **Schema registry** (Schema validation)
3. **Security** (IAM, VPC, encryption)
4. **CI/CD** (Cloud Build pipelines)
5. **Cost optimization** (Committed use discounts)

---

## 📚 Additional Resources

- [Apache Beam Documentation](https://beam.apache.org/documentation/)
- [Apache Iceberg Documentation](https://iceberg.apache.org/)
- [Google Cloud Dataflow](https://cloud.google.com/dataflow/docs)
- [Lambda Architecture Pattern](https://en.wikipedia.org/wiki/Lambda_architecture)

---

## 🤝 Contributing

Found an issue or want to improve this project?
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

This project is part of the GCP Data Engineering Mini Projects series.
Use for learning and educational purposes.

---

**⭐ Don't forget to star this repository if it helped you learn!**