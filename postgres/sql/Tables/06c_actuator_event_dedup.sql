CREATE UNIQUE INDEX IF NOT EXISTS uq_actuator_event_dedup
ON public.actuator_event (event_time, actuator_id);