CREATE OR ALTER VIEW vw_iot_raw
AS
SELECT
    CAST(SUBSTRING(value,1,19) AS datetime2) AS measurement_time,
    CAST(PARSENAME(REPLACE(value, ',', '.'), 11) AS int) AS temperature,
    CAST(PARSENAME(REPLACE(value, ',', '.'), 10) AS int) AS humidity,
    CAST(PARSENAME(REPLACE(value, ',', '.'), 9) AS int)  AS water_level,
    CAST(PARSENAME(REPLACE(value, ',', '.'), 8) AS int)  AS nitrogen,
    CAST(PARSENAME(REPLACE(value, ',', '.'), 7) AS int)  AS phosphorus,
    CAST(PARSENAME(REPLACE(value, ',', '.'), 6) AS int)  AS potassium
FROM (
    SELECT
        JSON_VALUE(doc,'$.payload."date,tempreature,humidity,water_level,N,P,K,Fan_actuator_OFF,Fan_actuator_ON,Watering_plant_pump_OFF,Watering_plant_pump_ON,Water_pump_actuator_OFF,Water_pump_actuator_ON"') AS value
    FROM
        OPENROWSET(
            BULK 'IOT/*.json',
            DATA_SOURCE = 'IOT_ADLS',
            FORMAT = 'CSV',
            FIELDTERMINATOR = '0x0b',
            FIELDQUOTE = '0x0b'
        ) WITH (doc varchar(max)) AS rows
) t;