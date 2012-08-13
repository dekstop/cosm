#!/bin/sh

bin=`dirname "$0"`
bin=`cd "${bin}"; pwd`
APP_HOME=`cd "${bin}"; cd ..; pwd`

SETTINGS_FILE=${APP_HOME}/config/development.cfg ${APP_HOME}/env/bin/python ${APP_HOME}/load_metadata.py $@ || exit 1
