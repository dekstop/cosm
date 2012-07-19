#!/usr/bin/env ruby
#
#  Created by martind on 2012-07-18.

STDOUT.sync = true # don't buffer stdout

@env = {
	:datadir => '~/cosm/data',
	:apikey => 'YOUR_API_KEY',
	
	:dbname => 'cosm', 
	:user => 'postgres', 
	:password => ''
}
