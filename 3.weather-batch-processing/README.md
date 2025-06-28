# 🌤️ Project 3/50: Weather Data Pipeline on GCP

This project uses a Cloud Function and Cloud Scheduler to fetch live weather data every 15 minutes and insert it into BigQuery.

---

## 🛠️ Tools Used
- **Google Cloud Functions** (Python)
- **Cloud Scheduler** (cron-like scheduling)
- **BigQuery** (data storage)
- **Open-Meteo API** (weather source)

---

## 📁 Project Structure

```
weather-pipeline/
├── fetch_weather.py           # Cloud Function to fetch and write data
├── requirements.txt           # Python packages
├── deploy.sh                  # Deploys function + scheduler
├── cleanup.sh                 # Deletes all GCP resources
└── README.md
```

---

## 🚀 How It Works

1. `Cloud Scheduler` triggers every 15 minutes.
2. `Cloud Function` fetches weather data via API.
3. Parses and writes data to `BigQuery` table.
4. You get historical weather snapshots.

---

## ✅ Setup

1. Edit `deploy.sh` and replace:
   - `your-project-id`
   - `your_dataset`

2. Run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📦 Example Output in BigQuery

| temperature | windspeed | recorded_at         | fetched_at           |
|-------------|-----------|---------------------|----------------------|
| 28.5        | 10.8      | 2024-06-21T10:00:00Z | 2024-06-21T10:00:10Z |

---

## 🧹 Cleanup

To delete all deployed resources:

```bash
chmod +x cleanup.sh
./cleanup.sh
```

---

## 📌 Notes

- Uses Open-Meteo API (no API key required)
- Timestamp columns use UTC
- Scheduler time zone is set to Asia/Kolkata

---

Happy building ☁️