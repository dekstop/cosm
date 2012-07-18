CREATE TABLE data_raw (
    envid       INTEGER NOT NULL,
    streamid    TEXT NOT NULL,
    timestamp   TIMESTAMP NOT NULL,
    value       TEXT NOT NULL
);

CREATE TABLE data (
    envid       INTEGER NOT NULL,
    streamid    TEXT NOT NULL,
    timestamp   TIMESTAMP NOT NULL,
    value       REAL
);

CREATE INDEX idx_data_envid_streamid_timestamp ON data USING btree (envid, streamid, "timestamp");
CREATE INDEX idx_data_timestamp ON data(timestamp);
