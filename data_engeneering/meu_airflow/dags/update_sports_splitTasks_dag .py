from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import io
import json
from minio import Minio
from minio.error import S3Error
from airflow.models.variable import Variable

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

BUCKET_NAME = "landing-zone-integrated"
FILE_NAME = "availablesports.json"

def validate_variables():
    required_vars = ["MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_SECURE"]
    for var in required_vars:
        if not Variable.get(var, None):
            raise ValueError(f"Missing required Airflow Variable: {var}")

def fetch_sports_data(ti):
    url = "https://www.openligadb.de/api/getAvailableSports"
    response = requests.get(url)
    response.raise_for_status()
    new_data = response.json()
    ti.xcom_push(key='new_data', value=new_data)

def download_existing_file(ti):
    MINIO_ENDPOINT = Variable.get("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")
    SECURE = Variable.get("MINIO_SECURE", "False").lower() == "true"

    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=SECURE
    )

    try:
        current_obj = client.get_object(BUCKET_NAME, FILE_NAME)
        current_data = json.load(current_obj)
        current_obj.close()
    except S3Error:
        current_data = None  # Means first run or file missing
    
    ti.xcom_push(key='current_data', value=current_data)

def compare_sports_data(ti):
    new_data = ti.xcom_pull(key='new_data')
    current_data = ti.xcom_pull(key='current_data')
    if new_data == current_data:
        print("No changes detected.")
        return False  # no update needed
    else:
        print("Changes detected, will update.")
        return True

def upload_new_file(ti):
    update_needed = ti.xcom_pull(task_ids='compare_sports_data', key='return_value')
    if not update_needed:
        print("Skipping upload since no changes.")
        return
    
    new_data = ti.xcom_pull(key='new_data')
    new_data_bytes = json.dumps(new_data, indent=2).encode("utf-8")
    
    MINIO_ENDPOINT = Variable.get("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = Variable.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = Variable.get("MINIO_SECRET_KEY")
    SECURE = Variable.get("MINIO_SECURE", "False").lower() == "true"
    
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=SECURE
    )

    client.put_object(
        BUCKET_NAME,
        FILE_NAME,
        io.BytesIO(new_data_bytes),
        length=len(new_data_bytes),
        content_type="application/json"
    )
    print("File updated successfully.")

with DAG(
    dag_id='check_and_update_sports_splitTasks_dag',
    default_args=default_args,
    start_date=datetime(2025, 7, 16),
    schedule='@weekly',
    catchup=False,
    tags=['minio', 'sports', 'update']
) as dag:

    validate_variables_task = PythonOperator(
        task_id='validate_variables',
        python_callable=validate_variables
    )

    fetch_sports_task = PythonOperator(
        task_id='fetch_sports_data',
        python_callable=fetch_sports_data
    )

    download_file_task = PythonOperator(
        task_id='download_existing_file',
        python_callable=download_existing_file
    )

    compare_task = PythonOperator(
        task_id='compare_sports_data',
        python_callable=compare_sports_data
    )

    upload_task = PythonOperator(
        task_id='upload_new_file',
        python_callable=upload_new_file
    )

    validate_variables_task >> fetch_sports_task >> download_file_task >> compare_task >> upload_task
