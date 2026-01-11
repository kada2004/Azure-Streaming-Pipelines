CREATE UNIQUE INDEX IF NOT EXISTS uq_iot_dedup
ON public.iot_reading (event_time, location_id);

CREATE INDEX IF NOT EXISTS idx_iot_location
ON public.iot_reading (location_id);
