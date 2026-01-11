CREATE TABLE public.actuator (
    actuator_id   BIGSERIAL PRIMARY KEY,
    actuator_name TEXT UNIQUE NOT NULL,
    actuator_type TEXT
);
