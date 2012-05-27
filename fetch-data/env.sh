#!/bin/bash

APIKEY=YOUR_API_KEY
DATADIR=~/cosm/data

PERL=perl

function add_days() {
	date=$1
	num_days=$2
	# BSD
	echo `date -j -f "%Y-%m-%d" -v +${num_days}d $date +"%Y-%m-%d"`
	# GNU
	#echo `date --date "${date} + $num_days day" +"%Y-%m-%d"`
}

function iso8601_to_epoch() {
	date=$1
	_time=$2
	# BSD
	echo `date -j -f "%Y-%m-%dT%H:%M:%S" "${date}T${_time}" +%s`
	# GNU
	#echo date --date "${date} ${_time}" +%s`
}

function xpath_query() {
	xmlfile=$1
	query=$2
	$PERL -e "
		use XML::XPath; 
		\$xpath = XML::XPath->new(filename => '${xmlfile}'); 
		print(\$xpath->find('${query}'));
	"
}

function check_cosm_error_response() {
	file="$1"
	if grep -q '<errors>' "${file}"
	then
		title=`xpath_query "${file}" '/errors/title/text()'`
		message=`xpath_query "${file}" '/errors/error/text()'`
		echo "${title}: ${message}"
		return 1
	fi
	if grep -q '<html>' "${file}"
	then
		cat "${file}"
		return 1
	fi
	return 0
}
