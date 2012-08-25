#!/bin/bash

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
  bin/python plot-volume.py "${infile}" ${colidx} "${outfile}" $@ || exit 1
done
