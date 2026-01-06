IF OBJECT_ID('dbo.vw_soil_humidity_over_time', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_soil_humidity_over_time');
END;
GO

CREATE VIEW dbo.vw_soil_humidity_over_time
AS
SELECT
    CAST(JSON_VALUE(raw_json, '$.payload.measurement_time') AS datetime2) AS measurement_time,
    CAST(JSON_VALUE(raw_json, '$.payload.humidity') AS int)              AS humidity
FROM dbo.iot_raw_ext
WHERE JSON_VALUE(raw_json, '$.event_type') = 'iot';
