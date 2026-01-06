CREATE TABLE location IF NOT EXISTS (
    location_id      BIGSERIAL PRIMARY KEY,
    city_name        TEXT,
    country_code     TEXT,
    latitude         DECIMAL(9,6),
    longitude        DECIMAL(9,6),
    timezone_offset  INT
);
