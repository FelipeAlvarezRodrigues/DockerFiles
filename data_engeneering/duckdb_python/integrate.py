import requests
import pandas as pd
import os
from io import StringIO
from dotenv import load_dotenv
from minio import Minio

# Tenho que testar ainda nao testei

# 1. Configurações (via .env)
load_dotenv()
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("MINIO_BUCKET")

# 2. Pega dados da API (exemplo: JSONPlaceholder)
def fetch_api_data():
    url = "https://jsonplaceholder.typicode.com/users"  # API pública de teste
    response = requests.get(url)
    return response.json()

# 3. Salva no MinIO
def save_to_minio(data, filename, format="csv"):
    # Conecta ao MinIO
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS,
        secret_key=MINIO_SECRET,
        secure=False  # SSL off para localhost
    )
    
    # Cria o bucket se não existir
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
    
    # Converte dados
    df = pd.DataFrame(data)
    
    if format == "csv":
        csv_data = df.to_csv(index=False).encode("utf-8")
        client.put_object(
            BUCKET_NAME,
            f"api_data/{filename}.csv",
            data=StringIO(df.to_csv(index=False)),
            length=len(csv_data),
            content_type="application/csv"
        )
    elif format == "parquet":
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        client.put_object(
            BUCKET_NAME,
            f"api_data/{filename}.parquet",
            data=parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type="application/parquet"
        )

# Execução
if __name__ == "__main__":
    data = fetch_api_data()
    save_to_minio(data, "usuarios", format="csv")  # Altere para "parquet" se quiser
    print(f"Dados salvos em {BUCKET_NAME}/api_data/usuarios.csv")