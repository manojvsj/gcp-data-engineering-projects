import functions_framework
import requests
from google.cloud import bigquery
from datetime import datetime

@functions_framework.http
def fetch_weather(request):
    """
    Cloud Function to fetch current weather from Open-Meteo API
    and insert data into BigQuery.
    """
    # Configuration
    latitude = 12.97
    longitude = 77.59
    project_id = "your-project-id"
    dataset_id = "weather_dt"
    table_id = "weather_snapshots"

    # Open-Meteo API URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather = data.get("current_weather", {})
        temperature = weather.get("temperature")
        windspeed = weather.get("windspeed")
        recorded_at = weather.get("time")
        fetched_at = datetime.utcnow().isoformat()

        if None in (temperature, windspeed, recorded_at):
            return ("Missing data in API response", 500)

        # Insert into BigQuery
        client = bigquery.Client()
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        rows = [{
            "temperature": temperature,
            "windspeed": windspeed,
            "recorded_at": recorded_at,
            "fetched_at": fetched_at
        }]

        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            return (f"BigQuery insert error: {errors}", 500)

        return ("Success", 200)

    except Exception as e:
        return (str(e), 500)