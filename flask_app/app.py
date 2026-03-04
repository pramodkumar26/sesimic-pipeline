import os
from flask import Flask, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "34.70.61.51")
DB_NAME = os.environ.get("DB_NAME", "seismic_db")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Project@2026")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10
    )

@app.route("/")
def index():
    return jsonify({"message": "Seismic Pipeline API", "status": "running"})

@app.route("/earthquakes")
def get_earthquakes():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM seismic_events ORDER BY event_time DESC LIMIT 100")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/earthquakes/recent")
def get_recent():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT * FROM seismic_events
        WHERE event_time >= NOW() - INTERVAL '24 hours'
        ORDER BY event_time DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/earthquakes/strong")
def get_strong():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT * FROM seismic_events
        WHERE magnitude >= 4.0
        ORDER BY magnitude DESC
        LIMIT 100
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/earthquakes/stats")
def get_stats():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            COUNT(*) as total_earthquakes,
            ROUND(AVG(magnitude)::numeric, 2) as avg_magnitude,
            MAX(magnitude) as max_magnitude,
            MIN(magnitude) as min_magnitude,
            MAX(event_time) as latest_event
        FROM seismic_events
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(dict(row))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)