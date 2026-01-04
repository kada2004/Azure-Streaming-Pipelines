IF OBJECT_ID('dbo.vw_iot_raw', 'V') IS NOT NULL
BEGIN
    EXEC('DROP VIEW dbo.vw_iot_raw');
END;

CREATE VIEW dbo.vw_iot_raw
AS
SELECT
    CAST(j.[0] AS datetime2) AS measurement_time,
    CAST(j.[1] AS int)       AS temperature,
    CAST(j.[2] AS int)       AS humidity,
    CAST(j.[3] AS int)       AS water_level,
    CAST(j.[4] AS int)       AS nitrogen,
    CAST(j.[5] AS int)       AS phosphorus,
    CAST(j.[6] AS int)       AS potassium
FROM dbo.iot_raw_ext t
CROSS APPLY OPENJSON(
    '["' + REPLACE(
        JSON_VALUE(
            t.raw_json,
            '$.payload."date,tempreature,humidity,water_level,N,P,K,Fan_actuator_OFF,Fan_actuator_ON,Watering_plant_pump_OFF,Watering_plant_pump_ON,Water_pump_actuator_OFF,Water_pump_actuator_ON"'
        ),
        ',', '","'
    ) + '"]'
)
WITH (
    [0] nvarchar(50),
    [1] nvarchar(50),
    [2] nvarchar(50),
    [3] nvarchar(50),
    [4] nvarchar(50),
    [5] nvarchar(50),
    [6] nvarchar(50)
) AS j;
