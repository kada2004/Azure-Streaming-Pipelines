IF NOT EXISTS (
    SELECT 1
    FROM sys.external_file_formats
    WHERE name = 'JsonLineFormat'
)
BEGIN
    CREATE EXTERNAL FILE FORMAT JsonLineFormat
    WITH (
        FORMAT_TYPE = DELIMITEDTEXT,
        FORMAT_OPTIONS (
            FIELD_TERMINATOR = '|',
            STRING_DELIMITER = '0x0b'
        )
    );
END;
