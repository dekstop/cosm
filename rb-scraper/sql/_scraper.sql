-- Misc scraper control queries

Prepare a schedule for scraper requests:
update schedule set request=true where starttime>='2012-04-01' and starttime<'2012-05-01';

Request queue breakdown by status:
select now(), success, httpstatus, paused, count(*), max(lastrequest) as lastrequest from requests group by success, httpstatus, paused order by success, httpstatus, paused;

Request queue breakdown by date:
select to_char(starttime, 'YYYY-MM-DD') as date, count(*) from schedule s join requests r on s.id=r.scheduleid where success is null and paused=false group by date order by date;