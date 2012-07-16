#!/bin/bash

DIR=$( cd "$( dirname "$0" )" && pwd )
. ${DIR}/env.sh

indexfile="${DATADIR}/feed_index/feed_index.txt"
ENV_IDS=`grep live "$indexfile" | cut -d '	' -f 1 | sort -n | uniq`
echo $ENV_IDS
