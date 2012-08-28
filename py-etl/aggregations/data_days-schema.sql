CREATE TABLE data_days (
  date        TEXT NOT NULL,
  streamid    INTEGER NOT NULL,
  count       INTEGER NOT NULL,
  min         NUMERIC,
  max         NUMERIC,
  mean        NUMERIC,
  median      NUMERIC,
  sd          NUMERIC
);

CREATE UNIQUE INDEX idx_data_days_date_streamid ON data_days(date, streamid);
CREATE UNIQUE INDEX idx_data_days_streamid_date ON data_days(streamid, date);

