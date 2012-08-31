#!/bin/bash

APP_HOME=`dirname "$0"`
APP_HOME=`cd "${APP_HOME}"; pwd`

if [ $# -lt 3 ]
then
  echo "Usage: `basename $0` <indir> <outdir> <colidx> [args]"
  exit 1
fi

indir="$1"
outdir="$2"
colidx="$3"
shift 3

for infile in "${indir}"/*.txt
do
  echo $infile
  name=`basename "${infile}" .txt`
  outfile="${outdir}/${name}.pdf"
  ${APP_HOME}/bin/python ${APP_HOME}/plot-histogram.py "${infile}" ${colidx} "${outfile}" $@ || exit 1
done
