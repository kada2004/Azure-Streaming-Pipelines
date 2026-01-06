IF OBJECT_ID('dbo.vw_npk_over_time', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_npk_over_time');
END;
GO

CREATE VIEW dbo.vw_npk_over_time
AS
SELECT
    CAST(JSON_VALUE(raw_json, '$.payload.measurement_time') AS datetime2) AS measurement_time,
    CAST(JSON_VALUE(raw_json, '$.payload.nitrogen') AS int)               AS nitrogen,
    CAST(JSON_VALUE(raw_json, '$.payload.phosphorus') AS int)             AS phosphorus,
    CAST(JSON_VALUE(raw_json, '$.payload.potassium') AS int)              AS potassium
FROM dbo.iot_raw_ext
WHERE JSON_VALUE(raw_json, '$.event_type') = 'iot';
