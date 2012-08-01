#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

indexfile="${DATADIR}/feed_index/feed_index.txt"

function get_feed() {
	page=$1
	curl -s -S "http://api.cosm.com/v2/feeds.xml?key=${APIKEY}&order=created_at&page=${page}" || return 1
}

function extract_summary() {
	file="$1"
	"$PERL" "${DIR}/extract_feed_summary.pl" "${file}"
}

mkdir -p "${DATADIR}/feed_index/xml" > /dev/null 2>&1
#rm "$indexfile"
echo "ID	CREATOR	CREATED_AT	UPDATED_AT	TITLE	FEED	STATUS	PRIVATE	LOCATION	LOCATION_DOMAIN	LOCATION_EXPOSURE	LOCATION_DISPOSITION	LAT	LON	ENV_TAGS	STREAM_ID	STREAM_UNIT	VALUE	STREAM_TIMESTAMP	STREAM_TAGS	ALL_TAGS" > "$indexfile"

for i in `seq 1 250`
do
	echo "Page ${i}..."
	xmlfile="${DATADIR}/feed_index/xml/${i}.xml"
	get_feed $i > "$xmlfile" || exit 1
	check_cosm_error_response "$xmlfile" || exit 1
	echo "Wait..."
	sleep 2
	extract_summary "$xmlfile" >> "$indexfile" # || exit 1
done
