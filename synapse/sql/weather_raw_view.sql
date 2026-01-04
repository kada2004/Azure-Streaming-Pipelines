CREATE OR ALTER VIEW vw_weather_raw
AS
SELECT
    JSON_VALUE(doc, '$.event_id')                        AS event_id,
    CAST(JSON_VALUE(doc, '$.event_time') AS datetime2)   AS event_time,
    JSON_VALUE(doc, '$.payload.name')                    AS city_name,
    JSON_VALUE(doc, '$.payload.sys.country')             AS country,
    CAST(JSON_VALUE(doc, '$.payload.coord.lat') AS decimal(9,6)) AS latitude,
    CAST(JSON_VALUE(doc, '$.payload.coord.lon') AS decimal(9,6)) AS longitude,
    JSON_VALUE(doc, '$.payload.weather[0].main')         AS weather_main,
    JSON_VALUE(doc, '$.payload.weather[0].description')  AS weather_description,
    CAST(JSON_VALUE(doc, '$.payload.main.temp') AS decimal(5,2)) - 273.15 AS temperature_c,
    CAST(JSON_VALUE(doc, '$.payload.main.humidity') AS int) AS humidity,
    CAST(JSON_VALUE(doc, '$.payload.main.pressure') AS int) AS pressure,
    CAST(JSON_VALUE(doc, '$.payload.wind.speed') AS decimal(5,2)) AS wind_speed,
    CAST(JSON_VALUE(doc, '$.payload.timezone') AS int)    AS timezone
FROM
    OPENROWSET(
        BULK 'WEATHER/*.json',
        DATA_SOURCE = 'WEATHER_ADLS',
        FORMAT = 'CSV',
        FIELDTERMINATOR = '0x0b',
        FIELDQUOTE = '0x0b'
    ) WITH (doc varchar(max)) AS rows;
