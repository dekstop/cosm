#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

indexfile="${DATADIR}/feed_index/feed_index.txt"
ENV_IDS=`grep live "$indexfile" | cut -d '	' -f 1 | sort -n | uniq`

if [ $# -eq 0 ]
then
	echo "<%Y-%m-%d> [%H:%M:%S]"
	echo "This will request data for a 24h window starting at the given time."
	echo "(Actual data returned may be less, depending on respective data stream.)"
	exit 1
fi

STARTDATE=$1
ENDDATE=`add_days $STARTDATE 1` || exit 1
STARTTIME=00:00:00

if [ $# -ge 2 ]
then
	STARTTIME="$2"
fi

echo "From: ${STARTDATE} ${STARTTIME}"
echo "To: ${ENDDATE} ${STARTTIME}"

function get_feed_history() {
	id=$1
	startdate=$2
	enddate=$3
	url="https://api.cosm.com/v2/feeds/${id}.xml?key=${APIKEY}&start=${startdate}&end=${enddate}"
	# echo "${url} ..."
	curl $url -s -S || return 1
}

dir="${DATADIR}/feed_history/${STARTDATE}T${STARTTIME}"
indexfile="${dir}/index.txt"
mkdir -p "${dir}" > /dev/null 2>&1

for id in $ENV_IDS
do
	file="${dir}/${id}.xml"
	echo "Feed ${id}: ${file}"
	if [ ! -f $file ];
	then
		get_feed_history "$id" "${STARTDATE}T${STARTTIME}" "${ENDDATE}T${STARTTIME}" > $file #|| exit 1
		check_cosm_error_response $file || (rm $file; exit 1)
		echo "Wait..."
		sleep 1
	fi
done
