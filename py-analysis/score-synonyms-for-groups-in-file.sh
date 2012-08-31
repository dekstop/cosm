#!/bin/bash

APP_HOME=`dirname "$0"`
APP_HOME=`cd "${APP_HOME}"; pwd`

if [ $# -lt 4 ]
then
  echo "Usage: `basename $0` <file1> <file2> <outdir> <tag> [args]"
  exit 1
fi

infile1="$1"
infile2="$2"
outdir="$3"
tag="$4"
shift 4

groups=`cut -f 1 "${infile1}" | uniq | sort | uniq`
for group in $groups
do
  echo $group
  # name=`basename "${infile}" .txt`
  outfile="${outdir}/${tag}-group-${group}.txt"
  nice -5 time arch -i386 ${APP_HOME}/bin/python ${APP_HOME}/score-synonyms.py "${infile1}" "${infile2}" "${outfile}" \
    --as-strings --group "${group}" $@ || exit 1
done
