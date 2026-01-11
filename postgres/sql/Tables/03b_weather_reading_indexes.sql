CREATE INDEX IF NOT EXISTS idx_weather_location
ON public.weather_reading (location_id);

CREATE INDEX IF NOT EXISTS idx_weather_condition
ON public.weather_reading (weather_condition_id);
