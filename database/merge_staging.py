import psycopg2

conn = psycopg2.connect(
    host="10.24.96.3",
    dbname="seismic_db",
    user="postgres",
    password="Project@2026"
)
cur = conn.cursor()
cur.execute("""
    INSERT INTO seismic_events (id, magnitude, place, event_time, longitude, latitude, depth)
    SELECT id, magnitude, place, event_time, longitude, latitude, depth
    FROM seismic_staging
    ON CONFLICT (id) DO NOTHING
""")
cur.execute("TRUNCATE TABLE seismic_staging")
conn.commit()
print(f"Rows inserted: {cur.rowcount}")
cur.close()
conn.close()
print("Merge complete!")
