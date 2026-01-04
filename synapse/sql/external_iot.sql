IF OBJECT_ID('dbo.iot_raw_ext') IS NULL
BEGIN
    CREATE EXTERNAL TABLE dbo.iot_raw_ext (
        raw_json varchar(max)
    )
    WITH (
        LOCATION = '/IOT/',
        DATA_SOURCE = IOT_ADLS,
        FILE_FORMAT = JsonLineFormat
    );
END;
