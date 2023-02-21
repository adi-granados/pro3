"""REST API for comments."""
import flask
from flask import request
import hashlib
import insta485
from insta485.api.helper_functions import calculate_password
from insta485.api.helper_functions import check_access
from insta485.api.helper_functions import comments_get
from insta485.api.helper_functions import likes_get
from insta485.api.helper_functions import posts_helper
from insta485.api.helper_functions import get_username
from insta485.api.helper_functions import return_403
from insta485.api.helper_functions import return_404


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def create_comment():
    """Create a new comment to a given post."""
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

        username = flask.session.get("username")

    postid = int(flask.request.args.get("postid"))
    text = flask.request.json["text"]
    connection = insta485.model.get_db()

    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        f"VALUES ('{username}', {int(postid)}, '{text}') "
    )

    cur = connection.execute("SELECT MAX(commentid) as c_id " "FROM comments ")
    commentid = cur.fetchone()

    context = {
        "commentid": commentid["c_id"],
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": "/users/" + username + "/",
        "text": text,
        "url": flask.request.path + str(commentid["c_id"]) + "/",
    }
    return flask.jsonify(**context), 201


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete comment."""
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

        username = flask.session.get("username")

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT Count(*) as comment_exists, owner "
        "FROM comments "
        "WHERE commentid == ?",
        (commentid,),
    )
    comment_query = cur.fetchone()

    if comment_query["comment_exists"] < 1:
        return return_404()

    if comment_query["owner"] != username:
        return return_403()

    connection.execute(
      "DELETE FROM comments " f"WHERE commentid == '{commentid}' ")
    return flask.jsonify(), 204
