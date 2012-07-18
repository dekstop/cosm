#!/usr/bin/env ruby
#
# Created by martind on 2012-07-18.

require 'pg'
require 'env'

@prefs = {
}

# ========
# = main =
# ========

conn = PGconn.open(
	:dbname => @env[:dbname], 
	:login=> @env[:login], 
	:password => @env[:password])

res = conn.exec('INSERT INTO requests(envid, scheduleid) 
	SELECT e.id, s.id 
	FROM environments e 
	CROSS JOIN schedule s 
	LEFT OUTER JOIN requests r ON (r.envid=e.id, r.scheduleid=s.id)
	WHERE e.created>s.starttime
	AND r.envid IS NULL;')

conn.close
