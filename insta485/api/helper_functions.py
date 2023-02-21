"""Helper functions."""
import hashlib
import insta485
import flask
from flask import request


def return_403():
    """Return 403."""
    return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403


def return_404():
    """Return 404."""
    return flask.jsonify({"message": "Forbidden", "status_code": 404}), 404


def comments_get():
    """Comments helper."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT commentid, owner, postid, text "
        "FROM comments ")

    comments_data = cur.fetchall()
    return comments_data


def likes_get():
    """Likes helper."""
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT likeid, owner, postid " "FROM likes")

    like_data = cur.fetchall()
    return like_data


def posts_helper(postid_url_slug):
    """Post helper."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT posts.postid, posts.filename, "
        "posts.owner, posts.created, users.filename AS user_filename "
        "FROM posts "
        "JOIN users ON posts.owner=users.username; "
    )

    post_data = cur.fetchall()
    post_data = [i for i in post_data if i["postid"] == int(postid_url_slug)]
    if len(post_data) == 0:
        return None

    comments = comments_get()
    comments = [i for i in comments if i["postid"] == int(postid_url_slug)]
    cur = connection.execute("SELECT owner, postid " "FROM likes ")

    num_likes = cur.fetchall()
    num_likes = [i for i in num_likes if i["postid"] == int(postid_url_slug)]

    cur = connection.execute("SELECT owner, postid " "FROM likes")

    likes = cur.fetchall()
    likeid = likes_get()
    likeid = [i for i in likeid if i["postid"] == int(postid_url_slug)]
    connection_data = [post_data, comments, num_likes, likes, likeid]
    return connection_data


def get_username():
    """Username."""
    if "login" in request.cookies:
        return flask.session["username"]
    return flask.request.authorization.get("username")


def calculate_password(user_password, password):
    """Calculate password."""
    algorithm = user_password[0]
    salt = user_password[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    password_string = "$".join([algorithm, salt, password_hash])
    return password_string


def check_access(request_auth):
    """Check access."""
    if "login" in request.cookies:
        return True
    if request_auth is None or (
        request_auth.get("username") is None
        or request_auth.get("password") is None
    ):
        return False
    username = request_auth.get("username")
    password = request_auth.get("password")
    if (len(username) == 0) or (len(password) == 0):
        return False

    user_data = (
        insta485.model.get_db()
        .execute("SELECT username, password " "FROM users ")
        .fetchall()
    )

    user_info = [i for i in user_data if i["username"] == username]
    if len(user_info) == 0:
        return False

    user_password = user_info[0]["password"].split("$")
    if user_info[0]["password"] != calculate_password(user_password, password):
        return False

    return True
