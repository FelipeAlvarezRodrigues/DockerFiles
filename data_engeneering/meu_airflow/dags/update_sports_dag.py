from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import requests
import io
import json
from minio import Minio
from minio.error import S3Error
from airflow.models.variable import Variable

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def check_and_update_sports():
    # 🔐 Load variables from Airflow UI (Admin > Variables)
    required_vars = ["MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_SECURE"]
    for var in required_vars:
        if not Variable.get(var,None):
            raise ValueError(f"❌ Missing required Airflow Variable: {var}")
        
    # Load MinIO connection details    
    MINIO_ENDPOINT = Variable.get("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")
    BUCKET_NAME = "landing-zone-integrated"
    SECURE = Variable.get("MINIO_SECURE", "False").lower() == "true"
    FILE_NAME = "availablesports.json"

    # Connect to MinIO
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=SECURE
    )

    # Get latest sports from API
    url = "https://www.openligadb.de/api/getAvailableSports"
    response = requests.get(url)
    response.raise_for_status()
    new_data = response.json()
    new_data_bytes = json.dumps(new_data, indent=2).encode("utf-8")

    # Try to get current file from MinIO
    try:
        current_obj = client.get_object(BUCKET_NAME, FILE_NAME)
        current_data = json.load(current_obj)
        current_obj.close()

        # Compare old vs new
        if current_data == new_data:
            print("✅ No changes in sports list. Skipping update.")
            return
        else:
            print("🔄 Changes detected in sports list. Updating MinIO...")

    except S3Error as e:
        print(f"⚠️ Could not fetch current file (might be first run): {e}")
        print("Uploading new file...")

    # Upload updated file
    client.put_object(
        BUCKET_NAME,
        FILE_NAME,
        io.BytesIO(new_data_bytes),
        length=len(new_data_bytes),
        content_type="application/json"
    )
    print("✅ File updated successfully.")

with DAG(
    dag_id='check_and_update_sports_dag',
    default_args=default_args,
    start_date=datetime(2025, 7, 16),
    schedule='@weekly',  # every week
    catchup=False,
    tags=['minio', 'sports', 'update']
) as dag:

    check_sports = PythonOperator(
        task_id='check_and_update_sports',
        python_callable=check_and_update_sports
    )

    check_sports
