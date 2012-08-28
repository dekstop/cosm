INSERT INTO sequence(streamid, updated) SELECT streamid, updated FROM data d ORDER BY streamid, updated;

INSERT INTO sequence_request_delay(streamid, seqid, updated, delay) SELECT a.streamid, b.id, b.updated, (b.updated-a.updated) FROM sequence a JOIN sequence b ON (a.id+1=b.id) WHERE a.streamid=b.streamid;
