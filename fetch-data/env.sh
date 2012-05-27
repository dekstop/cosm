#!/bin/bash

APIKEY=YOUR_API_KEY
DATADIR=~/cosm/data

PERL=perl5.10

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
