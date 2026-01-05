IF OBJECT_ID('dbo.vw_iot_raw', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_iot_raw');
END;
GO

CREATE VIEW dbo.vw_iot_raw
AS
SELECT
    JSON_VALUE(raw_json, '$.event_id')                                      AS event_id,
    CAST(JSON_VALUE(raw_json, '$.event_time') AS datetime2)                 AS event_time,
    CAST(JSON_VALUE(raw_json, '$.payload.measurement_time') AS datetime2)   AS measurement_time,
    CAST(JSON_VALUE(raw_json, '$.payload.temperature') AS int)              AS temperature,
    CAST(JSON_VALUE(raw_json, '$.payload.humidity') AS int)                 AS humidity,
    CAST(JSON_VALUE(raw_json, '$.payload.water_level') AS int)              AS water_level,
    CAST(JSON_VALUE(raw_json, '$.payload.nitrogen') AS int)                 AS nitrogen,
    CAST(JSON_VALUE(raw_json, '$.payload.phosphorus') AS int)               AS phosphorus,
    CAST(JSON_VALUE(raw_json, '$.payload.potassium') AS int)                AS potassium,
    CAST(JSON_VALUE(raw_json, '$.payload.fan_actuator_off') AS bit)          AS fan_actuator_off,
    CAST(JSON_VALUE(raw_json, '$.payload.fan_actuator_on') AS bit)           AS fan_actuator_on,
    CAST(JSON_VALUE(raw_json, '$.payload.watering_pump_off') AS bit)         AS watering_pump_off,
    CAST(JSON_VALUE(raw_json, '$.payload.watering_pump_on') AS bit)          AS watering_pump_on,
    CAST(JSON_VALUE(raw_json, '$.payload.water_pump_off') AS bit)            AS water_pump_off,
    CAST(JSON_VALUE(raw_json, '$.payload.water_pump_on') AS bit)             AS water_pump_on
FROM dbo.iot_raw_ext;