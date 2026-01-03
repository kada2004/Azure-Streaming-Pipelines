CREATE EXTERNAL DATA SOURCE IOT_ADLS
WITH (
    LOCATION = 'https://stdatastorequality.dfs.core.windows.net/iot-stream',
    CREDENTIAL = SynapseMI
);
