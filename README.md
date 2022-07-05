# ebi.ac.uk compounds database parser

Parsing compounds data from ebi.ac.uk api to Postgres database.
The goal was to keep it clean and minimal in modules, without using
unnecesary thinks like flask etc.

external modules used:

requests

rich

sqlalchemy

# How to use:

_install with_

> docker-compose build

_run with command line arguments:_

### sudo docker-compose run app [arguments...]

for example

> sudo docker-compose run app get all

get - parse compound info to db

get all - get all compounds

show - display compound data from db

show all - display all gathered data

clear - erase the database

valid compound names are:

ADP, ATP, STI, ZID, DPM, XP9, 18W, 29P
