CREATE TABLE schedule (
    id          SERIAL PRIMARY KEY,
    starttime   TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    endtime     TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    request     BOOLEAN NOT NULL DEFAULT false,
    UNIQUE(starttime, endtime)
);

CREATE TABLE environments (
    id          INTEGER NOT NULL,
    created     TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated     TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE requests (
    id          SERIAL PRIMARY KEY,
    envid       INTEGER NOT NULL,
    scheduleid  INTEGER NOT NULL,
    lastrequest TIMESTAMP WITHOUT TIME ZONE,
    success     BOOLEAN,
    httpstatus  INTEGER,
    response    TEXT,
    UNIQUE(envid, scheduleid)
);

