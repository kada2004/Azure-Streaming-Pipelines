IF OBJECT_ID('dbo.vw_weather_raw', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_weather_raw');
END;
GO

CREATE VIEW dbo.vw_weather_raw
AS
SELECT
    JSON_VALUE(raw_json, '$.event_id') AS event_id,
    CAST(JSON_VALUE(raw_json, '$.event_time') AS datetime2) AS event_time,
    JSON_VALUE(raw_json, '$.payload.name') AS city_name,
    JSON_VALUE(raw_json, '$.payload.sys.country') AS country,
    CAST(JSON_VALUE(raw_json, '$.payload.coord.lat') AS decimal(9,6)) AS latitude,
    CAST(JSON_VALUE(raw_json, '$.payload.coord.lon') AS decimal(9,6)) AS longitude,
    JSON_VALUE(raw_json, '$.payload.weather[0].main') AS weather_main,
    JSON_VALUE(raw_json, '$.payload.weather[0].description') AS weather_description,
    CAST(JSON_VALUE(raw_json, '$.payload.main.temp') AS decimal(6,2)) - 273.15 AS temperature_c,
    CAST(JSON_VALUE(raw_json, '$.payload.main.humidity') AS int) AS humidity,
    CAST(JSON_VALUE(raw_json, '$.payload.main.pressure') AS int) AS pressure,
    CAST(JSON_VALUE(raw_json, '$.payload.wind.speed') AS decimal(5,2)) AS wind_speed,
    CAST(JSON_VALUE(raw_json, '$.payload.timezone') AS int) AS timezone
FROM dbo.weather_raw_ext;
