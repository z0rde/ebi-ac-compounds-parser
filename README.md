# ebi.ac.uk compounds database parser

Parsing compounds data from ebi.ac.uk api to Postgres database.
The goal was to keep it clean and minimal in modules, without using
any unnecesary things like flask etc.

external modules used:

_requests_, for getting data from web api

_rich_, for printing it in table form

_sqlalchemy_ for database access

# How to use:

_install with_

> docker-compose build

_run with command line arguments:_

### sudo docker-compose run app [arguments...]

for example

> sudo docker-compose run app get all

_get_ - parse compound info to db

_get all_ - get all compounds

_show_ - display compound data from db

_show all_ - display all gathered data

_clear_ - erase the database

valid compound names are:

_ADP, ATP, STI, ZID, DPM, XP9, 18W, 29P_
