CREATE TABLE IF NOT EXISTS actuator (
    actuator_id  BIGSERIAL PRIMARY KEY,
    actuator_name TEXT UNIQUE,
    actuator_type TEXT
);
