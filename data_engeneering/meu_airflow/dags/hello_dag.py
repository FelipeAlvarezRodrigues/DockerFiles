from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.decorators import task

# Criação da DAG
with DAG(
    dag_id="hello_dag",
    start_date=datetime(2025, 1, 1),
    schedule=None,  # substitui o antigo schedule_interval
    catchup=False,
    tags=["example"],
) as dag:

    @task
    def say_hello():
        print("Olá, mundo! DAG está funcionando corretamente.")

    # Task declarada e usada
    say_hello()
