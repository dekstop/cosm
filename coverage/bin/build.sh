#!/bin/bash
bin=`dirname "$0"`
bin=`cd "${bin}"; pwd`
APP_HOME=`cd "${bin}"; cd ..; pwd`

cp="${APP_HOME}/conf"
cp="${cp}:${APP_HOME}/build/classes"
cp="${cp}:${APP_HOME}/lib/*"

mkdir -p ${APP_HOME}/build/classes > /dev/null 2>&1
echo $cp
javac -classpath "${cp}" -sourcepath ${APP_HOME}/java -d ${APP_HOME}/build/classes ${APP_HOME}/java/de/dekstop/cosm/Coverage.java "$@" || exit 1
