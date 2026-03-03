CREATE TABLE IF NOT EXISTS seismic_events (
    id VARCHAR(50) PRIMARY KEY,
    magnitude FLOAT,
    place VARCHAR(255),
    event_time TIMESTAMP,
    longitude FLOAT,
    latitude FLOAT,
    depth FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_time ON seismic_events(event_time);
CREATE INDEX IF NOT EXISTS idx_magnitude ON seismic_events(magnitude);