#!/bin/bash

APP_HOME=`dirname "$0"`
APP_HOME=`cd "${APP_HOME}"; pwd`

if [ $# -lt 4 ]
then
  echo "Usage: `basename $0` <indir> <outdir> <colidx> <tag> [args]"
  exit 1
fi

indir="$1"
outdir="$2"
colidx="$3"
tag="$4"
shift 4

for infile in "${indir}"/*.txt
do
  echo $infile
  name=`basename "${infile}" .txt`
  outfile="${outdir}/${name}-${tag}.pdf"
  ${APP_HOME}/bin/python ${APP_HOME}/plot-numeric-volume.py "${infile}" ${colidx} "${outfile}" $@ || exit 1
done
