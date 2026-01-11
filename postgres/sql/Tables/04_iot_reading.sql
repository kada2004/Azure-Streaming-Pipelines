CREATE TABLE IF NOT EXISTS public.iot_reading (
    iot_reading_id BIGSERIAL,
    event_time     TIMESTAMPTZ NOT NULL,

    location_id    BIGINT NULL,  -- nullable by design

    temperature    DECIMAL(5,2),
    humidity       DECIMAL(5,2),
    water_level    DECIMAL(5,2),
    nitrogen       DECIMAL(5,2),
    phosphorus     DECIMAL(5,2),
    potassium      DECIMAL(5,2),

    CONSTRAINT fk_iot_location
        FOREIGN KEY (location_id)
        REFERENCES public.location(location_id),

    PRIMARY KEY (iot_reading_id, event_time)
);


SELECT create_hypertable(
    'public.iot_reading',
    'event_time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_iot_location
    ON public.iot_reading (location_id);
