-- TOOLS

CREATE OR REPLACE FUNCTION array_sort (ANYARRAY)
RETURNS ANYARRAY LANGUAGE SQL
AS $$
SELECT ARRAY(
    SELECT $1[s.i] AS "foo"
    FROM
        generate_series(array_lower($1,1), array_upper($1,1)) AS s(i)
    ORDER BY foo
);
$$;

-- MEDIAN(x) FUNCTION

CREATE OR REPLACE FUNCTION median_row_fn(ANYARRAY, ANYELEMENT) RETURNS ANYARRAY AS $$
    SELECT array_sort($1 || $2);
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION median_final_fn(ANYARRAY) RETURNS ANYELEMENT AS $$
    SELECT CASE (mod(array_len, 2))
        WHEN 0 THEN (val[array_len / 2] + $1[array_len / 2 + 1]) / 2
        WHEN 1 THEN (val[array_len / 2 + 1])
    END
    FROM (SELECT array_upper($1, 1) as array_len, array_sort($1) as val) t1
$$ LANGUAGE SQL;

CREATE AGGREGATE median(ANYELEMENT) (
    sfunc = median_row_fn,
    finalfunc = median_final_fn,
    stype = ANYARRAY, 
    initcond = '{}'
);
