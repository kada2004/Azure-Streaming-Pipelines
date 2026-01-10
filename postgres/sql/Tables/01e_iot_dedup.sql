CREATE UNIQUE INDEX IF NOT EXISTS uq_iot_dedup
ON public.iot_reading (event_time, location_id);
