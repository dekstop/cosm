#!/bin/bash
bin=`dirname "$0"`
bin=`cd "${bin}"; pwd`
APP_HOME=`cd "${bin}"; cd ..; pwd`

cp="${APP_HOME}/conf"
cp="${cp}:${APP_HOME}/build/classes"
cp="${cp}:${APP_HOME}/lib/*"

java -Djava.awt.headless=true -Xmx1G -classpath "${cp}" de.dekstop.cosm.Coverage "$@" || exit 1
