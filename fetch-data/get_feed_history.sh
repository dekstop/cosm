#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

indexfile="${DATADIR}/feed_index/feed_index.txt"
ENV_IDS=`grep live "$indexfile" | cut -d '	' -f 1 | sort | uniq`

NUMDAYS=14

if [ $# -ge 1 ]
then
	STARTDATE=$1
	ENDDATE=$2
else
	# BSD
	STARTDATE=`date -v "-${NUMDAYS}d" "+%Y-%m-%d"`
	ENDDATE=`date -v "-1d" "+%Y-%m-%d"`
	# GNU
	#STARTDATE=`date --date="${NUMDAYS} days ago" "+%Y-%m-%d"`
	#ENDDATE=`date --date="1 day ago" "+%Y-%m-%d"`
fi

function get_feed_history() {
	id=$1
	startdate=$2
	enddate=$3
	url="https://api.cosm.com/v2/feeds/${id}.xml?key=${APIKEY}&start=${startdate}&end=${enddate}"
	# echo "${url} ..."
	curl $url -s -S || return 1
}

dir="${DATADIR}/feed_history/${STARTDATE}"
mkdir -p "${dir}" > /dev/null 2>&1

for id in $ENV_IDS
do
	file="${dir}/${id}.xml"
	echo "Feed ${id}: ${file}"
	if [ ! -f $file ];
	then
		get_feed_history "$id" "$STARTDATE" "$ENDDATE" > $file || exit 1
		check_cosm_error_response $file || (rm $file; exit 1)
		echo "Wait..."
		sleep 2
	fi
done
