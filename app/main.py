import time
from pyparsing import col
import requests
import json

from psycopg2 import connect, Error
import rich
import sys

from sqlalchemy import create_engine


db_name = "compounds"
db_user = "ebi-as"
db_pass = "secrekt"
db_host = "localhost"  # db
db_port = "5432"

columns = ["compound", "formula", "inchi", "inchi_key", "smiles", "cross_links_count"]

compound_names = ["ADP", "ATP", "STI", "ZID", "DPM", "XP9", "18W", "29P"]
# Connecto to the database
db_string = "postgresql://{}:{}@{}:{}/{}".format(
    db_user, db_pass, db_host, db_port, db_name
)


db = create_engine(db_string)


def add_new_row(n):
    db.execute(
        "INSERT INTO compounds (number,timestamp) "
        + "VALUES ("
        + str(n)
        + ","
        + str(int(round(time.time() * 1000)))
        + ");"
    )


def get_last_row():
    query = (
        ""
        + "SELECT compound "
        + "FROM compounds "
        + "WHERE timestamp >= (SELECT max(timestamp) FROM numbers)"
        + "LIMIT 1"
    )

    result_set = db.execute(query)
    for r in result_set:
        return r[0]


def request_api(api):
    api = api.upper()
    url = "https://www.ebi.ac.uk/pdbe/graph-api/compound/summary/" + api
    print(f"Requesting JSON from {url}")
    try:
        text = requests.get(url)
    except:
        print("Could not connect to ebi.ac api ¯\_(ツ)_/¯")
        quit()
    text = text.text
    data = json.loads(text)
    # print(type(data))
    # print(data[api][0]["name"])
    return data


def insert_row(data, api):
    for column in columns:
        print(column)
    print("INSERT INTO compounds (" + ",".join(columns) + ")")
    """
    db.execute(
        "INSERT INTO compounds (number,timestamp) "
        + "VALUES ("
        + str(n)
        + ","
        + str(int(round(time.time() * 1000)))
        + ");"
    )
    """


if __name__ == "__main__":
    print("Application started")
    # add_new_row(random.randint(1, 100000))

    # print("The last value insterted is: {}".format(get_last_row()))

    # while True:
    # time.sleep(1)
    # add_new_row(random.randint(1, 100000))
    # print("The last value insterted is: {}".format(get_last_row()))

    if (len(sys.argv)) == 1:
        print("USAGE: \n\n get <compound name>")
        print("or \n show <compound name>")
        print("\nvalid compound names are:")
        print(*compound_names, sep=", ")
        quit()

    if sys.argv[1] == "get":
        if len(sys.argv) == 2:
            print("You must specify a compound name")
            quit()
        if sys.argv[2].upper() not in compound_names:
            print("\nInvalid compound name:", sys.argv[2].upper())
            quit()
        data = request_api(sys.argv[2])
        insert_row(data, sys.argv[2])

    elif sys.argv[1] == "show":
        if len(sys.argv) == 2:
            # show all
            quit()
    # print(sys.argv[1])


def test_no_args():
    add_new_row(111)


def test_wrong_args():
    pass


def test_right_args():
    pass
