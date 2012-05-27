#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

indexfile="${DATADIR}/feed_index/feed_index.txt"
outdir="${DATADIR}/feed_index"
aqfeedfile="${outdir}/aq_feeds.txt"

AQTAGS='air quality
airquality
airqualityegg
air quality egg
aqe
project:id:aqe'

function get_feeds() {
	tag=$1
	grep -i "${tag}" $indexfile
}

function get_last_column() {
	awk -F\t '{print $NF}'
}

function split_tags() {
	tr "," "\n"
}

function strip_leading_whitespace() {
	sed -e 's/^[ ]*//'
}

function summarise_tags() {
	file=$1
	col_uniqid=$2
	col_tags=$3
	
	cut -f ${col_uniqid},${col_tags} $file | sort | uniq | get_last_column | split_tags | strip_leading_whitespace | sort | uniq -c | sort -rn 
}

function cleanup() {
	IFS=$SAVEIFS
}

mkdir -p "${outdir}" > /dev/null 2>&1

# select datastreams

# for tag in ${AQTAGS}
# do
# 	echo "${tag}..."
# 	get_feeds "${tag}" >> "${aqfeedfile}.tmp" || (cleanup; exit 1)
# done
# 
# head -n 1 "$indexfile" > "$aqfeedfile"
# sort "${aqfeedfile}.tmp" | uniq >> "$aqfeedfile"
# rm "${aqfeedfile}.tmp"
# 
# echo "Number of datastreams:"
# wc -l "$aqfeedfile"

# summarise tags
summarise_tags "$aqfeedfile" 1 10 > "${outdir}/aq_feed_tags.txt"
summarise_tags "$aqfeedfile" 1,11 15 > "${outdir}/aq_datastream_tags.txt"
summarise_tags "$aqfeedfile" 1,11 11 > "${outdir}/aq_datastream_ids.txt"
summarise_tags "$aqfeedfile" 1,11 12 > "${outdir}/aq_datastream_units.txt"

cleanup
