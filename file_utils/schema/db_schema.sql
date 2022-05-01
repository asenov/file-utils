CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_file_location TEXT NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    created_on DATETIME NOT NULL
);
CREATE TABLE file_chunks (
    file_id INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    chunk BLOB
);
CREATE INDEX idx_file_name ON files (file_name);
CREATE UNIQUE INDEX idx_file ON files (original_file_location, file_name);
CREATE INDEX idx_file_chunks ON file_chunks(file_id);
CREATE INDEX idx_file_chunk_id ON file_chunks(chunk_id);
CREATE VIEW v_files AS
SELECT f.*,
    f_size_mb AS fsize_mb
FROM files as f
    JOIN (
        SELECT file_id,
            (SUM(LENGTH(chunk)) / 1000000.0) as f_size_mb
        FROM file_chunks
        GROUP BY file_id
    ) as fc ON f.id = fc.file_id;