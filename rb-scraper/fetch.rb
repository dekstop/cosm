#!/usr/bin/env ruby
#
#  Created by martind on 2012-07-18.

require 'fileutils'
require "net/http"
require 'pg'
require 'rubygems'
require 'time'
require "uri"
require_relative 'env'

require 'xray/thread_dump_signal_handler'

@prefs = {
	:cachedir => File.expand_path("#{@env[:datadir]}/feed_history"),
	:requests_per_minute => 80,
	:throttle_history_size => 100,
	:dateformat => '%Y-%m-%dT%H:%M:%S',
	:skip_when_file_exists => true
}

# A workaround for Ruby's lack of fractional sleep times.
# Keeps track of the last n timestamps and adjusts delays times accordingly.
class RequestThrottle

	def initialize(calls_per_minute, history_size=10)
		@calls_per_minute = calls_per_minute
		@call_times = []
		@history_size = history_size
	end

	# Call once per request to determine how long to sleep.
	def get_delay
		@call_times << Time.now
		if @call_times.size < 2 then
			return 0
		else
			@call_times.shift while @call_times.size > @history_size
			first = @call_times[0]
			last = @call_times[-1]

			expected = (@call_times.size / (@calls_per_minute / 60.0))
			actual = last - first # float: number of seconds
			delay = [0, expected-actual].max
			return delay
		end
	end
end

# ========
# = main =
# ========

throttle = RequestThrottle.new(@prefs[:requests_per_minute], @prefs[:throttle_history_size])

conn = PGconn.open(
	:dbname => @env[:dbname], 
	:user => @env[:user], 
	:password => @env[:password])

begin

	res = conn.exec('SELECT r.id as id, envid, starttime, endtime 
		FROM schedule s 
		JOIN requests r ON s.id=r.scheduleid 
		WHERE (r.success IS NULL OR (r.success=false AND r.httpstatus NOT IN(403, 404)))
		ORDER BY starttime, envid;')

	res.each do |row|
		rid = row['id']
		envid = row['envid']
		starttime = Time.parse(row['starttime']).strftime(@prefs[:dateformat])
		endtime = Time.parse(row['endtime']).strftime(@prefs[:dateformat])

		dir = "#{@prefs[:cachedir]}/#{starttime}"
		FileUtils.makedirs(dir)
		filename = "#{dir}/#{envid}.xml"
		
		puts "Feed #{envid}: #{filename}"
		
		if (@prefs[:skip_when_file_exists] && File.exists?(filename) && File.size(filename)>0) then
			puts "File already exists." 
			conn.exec('UPDATE requests 
				SET 
					lastrequest=now(), 
					success=true, 
					httpstatus=null,
					response=null
				WHERE id=$1', 
				[rid])
		else
			uri = URI.parse("http://api.cosm.com/v2/feeds/#{envid}.xml?key=#{@env[:apikey]}&start=#{starttime}&end=#{endtime}")
			http = Net::HTTP.new(uri.host, uri.port)

			do_retry = false
			num_retries_left = 3
			begin
				response = http.request(Net::HTTP::Get.new(uri.request_uri))
			rescue Timeout::Error
				num_retries_left -= 1
				if (num_retries_left > 0) then
					do_retry = true
					delay = Random.rand(20) + 1
					puts "Timout error, will try again in #{delay} seconds"
					sleep (delay)
				else 
					puts "Too many failed retries, terminating"
					exit 1
				end
			end while do_retry

			if (response.code.to_i==200) then
				File.open(filename, 'w') {|f| f.write(response.body) }

				conn.exec('UPDATE requests 
					SET 
						lastrequest=now(), 
						success=true, 
						httpstatus=$1,
						response=null
					WHERE id=$2', 
					[response.code, rid])
			else
				puts "#{response.code}: #{response.message}"
				conn.exec('UPDATE requests 
					SET 
						lastrequest=now(), 
						success=false, 
						httpstatus=$1,
						response=$2
					WHERE id=$3', 
					[response.code, response.body, rid])
			end
			
			#puts "Wait..."
			#sleep 1
			delay = throttle.get_delay
			if (delay > 0) then
				puts "Waiting: #{delay}"
				sleep(delay) # This rounds to int, but the throttle auto-adjusts
			end
		end
	end
ensure
	conn.close
end

