#!/usr/bin/env ruby
#
#  Created by martind on 2012-07-18.

require 'pg'
require "net/http"
require "uri"
require 'env'

@prefs = {
	:dateformat => '%Y-%m-%dT%H:%M:%S'
}

# ========
# = main =
# ========

conn = PGconn.open(
	:dbname => @env[:dbname], 
	:login=> @env[:login], 
	:password => @env[:password])

res  = conn.exec('SELECT 1 AS a, 2 AS b, NULL AS c')
puts res.getvalue(0,0) # '1'
puts res[0]['b']       # '2'
puts res[0]['c']       # nil

res = conn.exec('SELECT envid, starttime, endtime 
	FROM schedule s 
	JOIN requests r ON s.id=r.scheduleid 
	JOIN environments e ON r.envid=e.id 
	WHERE s.request
	AND e.created>=r.starttime
	AND (r.success IS NULL OR r.success=false)
	ORDER BY envid, starttime;')

res.each do |row|
	envid = row[0]
	starttime = (row[1]).strftime(@prefs[:dateformat])
	endtime = (row[2]).strftime(@prefs[:dateformat])

	puts "#{envid}: #{starttime} - #{endtime}"
	uri = URI.parse("https://api.cosm.com/v2/feeds/#{envid}.xml?key=#{@env[:apikey]}&start=#{starttime}&end=#{endtime}")
	http = Net::HTTP.new(uri.host, uri.port)
	response = http.request(Net::HTTP::Get.new(uri.request_uri))
	
	if (response.code==200) then
		filename = "#{@env[:datadir]}/feed_history/#{starttime}/#{envid}.xml"
		puts filename
		File.open(File.expand_path(filename), 'w') {|f| f.write(response.body) }

		conn.exec('UPDATE requests 
			SET 
				lastrequest=now(), 
				success=true, 
				httpstatus=$1', 
			[response.status])
	else
		puts "#{response.code}: #{response.message}"
		conn.exec('UPDATE requests 
			SET 
				lastrequest=now(), 
				success=false, 
				httpstatus=$1,
				response=$2', 
			[response.status, response.body])
	end
	
	sleep 1.5
end

conn.close
