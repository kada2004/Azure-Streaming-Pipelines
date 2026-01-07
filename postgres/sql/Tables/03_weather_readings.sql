CREATE TABLE IF NOT EXISTS public.weather_reading (
    weather_reading_id BIGSERIAL,
    event_time         TIMESTAMPTZ NOT NULL,

    location_id        BIGINT NOT NULL,
    condition_id       INT NOT NULL,

    temperature        DECIMAL(5,2),
    feels_like         DECIMAL(5,2),
    pressure           INT,
    humidity           INT,
    wind_speed         DECIMAL(5,2),
    wind_deg           INT,
    visibility         INT,
    cloudiness         INT,

    CONSTRAINT fk_weather_location
        FOREIGN KEY (location_id)
        REFERENCES public.location(location_id),

    CONSTRAINT fk_weather_condition
        FOREIGN KEY (condition_id)
        REFERENCES public.weather_condition(condition_id),

    PRIMARY KEY (weather_reading_id, event_time)
);

SELECT create_hypertable(
    'public.weather_reading',
    'event_time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_weather_location
    ON public.weather_reading (location_id);

CREATE INDEX IF NOT EXISTS idx_weather_condition
    ON public.weather_reading (condition_id);
