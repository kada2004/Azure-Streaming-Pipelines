IF OBJECT_ID('dbo.vw_iot_raw', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_iot_raw');
END;
GO

CREATE VIEW dbo.vw_iot_raw
AS
SELECT
    CAST(SUBSTRING(payload, 1, 19) AS datetime2) AS measurement_time,
    CAST(PARSENAME(REPLACE(payload, ',', '.'), 11) AS int) AS temperature,
    CAST(PARSENAME(REPLACE(payload, ',', '.'), 10) AS int) AS humidity,
    CAST(PARSENAME(REPLACE(payload, ',', '.'), 9)  AS int) AS water_level,
    CAST(PARSENAME(REPLACE(payload, ',', '.'), 8)  AS int) AS nitrogen,
    CAST(PARSENAME(REPLACE(payload, ',', '.'), 7)  AS int) AS phosphorus,
    CAST(PARSENAME(REPLACE(payload, ',', '.'), 6)  AS int) AS potassium
FROM (
    SELECT
        JSON_VALUE(
            raw_json,
            '$.payload."date,tempreature,humidity,water_level,N,P,K,Fan_actuator_OFF,Fan_actuator_ON,Watering_plant_pump_OFF,Watering_plant_pump_ON,Water_pump_actuator_OFF,Water_pump_actuator_ON"'
        ) AS payload
    FROM dbo.iot_raw_ext
) s;
