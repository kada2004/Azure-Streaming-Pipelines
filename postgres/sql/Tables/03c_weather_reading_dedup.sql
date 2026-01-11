CREATE UNIQUE INDEX IF NOT EXISTS uq_weather_dedup
ON public.weather_reading (event_time, location_id, weather_condition_id);
