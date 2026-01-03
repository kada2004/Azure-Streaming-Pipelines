IF NOT EXISTS (
    SELECT 1
    FROM sys.external_data_sources
    WHERE name = 'IOT_ADLS'
)
BEGIN
    CREATE EXTERNAL DATA SOURCE IOT_ADLS
    WITH (
        LOCATION = 'https://stdatastorequality.dfs.core.windows.net/iot-stream',
        CREDENTIAL = SynapseMI
    );
END;
