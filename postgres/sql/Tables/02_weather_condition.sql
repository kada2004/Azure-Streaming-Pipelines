CREATE TABLE IF NOT EXISTS public.weather_condition (
    condition_id INT PRIMARY KEY,     -- from API (e.g. 803)
    main         TEXT,
    description  TEXT,
    icon         TEXT
);
