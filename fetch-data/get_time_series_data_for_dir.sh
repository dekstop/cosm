#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

if [ $# -eq 0 ]
then
	echo "<dir>"
	echo "This will extract time series data from the XML files of a particular directory."
	exit 1
fi

dir="$1"
files=`find "${dir}" -name "*.xml"`

function extract_data() {
	file="$1"
	"$PERL" "${DIR}/extract_feed_time_series_data.pl" "${file}"
}

for file in $files 
do
	extract_data $file
done
