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
batch_size=10
find "${dir}" -name "*.xml" | xargs -n $batch_size "$PERL" "${DIR}/extract_feed_time_series_data.pl" || exit 1

