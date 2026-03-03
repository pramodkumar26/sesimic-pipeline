from pyspark.sql import SparkSession
from datetime import datetime



GCS_BUCKET = "sesimic-pipeline-raw-data"
DB_HOST = "10.24.96.3"
DB_NAME = "seismic_db"
DB_USER = "postgres"
DB_PASSWORD = "Project@2026"
JDBC_URL = f"jdbc:postgresql://{DB_HOST}:5432/{DB_NAME}"

def run():
    spark = SparkSession.builder \
        .appName("SeismicDBLoader") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    today = datetime.utcnow().strftime("%Y%m%d")
    parquet_path = f"gs://{GCS_BUCKET}/processed/seismic/"
    df = spark.read.parquet(parquet_path)
    df = df.dropDuplicates(["id"])

    print(f"Records found: {df.count()}")
    df.show(truncate=False)

    rows = df.collect()
    engine = create_db_engine()
    create_table(engine)
    load_data(engine, rows)
    print("Data loaded to Cloud SQL!")

if __name__ == "__main__":
    run()