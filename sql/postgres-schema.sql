CREATE TABLE data (
    envid       INTEGER NOT NULL,
    streamid    INTEGER NOT NULL,
    timestamp   TIMESTAMP NOT NULL,
    value       REAL NOT NULL,
    UNIQUE(envid, streamid, timestamp)
);
