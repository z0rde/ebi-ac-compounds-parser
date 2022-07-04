import time
from attr import field
from pyparsing import col
import requests
import json
from psycopg2 import connect, Error
from rich.console import Console
from rich.table import Table
import sys
import os
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
    db.execute(
        """
    CREATE TABLE compounds (compound VARCHAR, 
    formula VARCHAR, inchi VARCHAR, inchi_key VARCHAR, 
    smiles VARCHAR, cross_links_count SMALLINT)
    """
    )
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


def shorten(list, length):
    newlist = []
    for element in list:
        if len(element) > length:
            element = element[:length] + "..."
        newlist.append(element)
    return newlist


def get_row(compound):
    print("geting compound:", compound)
    try:
        row = db.execute(
            ""
            + "SELECT * "
            + "FROM compounds "
            + "WHERE compound = '"
            + compound
            + "' LIMIT 1"
        )
        row = list(row)
        row = list(row[0])
        row.append(str(row.pop()))  # for Rich table int is not acceptable
        return row
    except:
        print("Failed to get row:", compound)
        return False


def print_table(*data):
    try:
        width = os.get_terminal_size().columns
    except:
        width = 120

    table = Table(title="Compounds:")
    for column in columns:
        table.add_column(column, style="magenta", no_wrap=True)
    # for row in rows:
    #    print("row:", row, "len:", len(row))
    for inner in data:
        for row in inner:
            row = shorten(
                row, int((width - 7) / len(row))
            )  # the formula of a nice table
            table.add_row(*row)  #
    console = Console()
    console.print(table)
    quit()


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
        if sys.argv[2].upper() == "ALL":
            print("Gathering all the compounds...")
            drop()
            execlist = []
            for compound in compound_names:
                insert_row(request_api(compound))
                if (
                    compound is not compound_names[-1]
                ):  # delay only if there are no more requests
                    time.sleep(1)
            quit()

        if sys.argv[2].upper() not in compound_names:
            print("\nInvalid compound name:", sys.argv[2].upper())
            quit()

        insert_row(request_api(sys.argv[2]))
        print("Compound", sys.argv[2], "added to database! ٩(◕‿◕｡)۶")
        quit()

    elif sys.argv[1] == "show":
        if len(sys.argv) == 2:
            data = []
            for compound in compound_names:
                data.append(get_row(compound)[0])
            print_table(data)
            # print(data)
            quit()


def test_no_args():
    add_new_row(111)


def test_wrong_args():
    pass


def test_right_args():
    pass
