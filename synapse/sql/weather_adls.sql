IF NOT EXISTS (
    SELECT 1
    FROM sys.external_data_sources
    WHERE name = 'WEATHER_ADLS'
)
BEGIN
    CREATE EXTERNAL DATA SOURCE WEATHER_ADLS
    WITH (
        LOCATION = 'https://stdatastorequality.dfs.core.windows.net/temperature',
        CREDENTIAL = SynapseMI
    );
END;
