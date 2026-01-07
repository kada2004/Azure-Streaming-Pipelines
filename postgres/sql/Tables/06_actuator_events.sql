CREATE TABLE IF NOT EXISTS public.actuator_event (
    actuator_event_id BIGSERIAL,
    event_time        TIMESTAMPTZ NOT NULL,

    actuator_id       BIGINT NOT NULL,
    state             BOOLEAN,      -- TRUE = ON, FALSE = OFF
    source            TEXT,         -- manual / automatic

    CONSTRAINT fk_actuator
        FOREIGN KEY (actuator_id)
        REFERENCES public.actuator(actuator_id),

    PRIMARY KEY (actuator_event_id, event_time)
);

SELECT create_hypertable(
    'public.actuator_event',
    'event_time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_actuator_event_actuator
    ON public.actuator_event (actuator_id);
