import duckdb
import os
from dotenv import load_dotenv

#duckdb foi instalado no venv, dotoenv tambem  

# Carrega variáveis do .env
load_dotenv()

# Configura DuckDB com as credenciais
duckdb.sql(f"""
    CREATE SECRET minio_creds (
        TYPE S3,
        KEY_ID '{os.getenv("MINIO_ACCESS_KEY")}',
        SECRET '{os.getenv("MINIO_SECRET_KEY")}',
        REGION 'eu-central-1'
    )
""")

duckdb.sql(f"SET s3_endpoint='{os.getenv('MINIO_ENDPOINT')}'")
duckdb.sql("SET s3_use_ssl=false")
duckdb.sql("SET s3_url_style='path'")

# Consulta o arquivo no MinIO
df = duckdb.sql(f"""
    SELECT * 
    FROM read_csv_auto('s3://{os.getenv("MINIO_BUCKET")}/caminho/arquivo.csv')
    WHERE valor = 100
""").fetchdf()

print(df)
