INSERT INTO data_days(date, count, min, max, mean, median, sd) SELECT TO_CHAR(updated, 'YYYY-MM-DD') AS date, streamid, count(*) AS count, min(value) AS min, max(value) AS max, avg(value) AS mean, median(value) AS median, stddev(value) AS sd FROM data GROUP BY date, streamid ORDER BY date, streamid;
-- In SQLite this would be: strftime('%Y-%m-%d', updated)
