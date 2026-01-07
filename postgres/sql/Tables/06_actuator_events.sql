CREATE TABLE IF NOT EXISTS actuator_event (
    actuator_event_id BIGSERIAL,
    event_time        TIMESTAMPTZ NOT NULL,
    actuator_id       BIGINT REFERENCES actuator,
    state             BOOLEAN, -- ON / OFF
    source            TEXT,    -- manual / automatic
    PRIMARY KEY (actuator_event_id, event_time)
);

SELECT create_hypertable('actuator_event','event_time');
