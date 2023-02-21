"""
Insta485 view.

URLs include:

"""
import flask
import insta485
import pathlib
import uuid
import hashlib
import datetime
import base64
import os
import arrow

app = flask.Flask(__name__)


@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Display a post."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    else:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()

        if login_query["is_user"] < 1:
            return flask.redirect(flask.url_for('show_login'))

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(postid) AS is_post "
        "FROM posts "
        "WHERE postid == ? ",
        (postid_url_slug, )
    )
    login_query = cur.fetchone()

    if login_query["is_post"] < 1:
        flask.abort(404)
    logname = flask.session['username']

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
        (postid_url_slug, )
    )
    post_info = cur.fetchone()

    cur = connection.execute(
        "SELECT COUNT(l.likeid) AS likes "
        "FROM posts AS p "
        "LEFT JOIN likes AS l ON l.postid = p.postid "
        "WHERE p.postid == ? ",
        (postid_url_slug, )
    )
    likes_amt = cur.fetchone()

    cur = connection.execute(
        "SELECT COUNT(l.likeid) AS liked_by "
        "FROM posts AS p "
        "LEFT JOIN likes AS l ON l.postid = p.postid "
        "WHERE p.postid == ? AND l.owner == ? ",
        (postid_url_slug, logname, )
    )
    logged_likes = cur.fetchone()

    cur = connection.execute(
        "SELECT c.owner AS owner, "
        "c.text AS text, "
        "c.commentid AS commentid "
        "FROM comments AS c "
        "WHERE c.postid == ? "
        "ORDER BY c.commentid ASC ",
        (postid_url_slug, )
    )
    comments = cur.fetchall()

    fmt = "YYYY-MM-DD HH:mm:ss"
    humanized = arrow.get(post_info["timestamp"], fmt)
    humanized = humanized.humanize()

    context = {"logname": logname,
               "postid": post_info["postid"],
               "owner": post_info["owner"],
               "owner_img_url": post_info["owner_img_url"],
               "img_url": post_info["img_url"],
               "timestamp": humanized,
               "likes": likes_amt["likes"],
               "liked_by": logged_likes["liked_by"],
               "comments": comments}
    return flask.render_template('post.html', **context)


@insta485.app.route('/likes/', methods=['POST'])
def likes():
    """Update a like in the database."""
    if 'username' not in flask.session:
        flask.abort(403)
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()

        if login_query["is_user"] < 1:
            flask.abort(403)
        cur = connection.execute(
                "SELECT COUNT(likeid) as has_liked "
                "FROM likes "
                "WHERE postid == ? AND owner == ? ",
                (flask.request.form.get("postid"), flask.session['username'], )
        )
        like_query = cur.fetchone()
        if flask.request.form.get("operation") == 'like':
            if like_query["has_liked"] > 0:
                flask.abort(409)
            cur = connection.execute(
                "INSERT INTO likes "
                "(owner, postid, created) "
                "VALUES (?, ?, CURRENT_TIMESTAMP) ",
                (flask.session['username'], flask.request.form.get("postid"), )
            )
        elif flask.request.form.get("operation") == 'unlike':
            if like_query["has_liked"] < 1:
                flask.abort(409)
            cur = connection.execute(
                "DELETE FROM likes "
                "WHERE postid == ? AND owner == ? ",
                (flask.request.form.get("postid"), flask.session['username'])
            )
        if "target" in flask.request.args:
            return flask.redirect(flask.request.args["target"])
        else:
            return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/comments/', methods=['POST'])
def comments():
    """Update a comment in the database."""
    if 'username' not in flask.session:
        flask.abort(403)
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()
        if login_query["is_user"] < 1:
            flask.abort(403)
        if flask.request.form.get("operation") == 'create':
            if flask.request.form.get("text") == "":
                flask.abort(400)
            username = flask.session['username']
            postid = flask.request.form.get("postid")
            text = flask.request.form.get("text")
            cur = connection.execute(
                "INSERT INTO comments "
                "(owner, postid, text, created) "
                "VALUES (?, ?, ?, CURRENT_TIMESTAMP) ",
                (username, postid, text,)
            )
        elif flask.request.form.get("operation") == 'delete':
            username = flask.session['username']
            commentid = flask.request.form.get("commentid")
            cur = connection.execute(
                "SELECT COUNT(commentid) as has_comment, "
                "owner "
                "FROM comments "
                "WHERE commentid == ? AND owner == ? ",
                (commentid, username, )
            )
            comment_query = cur.fetchone()
            if comment_query["has_comment"] < 1:
                flask.abort(403)
            cur = connection.execute(
                "DELETE FROM comments "
                "WHERE commentid == ? AND owner == ? ",
                (commentid, username, )
            )
        else:
            flask.abort(403)
        if "target" in flask.request.args:
            return flask.redirect(flask.request.args["target"])
        else:
            return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/posts/', methods=['POST'])
def posts():
    """Update a post in the database."""
    if 'username' not in flask.session:
        flask.abort(403)
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()
        if login_query["is_user"] < 1:
            flask.abort(403)
        username = flask.session['username']
        if flask.request.form.get("operation") == 'create':
            if 'file' in flask.request.files:
                upload_dir = insta485.app.config["UPLOAD_FOLDER"]

                file = flask.request.files['file']
                filename = file.filename

                stem = uuid.uuid4().hex
                suffix = pathlib.Path(filename).suffix.lower()
                uuid_name = f"{stem}{suffix}"
                path = upload_dir/uuid_name
                file.save(path)

                username = flask.session['username']
                cur = connection.execute(
                    "INSERT INTO posts (filename, owner, created) "
                    "VALUES (?, ?, CURRENT_TIMESTAMP) ",
                    (uuid_name, username, )
                )
            else:
                flask.abort(400)
        elif flask.request.form.get("operation") == 'delete':
            postid = flask.request.form.get("postid")
            cur = connection.execute(
                "SELECT filename, COUNT(owner) as is_owner "
                "FROM posts "
                "WHERE postid == ? AND owner == ? ",
                (postid, username, )
            )
            file_query = cur.fetchone()
            if file_query["is_owner"] < 1:
                flask.abort(403)

            upload_dir = insta485.app.config["UPLOAD_FOLDER"]
            os.remove(upload_dir/file_query["filename"])

            cur = connection.execute(
                "DELETE FROM posts "
                "WHERE postid == ? ",
                (postid, )
            )
        else:
            flask.abort(403)
        if "target" in flask.request.args:
            return flask.redirect(flask.request.args["target"])
        else:
            return flask.redirect(flask.url_for('show_user',
                                  user_url_slug=flask.session['username']))
