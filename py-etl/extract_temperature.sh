#!/bin/bash

bin=`dirname "$0"`
bin=`cd "${bin}"; pwd`
APP_HOME=`cd "${bin}"; pwd`

#rootdir="${APP_HOME}/data"
rootdir=~/cosm/data/groups/2012-08-14

export SETTINGS_FILE="${APP_HOME}/config/development.cfg"
app="${APP_HOME}/env/bin/python export_group_summary.py"

tags='temperature,temp,temperatura,temperatures,temperatur,outside temperature,outside temp,air temperature,température,temperatuur,outdoor temperature'
units='celsius,c,c.,ºc,º c,degc,celcius,oc,degrees celsius,deg c,degrees c,degree c,deg. c.,*c,celsius (°c),centigrade,centigrades,degrees celcius,degree celcius,degrès celcius,deg celsius'
lat="48.0,61.0"
lon="-11.0,4.15"

# for d in `seq -w 1 31`
for d in 01 05 10 15 20 25 30
do
	for h in `seq -w 0 3 21`
	do
		date="2011-08-${d}"
		fromdate="${date}T${h}:00:00"
		# todate="${date}T03:00:00"
		#todate=`date -j -f "%Y-%m-%dT%H:%M:%S" -v +3H ${fromdate} +"%Y-%m-%dT%H:%M:%S"`
		todate=`date -u --date "${date} ${h} + 3 hour" +"%Y-%m-%dT%H:%M:%S"`
		echo "${fromdate} - ${todate}"
		${app} ${fromdate} ${todate} ${rootdir}/uk-all/${fromdate}-${todate} --latitude="${lat}" --longitude="${lon}" || exit 1
		${app} ${fromdate} ${todate} ${rootdir}/uk-temperature-units/outdoor/${fromdate}-${todate} -e outdoor -u "${units}" --latitude="${lat}" --longitude="${lon}" || exit 1
		${app} ${fromdate} ${todate} ${rootdir}/uk-temperature-units/all/${fromdate}-${todate} -u "${units}" --latitude="${lat}" --longitude="${lon}" || exit 1
		${app} ${fromdate} ${todate} ${rootdir}/uk-temperature-tags/outdoor/${fromdate}-${todate} -e outdoor -t "${tags}" --latitude="${lat}" --longitude="${lon}" || exit 1
		${app} ${fromdate} ${todate} ${rootdir}/uk-temperature-tags/all/${fromdate}-${todate} -t "${tags}" --latitude="${lat}" --longitude="${lon}" || exit 1
		${app} ${fromdate} ${todate} ${rootdir}/uk-temperature-tags-units/outdoor/${fromdate}-${todate} -e outdoor -t "${tags}" -u "${units}" --latitude="${lat}" --longitude="${lon}" || exit 1
		${app} ${fromdate} ${todate} ${rootdir}/uk-temperature-tags-units/all/${fromdate}-${todate} -t "${tags}" -u "${units}" --latitude="${lat}" --longitude="${lon}" || exit 1
	done
done
