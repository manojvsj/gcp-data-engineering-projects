# gcloud-workflow

## Overview
This project orchestrates a workflow using Google Cloud services, including Google Cloud Storage (GCS), DataProc, BigLake, and BigQuery. The application is designed to manage data operations seamlessly across these platforms.

## Project Structure
```
gcloud-workflow
├── src
│   ├── main.py                # Entry point of the application
│   ├── gcs
│   │   └── gcs_operations.py   # Functions for GCS operations
│   ├── dataproc
│   │   └── dataproc_operations.py # Functions for DataProc job management
│   ├── biglake
│   │   └── biglake_operations.py  # Functions for BigLake table management
│   ├── bigquery
│   │   └── bigquery_operations.py  # Functions for BigQuery table management
│   └── types
│       └── index.py            # Data types and models
├── requirements.txt            # Project dependencies
├── config
│   └── config.yaml             # Configuration settings
└── README.md                   # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd gcloud-workflow
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your Google Cloud credentials and settings in `config/config.yaml`.

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Workflow Description
The application performs the following operations:
- Uploads and downloads files to/from a GCS bucket.
- Manages DataProc jobs for data processing tasks.
- Interacts with BigLake tables for data storage and retrieval.
- Manages BigQuery internal tables for analytics and reporting.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.