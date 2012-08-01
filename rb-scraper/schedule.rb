#!/usr/bin/env ruby
#
# Created by martind on 2012-07-18.

require 'pg'
require_relative 'env'

@prefs = {
}

# ========
# = main =
# ========

conn = PGconn.open(
	:dbname => @env[:dbname], 
	:user => @env[:user], 
	:password => @env[:password])

res = conn.exec('SELECT id FROM environments ORDER BY id')
environments = {}
idx = 0
res.each do |row|
	environments[idx / 100] ||= []
	environments[idx / 100] << row['id']
	idx += 1
end

environments.values.each do |batch|
	res = conn.exec('INSERT INTO requests(envid, scheduleid) 
		SELECT e.id, s.id 
		FROM environments e 
		CROSS JOIN schedule s 
		LEFT OUTER JOIN requests r ON (r.envid=e.id and r.scheduleid=s.id)
		WHERE s.request
		AND e.created<=endtime
		AND e.updated>=starttime
		AND r.envid IS NULL
		AND e.id IN (' + batch.join(', ') + ');')
	print "."
end

puts
puts "Scheduled requests for #{res.size} environments."

conn.close
