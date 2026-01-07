CREATE TABLE IF NOT EXISTS iot_reading (
    iot_reading_id BIGSERIAL,
    event_time     TIMESTAMPTZ NOT NULL,
    location_id    BIGINT REFERENCES location,
    temperature    DECIMAL(5,2),
    humidity       DECIMAL(5,2),
    water_level    DECIMAL(5,2),
    nitrogen       DECIMAL(5,2),
    phosphorus     DECIMAL(5,2),
    potassium      DECIMAL(5,2),
    PRIMARY KEY (iot_reading_id, event_time)
);

SELECT create_hypertable('iot_reading','event_time');
