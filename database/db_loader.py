from pyspark.sql import SparkSession

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

    parquet_path = f"gs://{GCS_BUCKET}/processed/seismic/"
    df = spark.read.parquet(parquet_path)
    df = df.dropDuplicates(["id"])

    df = df.select("id", "magnitude", "place", "event_time", "longitude", "latitude", "depth")

    print(f"Records found: {df.count()}")
    df.show(truncate=False)

    df.write \
        .format("jdbc") \
        .option("url", JDBC_URL) \
        .option("dbtable", "seismic_events") \
        .option("user", DB_USER) \
        .option("password", DB_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .option("stringtype", "unspecified") \
        .mode("append") \
        .save()

    print("Data loaded to Cloud SQL!")

if __name__ == "__main__":
    run()