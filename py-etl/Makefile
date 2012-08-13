
# Use the right settings file based on current hostname.
hostname=$(shell hostname)
SETTINGS=./config/development.cfg

ifeq ($(hostname),paris)
SETTINGS=./config/live.cfg
endif

install:
	./env/bin/python ./env/bin/pip install -r ./requirements.txt

init:
	virtualenv ./env

# This is just for test runs
run:
	SETTINGS_FILE=$(SETTINGS) ./env/bin/python ./main.py
