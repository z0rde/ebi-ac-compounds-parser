# from doctest import debug
# from attr import field
# from pyparsing import col
import time
import requests
import json
from rich import print
from rich.console import Console
from rich.table import Table
import sys
import os
from sqlalchemy import create_engine
import logging.handlers

handler = logging.FileHandler("sql_calls.log")
handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s %(message)s"))
sql_logger = logging.getLogger("sqlalchemy.engine")
sql_logger.propagate = False
sql_logger.setLevel(20)
sql_logger.addHandler(handler)


db_name = "compounds"
db_user = "ebi-as"
db_pass = "secrekt"
db_host = "localhost"  # db
db_port = "5432"

columns = ["compound", "formula", "inchi", "inchi_key", "smiles", "cross_links_count"]

# global compound_names
compound_names = ["ADP", "ATP", "STI", "ZID", "DPM", "XP9", "18W", "29P"]

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
        debug.critical("Could not connect to ebi.ac api (ツ)")
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
        if type(element) == int:  # check for cross_links_count
            element = str(element)
        if len(element) > length:
            element = element[:length] + "..."
        newlist.append(element)
    return newlist


def table_rows_count():
    return list(db.execute("" + "SELECT COUNT(*) " + "FROM compounds "))[0][0]


def compounds_inside_table():
    tlist = list(db.execute("" + "SELECT compound FROM compounds "))
    return [item for t in tlist for item in t]


def get_row(compound):
    # print("geting compound:", compound)
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
        return False


def print_table(*data):
    try:
        width = os.get_terminal_size().columns
    except:
        width = 120

    table = Table(title="Compounds:")
    for column in columns:
        table.add_column(column, style="magenta", no_wrap=True)
    for inner in data:
        for row in inner:
            if row:
                row = shorten(
                    row, int((width - 7) / len(row))
                )  # the formula of a nice table
                table.add_row(*row)  #
    console = Console()
    console.print(table)


def is_compound(name):
    if name.upper() not in compound_names:
        print("\nInvalid compound name:", name)
        return False
    return True


def show_help():
    print(  # if unknown argument or no argument given, print help
        """
[italic]USAGE:[/italic]
            
[bold]get[/bold] [compound name] - parse compound info to db
[bold]get all[/bold] - get all compounds

[bold]show[/bold] [compound name] - display compound data from db
[bold]show all[/bold] - display all gathered data
            
[bold]clear[/bold] - erase the database

valid compound names are: """
    )
    print(*compound_names, sep=", ")
    return "Invalid arguments"


def blue(string):
    return "[bold blue]" + string + "[/bold blue]"


def main(cmd):
    print("[yellow]ebi.cli.uk compound database parser version 1.0[/yellow]")
    if len(cmd) == 1:
        return show_help()
    if cmd[1] == "clear":
        drop()
        return "Table dropped"

    if cmd[1] == "get":

        if len(cmd) == 2:
            return "You must specify a compound name"
        if cmd[2].upper() == "ALL":
            print("Gathering all the compounds...")
            drop()
            for compound in compound_names:
                insert_row(request_api(compound))
                if (
                    compound is not compound_names[-1]
                ):  # delay only if there are no more requests
                    time.sleep(1)
            return "All compounds gathered"

        if not is_compound(cmd[2].upper()):
            return "Invalid compound name"
        elif cmd[2].upper() not in compounds_inside_table():
            insert_row(request_api(cmd[2]))
            return "Compound " + cmd[2] + " added to database"
        else:
            return "Compound is already in the database!"

    elif cmd[1] == "show":
        compounds_inside = compounds_inside_table()  # less sql queries
        if not compounds_inside:
            return "Nothing to show, table is empty!"
        data = []

        if len(cmd) == 2 or cmd[2].upper() == "ALL":
            pass  # some tricky logic, or not ( ͡° ͜ʖ ͡°)

        elif not is_compound(cmd[2]):
            return "invalid compound name"

        else:
            if cmd[2] not in compounds_inside:
                return "That compound in not in the table"
        data = list(
            db.execute(
                "" + "SELECT * FROM compounds " + " LIMIT " + str(len(compound_names))
            )
        )
        print_table(data)
        return "Done!"
    return show_help()


if __name__ == "__main__":
    print(blue(main(sys.argv)))


def test_no_args():
    assert main([None, None]) == "Invalid arguments"


def test_wrong_args():
    assert main([None, "oh", "hi", "mark"]) == "Invalid arguments"


def test_wrong_sub_args():
    assert main([None, "get", "something"]) == "Invalid compound name"


def test_right_args():
    main([None, "clear"])
    assert main([None, "get", "atp"]) == "Compound atp added to database"


def test_double_record():
    main([None, "clear"])
    main([None, "get", "18w"])
    assert main([None, "get", "18w"]) == "Compound is already in the database!"


# [green]٩(◕‿◕｡)۶[/green]
