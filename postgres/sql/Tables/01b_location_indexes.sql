CREATE UNIQUE INDEX IF NOT EXISTS uq_location_city_country
ON public.location (city_name, country_code);
