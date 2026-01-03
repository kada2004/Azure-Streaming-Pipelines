CREATE EXTERNAL DATA SOURCE WEATHER_ADLS
WITH (
    LOCATION = 'https://stdatastorequality.dfs.core.windows.net/temperature',
    CREDENTIAL = SynapseMI
);
