2012-08-13 18:27:16

Python tools for Cosm DB data loading and data extraction.

 =================
 = Prerequisites =
 =================

- Python 2.7
- virtualenv, virtualenvwrapper
- pip
- A relational database (tested on SQLite and PostgreSQL)

For installation instructions of the Python prerequisites on OSX refer to:
http://jamiecurle.co.uk/blog/installing-pip-virtualenv-and-virtualenvwrapper-on-os-x/

 =========
 = Setup =
 =========

Edit config/development.cfg

Then:
$ make init
$ make install

 =============
 = Execution =
 =============

TODO
- how to initialise the DB
- how to load metadata tables
- how to load data
- how to query for data
