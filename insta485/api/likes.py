"""REST API for posts."""
import flask
import insta485
import pathlib
import uuid
import hashlib
import datetime
import base64
import os
import arrow


@insta485.app.route("/api/v1/likes/<int:likeid_url_slug>/", methods=["DELETE"])
def delete_like(likeid_url_slug):
    """Update a like in the database."""
    if (
        flask.request.authorization
        and flask.request.authorization.get("username")
        and flask.request.authorization.get("password")
    ):
        username = flask.request.authorization.get("username")
        password = flask.request.authorization.get("password")
        if (username is None) or (password is None):
            if "username" not in flask.session:
                context = {"message": "Forbidden", "status_code": 403}
                return flask.jsonify(**context), 403

            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT COUNT(username) as is_user "
                "FROM users AS u "
                "WHERE u.username == ?",
                (flask.session.get("username"),),
            )
            login_query = cur.fetchone()
            if login_query["is_user"] < 1:
                context = {"message": "Forbidden", "status_code": 403}
                return flask.jsonify(**context), 403
            else:
                username = flask.session.get("username")
        else:
            if insta485.model.check_authorized(username, password) is False:
                console.log(
                    "HTTP Authentication failed! For user: "
                    + username
                    + " and password: "
                    + password
                )
                context = {"message": "Forbidden", "status_code": 403}
                return flask.jsonify(**context), 403
    else:
        if "username" not in flask.session:
            return "", 403
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session.get("username"),),
        )
        login_query = cur.fetchone()
        if login_query["is_user"] < 1:
            return ("", 403)

        username = flask.session.get("username")

    if flask.request.method == "DELETE":
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(likeid) as like_exists "
            "FROM likes " "WHERE likeid == ? ",
            (likeid_url_slug,),
        )
        like_query = cur.fetchone()

        if like_query["like_exists"] < 1:
            context = {"message": "Not Found", "status_code": 403}
            return flask.jsonify(**context), 404

        cur = connection.execute(
            "SELECT COUNT(likeid) as has_liked "
            "FROM likes "
            "WHERE likeid == ? AND owner == ? ",
            (
                likeid_url_slug,
                username,
            ),
        )
        like_query = cur.fetchone()

        if like_query["has_liked"] < 1:
            return ("", 403)

        cur = connection.execute(
            "DELETE FROM likes " "WHERE likeid == ? AND owner == ? ",
            (
                likeid_url_slug,
                username,
            ),
        )
        return ("", 204)
    else:
        console.log("Request.method was not DELETE")
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def post_like():
    """Update a like in the database."""
    if (
        flask.request.authorization
        and flask.request.authorization.get("username")
        and flask.request.authorization.get("password")
    ):
        username = flask.request.authorization.get("username")
        password = flask.request.authorization.get("password")
        if (username is None) or (password is None):
            if "username" not in flask.session:
                return "", 403

            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT COUNT(username) as is_user "
                "FROM users AS u "
                "WHERE u.username == ?",
                (flask.session.get("username"),),
            )
            login_query = cur.fetchone()
            if login_query["is_user"] < 1:
                return "", 403
            else:
                username = flask.session.get("username")

        else:
            if insta485.model.check_authorized(username, password) is False:
                console.log(
                    "HTTP Authentication failed! For user: "
                    + username
                    + " and password: "
                    + password
                )
                context = {"message": "Forbidden", "status_code": 403}
                return flask.jsonify(**context), 403
    else:
        if "username" not in flask.session:
            return "", 403
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session.get("username"),),
        )
        login_query = cur.fetchone()
        if login_query["is_user"] < 1:
            return "", 403

        username = flask.session.get("username")

    if flask.request.method == "POST":
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(likeid) as has_liked "
            "FROM likes "
            "WHERE postid == ? AND owner == ? ",
            (
                flask.request.args.get("postid"),
                username,
            ),
        )
        like_query = cur.fetchone()

        if like_query["has_liked"] < 1:
            cur = connection.execute(
                "INSERT INTO likes(owner, postid) " "VALUES (?, ?)",
                (
                    username,
                    flask.request.args.get("postid"),
                ),
            )
            status = 201
        else:
            status = 200

        cur = connection.execute(
            "SELECT likeid " "FROM likes " "WHERE postid == ? AND owner == ? ",
            (
                flask.request.args.get("postid"),
                username,
            ),
        )
        like_query = cur.fetchone()

        context = {
            "likeid": like_query["likeid"],
            "url": "/api/v1/likes/{}/".format(like_query["likeid"]),
        }
        return flask.jsonify(**context), status
    else:
        console.log("Request.method was not POST")
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
