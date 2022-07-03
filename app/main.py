import time
import random
import psycopg2
import rich
import sys

from sqlalchemy import create_engine

db_name = "compounds"
db_user = "ebi-as"
db_pass = "secrekt"
db_host = "localhost"  # db
db_port = "5432"

# Connecto to the database
db_string = "postgresql://{}:{}@{}:{}/{}".format(
    db_user, db_pass, db_host, db_port, db_name
)
db = create_engine(db_string)


def add_new_row(n):
    # Insert a new number into the 'numbers' table.
    db.execute(
        "INSERT INTO numbers (number,timestamp) "
        + "VALUES ("
        + str(n)
        + ","
        + str(int(round(time.time() * 1000)))
        + ");"
    )


def get_last_row():
    # Retrieve the last number inserted inside the 'numbers'
    query = (
        ""
        + "SELECT number "
        + "FROM numbers "
        + "WHERE timestamp >= (SELECT max(timestamp) FROM numbers)"
        + "LIMIT 1"
    )

    result_set = db.execute(query)
    for r in result_set:
        return r[0]


if __name__ == "__main__":
    print("Application started")
    add_new_row(random.randint(1, 100000))
    print("The last value insterted is: {}".format(get_last_row()))
    # while True:
    # time.sleep(1)
    # add_new_row(random.randint(1, 100000))
    # print("The last value insterted is: {}".format(get_last_row()))
    if (len(sys.argv)) == 1:
        print("USAGE: \n get <compound name>")
        print("")
    # print(sys.argv[1])
