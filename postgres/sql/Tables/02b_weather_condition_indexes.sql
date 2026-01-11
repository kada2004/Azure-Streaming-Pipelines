CREATE UNIQUE INDEX IF NOT EXISTS uq_weather_condition_natural
ON public.weather_condition (external_condition_id, icon);
