IF OBJECT_ID('dbo.vw_iot_weather_10min', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_iot_weather_10min');
END;
GO

CREATE VIEW dbo.vw_iot_weather_10min
AS
WITH iot AS (
    SELECT
        DATEADD(minute, (DATEDIFF(minute, 0, CAST(JSON_VALUE(raw_json, '$.payload.measurement_time') AS datetime2)) / 10) * 10, 0) AS bucket_10min,
        CAST(JSON_VALUE(raw_json, '$.payload.humidity') AS int)      AS soil_humidity,
        CAST(JSON_VALUE(raw_json, '$.payload.temperature') AS int)   AS soil_temperature_c,
        CAST(JSON_VALUE(raw_json, '$.payload.water_level') AS int)   AS water_level,
        CAST(JSON_VALUE(raw_json, '$.payload.nitrogen') AS int)      AS nitrogen,
        CAST(JSON_VALUE(raw_json, '$.payload.phosphorus') AS int)    AS phosphorus,
        CAST(JSON_VALUE(raw_json, '$.payload.potassium') AS int)     AS potassium
    FROM dbo.iot_raw_ext
    WHERE JSON_VALUE(raw_json, '$.event_type') = 'iot'
),
wx AS (
    SELECT
        DATEADD(minute, (DATEDIFF(minute, 0, CAST(JSON_VALUE(raw_json, '$.event_time') AS datetime2)) / 10) * 10, 0) AS bucket_10min,
        JSON_VALUE(raw_json, '$.payload.weather[0].main')            AS weather_main,
        JSON_VALUE(raw_json, '$.payload.weather[0].description')     AS weather_description,
        CAST(JSON_VALUE(raw_json, '$.payload.main.temp') AS decimal(6,2)) - 273.15 AS air_temperature_c
    FROM dbo.weather_raw_ext
    WHERE JSON_VALUE(raw_json, '$.event_type') = 'weather'
)
SELECT
    iot.bucket_10min AS time_bucket,
    iot.soil_humidity,
    iot.soil_temperature_c,
    iot.water_level,
    iot.nitrogen,
    iot.phosphorus,
    iot.potassium,
    wx.weather_main,
    wx.weather_description,
    wx.air_temperature_c
FROM iot
LEFT JOIN wx
    ON iot.bucket_10min = wx.bucket_10min;
