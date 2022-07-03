import time
import random
import requests
import json

# import psycopg2
import rich
import sys

from sqlalchemy import create_engine


db_name = "compounds"
db_user = "ebi-as"
db_pass = "secrekt"
db_host = "localhost"  # db
db_port = "5432"

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
        if sys.argv[2].upper() not in compound_names:
            print("\nInvalid compound name:", sys.argv[2].upper())
            quit()
        url = (
            "https://www.ebi.ac.uk/pdbe/graph-api/compound/summary/"
            + sys.argv[2].upper()
        )
        print(f"Requesting JSON from {url}")
        text = requests.get(url)
        text = text.text
        data = json.loads(text)
        print(type(data))
        print(data)

    # print(sys.argv[1])
