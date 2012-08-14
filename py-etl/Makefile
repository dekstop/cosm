
# Use the right settings file based on current hostname.
hostname=$(shell hostname)
SETTINGS=./config/development.cfg

ifeq ($(hostname),paris)
SETTINGS=./config/live.cfg
endif

init:
	virtualenv ./env

install:
	./env/bin/python ./env/bin/pip install -r ./requirements.txt

# This is just for test runs
run:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./main.py
