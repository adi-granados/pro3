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


@insta485.app.route("/api/v1/")
def get_api():
    """Get api."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)


@insta485.app.route("/api/v1/posts/")
def get_posts():
    """Return post on postid."""
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
      "SELECT MAX(P.postid) AS postid " "FROM Posts AS P ")
    post_query = cur.fetchone()
    max_post = post_query["postid"]
    temp_post = max_post
    if flask.request.args.get("postid_lte"):
        max_post = flask.request.args.get("postid_lte")
        if max_post is None:
            max_post = temp_post

    max_size = flask.request.args.get("size", default=10, type=int)

    if max_size < 0:
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400

    chosen_page = flask.request.args.get("page", default=0, type=int)

    if chosen_page < 0:
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400

    cur = connection.execute(
        "SELECT p.postid AS postid, p.owner AS owner "
        "FROM users AS u "
        "LEFT JOIN posts AS p ON p.owner = u.username "
        "WHERE p.postid <= ? "
        "ORDER BY p.postid DESC "
        "LIMIT ? OFFSET ? ",
        (
            max_post,
            max_size,
            max_size * (chosen_page),
        ),
    )
    posts = cur.fetchall()

    next_page = chosen_page + 1

    if max_size > len(posts):
        next_url = ""
    else:
        next_url = "/api/v1/posts/?size={}&page={}&postid_lte={}".format(
            max_size, next_page, max_post
        )

    postsinfo = []
    for post in posts:
        cur = connection.execute(
            "SELECT COUNT(f.username2) AS follows "
            "FROM following AS f "
            "WHERE f.username1 == ? AND f.username2 == ? ",
            (
                username,
                post["owner"],
            ),
        )
        follow_amt = cur.fetchone()

        if_follows = follow_amt["follows"]

        if if_follows > 0 or username == post["owner"]:
            postsinfo.append(
                {
                    "postid": post["postid"],
                    "url": "/api/v1/posts/{}/".format(post["postid"]),
                }
            )

    full_path = flask.request.full_path
    if flask.request.path == full_path[:-1]:
        full_path = flask.request.path
    context = {"next": next_url, "results": postsinfo, "url": full_path}

    return flask.jsonify(**context)


@insta485.app.route("/api/v1/posts/<int:postid_url_slug>/")
def get_post(postid_url_slug):
    """Return post on postid."""
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
        "SELECT COUNT(postid) AS is_post " "FROM posts " "WHERE postid == ? ",
        (postid_url_slug,),
    )
    post_query = cur.fetchone()

    if post_query["is_post"] < 1:
        context = {"message": "Not Found", "status_code": 404}
        return flask.jsonify(**context), 404

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT p.postid AS postid, "
        "p.filename AS img_url, "
        "p.owner AS owner, "
        "p.created AS timestamp, "
        "u.filename as owner_img_url "
        "FROM users AS u "
        "JOIN posts AS p ON p.owner = u.username "
        "WHERE p.postid == ?",
        (postid_url_slug,),
    )
    post_info = cur.fetchone()

    cur = connection.execute(
        "SELECT COUNT(l.likeid) AS likes "
        "FROM posts AS p "
        "LEFT JOIN likes AS l ON l.postid = p.postid "
        "WHERE p.postid == ? ",
        (postid_url_slug,),
    )
    likes_amt = cur.fetchone()

    cur = connection.execute(
        "SELECT COUNT(l.likeid) AS liked_by, l.likeid AS l_id "
        "FROM posts AS p "
        "LEFT JOIN likes AS l ON l.postid = p.postid "
        "WHERE p.postid == ? AND l.owner == ? ",
        (
            postid_url_slug,
            username,
        ),
    )
    logged_likes = cur.fetchone()

    cur = connection.execute(
        "SELECT c.commentid AS commentid, "
        "c.owner AS owner, "
        "c.text AS text, "
        "c.commentid AS commentid "
        "FROM comments AS c "
        "WHERE c.postid == ? "
        "ORDER BY c.commentid ASC ",
        (postid_url_slug,),
    )
    comments = cur.fetchall()

    commentsInfo = []
    for comment in comments:
        cur = connection.execute(
            "SELECT COUNT(c.owner) AS is_owner "
            "FROM comments AS c "
            "WHERE c.commentid == ? AND c.owner == ? ",
            (comment["commentid"], username),
        )
        owner_query = cur.fetchone()

        is_owner = False
        if owner_query["is_owner"] > 0:
            is_owner = True

        commentsInfo.append(
            {
                "commentid": comment["commentid"],
                "lognameOwnsThis": is_owner,
                "owner": comment["owner"],
                "ownerShowUrl": "/users/{}/".format(comment["owner"]),
                "text": comment["text"],
                "url": "/api/v1/comments/{}/".format(comment["commentid"]),
            }
        )

    if logged_likes["liked_by"] < 1:
        likesUrl = None
        log_likes = False
    else:
        likesUrl = "/api/v1/likes/{}/".format(logged_likes["l_id"])
        log_likes = True

    context = {
        "comments": commentsInfo,
        "comments_url": "/api/v1/comments/?postid={}"
        .format(post_info["postid"]),
        "created": post_info["timestamp"],
        "imgUrl": "/uploads/{}".format(post_info["img_url"]),
        "likes": {
            "lognameLikesThis": log_likes,
            "numLikes": likes_amt["likes"],
            "url": likesUrl,
        },
        "owner": post_info["owner"],
        "ownerImgUrl": "/uploads/{}".format(post_info["owner_img_url"]),
        "ownerShowUrl": "/users/{}/".format(post_info["owner"]),
        "postShowUrl": "/posts/{}/".format(post_info["postid"]),
        "postid": post_info["postid"],
        "url": "/api/v1/posts/{}/".format(post_info["postid"]),
    }

    return flask.jsonify(**context)
