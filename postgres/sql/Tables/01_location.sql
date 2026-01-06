CREATE TABLE IF NOT EXISTS location (
    location_id      BIGSERIAL PRIMARY KEY,
    city_name        TEXT,
    country_code     TEXT,
    latitude         DECIMAL(9,6),
    longitude        DECIMAL(9,6),
    timezone_offset  INT
);
