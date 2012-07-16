#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

if [ $# -eq 0 ]
then
	echo "<environment ID>"
	echo "This will extract time series data from the XML files of a particular environment."
	exit 1
fi

ENVID=$1
files=`find $DATADIR -name "${ENVID}.xml"`

function extract_data() {
	file="$1"
	"$PERL" "${DIR}/extract_feed_time_series_data.pl" "${file}"
}

for file in $files 
do
	extract_data $file
done
