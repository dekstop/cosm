CREATE TABLE sequence (
  id          SERIAL PRIMARY KEY,
  streamid    INTEGER NOT NULL,
  updated     TIMESTAMP NOT NULL
);

CREATE TABLE sequence_request_delay (
  streamid    INTEGER NOT NULL,
  seqid       INTEGER NOT NULL,
  updated     TIMESTAMP NOT NULL,
  delay       INTERVAL NOT NULL
);

CREATE INDEX idx_sequence_request_delay_updated ON sequence_request_delay(updated);
