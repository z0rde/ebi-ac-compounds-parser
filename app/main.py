import time
from attr import field
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


def request_api(compound):
    compound = compound.upper()
    url = "https://www.ebi.ac.uk/pdbe/graph-api/compound/summary/" + compound
    print(f"Requesting JSON from {url}")
    try:
        text = requests.get(url)
    except:
        print("Could not connect to ebi.ac api ¯\_(ツ)_/¯")
        quit()
    text = text.text
    data = json.loads(text)
    fields_data = [compound]  # first element is not from nested json part
    for column in columns[1:-1]:
        fields_data.append(data[compound][0][column])
    fields_data.append(
        len(data[compound][0]["cross_links"][0])
    )  # calculating cross_links_count
    return fields_data


def drop():
    db.execute("DROP TABLE IF EXISTS compounds")
    print("Database cleared")


def insert_row(fields_data):
    db.execute(
        "INSERT INTO compounds ("
        + ",".join(columns)
        + ")"
        + "VALUES ('"
        + "','".join(fields_data[:-1])
        + "',"
        + str(fields_data[-1])  # last element cross_links_count is an int
        + ");"
    )


if __name__ == "__main__":
    print("Mission start!")

    if (len(sys.argv)) == 1:  # show help if no arguments
        print(
            """
    USAGE:
                
    get [compound name] - parse compound info to db
    get all - get all compounds

    show [compound name] - display compound data from db
    show all - display all gathered data
               
    clear - erase the database

    valid compound names are: """
        )
        print(*compound_names, sep=", ")
        print(
            """

            """
        )
        quit()

    if sys.argv[1] == "clear":
        drop()
        quit()

    if sys.argv[1] == "get":

        if len(sys.argv) == 2:
            print("You must specify a compound name")
            quit()

        if sys.argv[2].upper() not in compound_names:
            print("\nInvalid compound name:", sys.argv[2].upper())
            quit()

        insert_row(request_api(sys.argv[2]))
        print("Compound", sys.argv[2], "added to database! ٩(◕‿◕｡)۶")
        quit()

    elif sys.argv[1] == "show":
        if len(sys.argv) == 2:
            # show all
            quit()


def test_no_args():
    add_new_row(111)


def test_wrong_args():
    pass


def test_right_args():
    pass
