"""Insta485 model (database) API."""
import sqlite3
import flask
import insta485
import pathlib
import uuid
import hashlib
import datetime
import base64
import os
import arrow


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    if "sqlite_db" not in flask.g:
        db_filename = insta485.app.config["DATABASE_FILENAME"]
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop("sqlite_db", None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def check_authorized(username, password):
    """Check authorized."""
    connection = get_db()
    cur = connection.execute(
        "SELECT COUNT(username) as is_user, "
        "u.username as queried_name, "
        "u.password as hashed_password "
        "FROM users AS u "
        "WHERE u.username == ?",
        (username,),
    )
    login_query = cur.fetchone()
    if login_query["is_user"] < 1:
        return False

    hash = login_query["hashed_password"]
    # print(login_query)
    split_hash = hash.split("$")
    # print(split_hash)
    salt_from_hash = split_hash[1]
    # print(salt_from_hash)

    algorithm = "sha512"
    salt = salt_from_hash
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if password_db_string == login_query["hashed_password"]:
        # print("Password matched! Loging in")
        return True
    else:
        # print("Password is not a match!")
        return False
