CREATE TABLE sequence (
  id          SERIAL PRIMARY KEY,
  envid       INTEGER NOT NULL,
  streamid    TEXT NOT NULL,
  timestamp   TIMESTAMP NOT NULL
);

CREATE TABLE sequence_request_delay (
  envid       INTEGER NOT NULL,
  streamid    TEXT NOT NULL,
  seqid       INTEGER NOT NULL,
  timestamp   TIMESTAMP NOT NULL,
  delay       INTERVAL NOT NULL
);
