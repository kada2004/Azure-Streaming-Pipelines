CREATE TABLE IF NOT EXISTS weather_reading (
    weather_reading_id BIGSERIAL,
    event_time         TIMESTAMPTZ NOT NULL,
    location_id        BIGINT REFERENCES location,
    temperature        DECIMAL(5,2),
    feels_like         DECIMAL(5,2),
    pressure           INT,
    humidity           INT,
    wind_speed         DECIMAL(5,2),
    wind_deg           INT,
    visibility         INT,
    cloudiness         INT,
    condition_id       INT REFERENCES weather_condition,
    PRIMARY KEY (weather_reading_id, event_time)
);

SELECT create_hypertable('weather_reading','event_time');
