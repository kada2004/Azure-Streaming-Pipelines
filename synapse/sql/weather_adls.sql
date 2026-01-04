IF NOT EXISTS (
    SELECT 1
    FROM sys.external_data_sources
    WHERE name = 'WEATHER_ADLS'
)
BEGIN
    CREATE EXTERNAL DATA SOURCE WEATHER_ADLS
    WITH (
        LOCATION = 'abfss://temperature@stdatastorequality.dfs.core.windows.net',
        CREDENTIAL = SynapseMI
    );
END;