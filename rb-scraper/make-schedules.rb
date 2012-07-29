#!/usr/bin/env ruby
#
# Produces TSV data that can be loaded into the "schedule" table.
# 
# Created by martind on 2012-07-18.

require 'date'
require_relative 'env'

@prefs = {
	:dateformat => '%Y-%m-%dT%H:%M:%S'
}

def format(date)
	return date.strftime(@prefs[:dateformat])
end

# ========
# = main =
# ========

if (ARGV.size!=2) then
	puts "<yyyy-mm-dd> <yyyy-mm-dd>"
	exit 1
end

fromdate = DateTime.parse(ARGV[0])
todate = DateTime.parse(ARGV[1])

curdate = fromdate

begin
	puts "#{format(curdate + 0.0)}\t#{format(curdate + 0.25)}\ttrue"
	puts "#{format(curdate + 0.25)}\t#{format(curdate + 0.5)}\ttrue"
	puts "#{format(curdate + 0.5)}\t#{format(curdate + 0.75)}\ttrue"
	puts "#{format(curdate + 0.75)}\t#{format(curdate + 1)}\ttrue"
	curdate += 1
end while curdate<=todate
