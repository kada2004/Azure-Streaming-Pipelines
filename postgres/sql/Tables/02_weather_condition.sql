CREATE TABLE IF NOT EXISTS public.weather_condition (
    weather_condition_id BIGSERIAL PRIMARY KEY,

    external_condition_id INT NOT NULL,   -- weather.id from payload
    main                  TEXT,
    description           TEXT,
    icon                  TEXT
);