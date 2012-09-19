-- Misc ETL queries.

-- After loading TSV data into data_raw table:
-- Convert numeric sample values, ignore others.
-- Then update sample sequence tables.
CREATE OR REPLACE FUNCTION etl_load_raw_data() -- (TIMESTAMP, TIMESTAMP)
RETURNS void LANGUAGE 'sql'
AS $$
-- numRowsData INTEGER;
-- numRowsSequence INTEGER;
-- numRowsSequenceRequestDelay INTEGER;
TRUNCATE data;
INSERT INTO data 
  SELECT envid, streamid, "timestamp", 
    (CASE 
      WHEN value ~ E'^ *[+-]?(?:\\d+(?:\\.\\d+)?|\\d\\.\\d+[eE]-\\d+) *$' THEN CAST(value AS DOUBLE PRECISION) 
      ELSE null 
    END) 
  FROM data_raw;
  -- WHERE timestamp>=$1 AND timestamp<$2;
-- GET DIAGNOSTICS numRowsData = ROW_COUNT;

TRUNCATE sequence;
INSERT INTO sequence(envid, streamid, timestamp) 
  SELECT envid, streamid, timestamp 
  FROM data 
  -- WHERE timestamp>=$1 AND timestamp<$2
  ORDER BY envid, streamid, timestamp;
-- GET DIAGNOSTICS numRowsSequence = ROW_COUNT;

TRUNCATE sequence_request_delay;
INSERT INTO sequence_request_delay(envid, streamid, seqid, timestamp, delay) 
  SELECT a.envid, a.streamid, b.id, b.timestamp, (b.timestamp-a.timestamp) 
  FROM sequence a JOIN sequence b ON (a.id+1=b.id) 
  WHERE a.envid=b.envid 
  AND a.streamid=b.streamid;
  -- AND b.timestamp>=$1 AND b.timestamp<$2;
-- GET DIAGNOSTICS numRowsSequenceRequestDelay = ROW_COUNT;

-- RETURN (numRowsData, numRowsSequence, numRowsSequenceRequestDelay);
$$;
