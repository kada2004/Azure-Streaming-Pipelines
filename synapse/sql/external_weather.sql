IF OBJECT_ID('dbo.weather_raw_ext') IS NULL
BEGIN
    CREATE EXTERNAL TABLE dbo.weather_raw_ext (
        raw_json varchar(max)
    )
    WITH (
        LOCATION = '/WEATHER/',
        DATA_SOURCE = WEATHER_ADLS,
        FILE_FORMAT = JsonLineFormat
    );
END;
