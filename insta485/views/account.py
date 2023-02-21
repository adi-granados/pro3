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


@insta485.app.route('/accounts/', methods=['POST'])
def accounts():
    """Display / route."""
    if flask.request.method == 'POST':
        if flask.request.form.get("operation") == 'login':
            if (flask.request.form.get("username") == ""
                    or flask.request.form.get("password") == ""):
                flask.abort(400)
            else:
                username = flask.request.form.get("username")
                connection = insta485.model.get_db()
                cur = connection.execute(
                    "SELECT COUNT(username) as is_user, "
                    "u.username as queried_name, "
                    "u.password as hashed_password "
                    "FROM users AS u "
                    "WHERE u.username == ?",
                    (username, )
                )
                login_query = cur.fetchone()

                if login_query["is_user"] < 1:
                    flask.abort(403)

                hash = login_query["hashed_password"]
                # print(login_query)
                split_hash = hash.split("$")
                # print(split_hash)
                salt_from_hash = split_hash[1]
                # print(salt_from_hash)

                algorithm = 'sha512'
                salt = salt_from_hash
                hash_obj = hashlib.new(algorithm)
                password_salted = salt + flask.request.form.get("password")
                hash_obj.update(password_salted.encode('utf-8'))
                password_hash = hash_obj.hexdigest()
                password_db_string = "$".join([algorithm, salt, password_hash])

                if password_db_string == login_query["hashed_password"]:
                    # print("Password matched! Loging in")
                    flask.session['username'] = username
                else:
                    # print("Password is not a match!")
                    flask.abort(403)
        elif flask.request.form.get("operation") == 'create':
            if flask.request.form.get("username") == "":
                flask.abort(400)
            username = flask.request.form.get("username")
            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT COUNT(username) as is_user, "
                "u.username as queried_name "
                "FROM users AS u "
                "WHERE u.username == ? ",
                (username, )
            )
            login_query = cur.fetchone()

            if login_query["is_user"] < 1:

                if flask.request.form.get("password") == "":
                    flask.abort(400)
                if flask.request.form.get("fullname") == "":
                    flask.abort(400)
                if flask.request.form.get("email") == "":
                    flask.abort(400)
                if flask.request.form.get("file") == "":
                    flask.abort(400)

                if 'file' not in flask.request.files:
                    flask.abort(403, 'file not provided')
                file = flask.request.files['file']
                filename = file.filename

                stem = uuid.uuid4().hex
                suffix = pathlib.Path(filename).suffix.lower()
                uuid_name = f"{stem}{suffix}"

                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_name
                file.save(path)

                algorithm = 'sha512'
                salt = uuid.uuid4().hex
                hash_obj = hashlib.new(algorithm)
                password_salted = salt + flask.request.form.get("password")
                hash_obj.update(password_salted.encode('utf-8'))
                password_hash = hash_obj.hexdigest()
                p_db_string = "$".join([algorithm, salt, password_hash])

                username = flask.request.form.get("username")
                fullname = flask.request.form.get("fullname")
                email = flask.request.form.get("email")

                cur = connection.execute(
                    "INSERT INTO users "
                    "(username, fullname, email, "
                    "filename, password, created) "
                    "VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP) ",
                    (username, fullname, email, uuid_name, p_db_string, )
                )
                flask.session['username'] = flask.request.form.get("username")

            else:
                flask.abort(409)
        elif flask.request.form.get("operation") == 'delete':
            if 'username' not in flask.session:
                flask.abort(403)
            else:
                connection = insta485.model.get_db()
                cur = connection.execute(
                    "SELECT COUNT(username) as is_user "
                    "FROM users AS u "
                    "WHERE u.username == ?",
                    (flask.session['username'], )
                )
                login_query = cur.fetchone()

                if login_query["is_user"] < 0:
                    flask.abort(403)
                cur = connection.execute(
                    "SELECT username, filename "
                    "FROM users "
                    "WHERE username == ? ",
                    (flask.session['username'], )
                )
                userinfo = cur.fetchone()
                filename = userinfo["filename"]
                upload_dir = insta485.app.config["UPLOAD_FOLDER"]
                os.remove(upload_dir/filename)
                cur = connection.execute(
                    "SELECT filename "
                    "FROM posts "
                    "WHERE owner == ? ",
                    (flask.session['username'], )
                )
                userposts = cur.fetchall()

                for post in userposts:
                    os.remove(upload_dir/post["filename"])
                cur = connection.execute(
                    "DELETE FROM users WHERE username == ? ",
                    (flask.session['username'], )
                )
                flask.session.clear()
        elif flask.request.form.get("operation") == 'edit_account':
            if "username" not in flask.session:
                flask.abort(403)
            else:
                connection = insta485.model.get_db()
                cur = connection.execute(
                    "SELECT COUNT(username) as is_user "
                    "FROM users AS u "
                    "WHERE u.username == ?",
                    (flask.session['username'], )
                )
                login_query = cur.fetchone()

                if login_query["is_user"] < 0:
                    flask.abort(403)
                fullname = flask.request.form.get("fullname")
                email = flask.request.form.get("email")
                if (fullname == "" or email == ""):
                    flask.abort(400)
                else:
                    if 'file' in flask.request.files:
                        cur = connection.execute(
                            "SELECT filename "
                            "FROM users "
                            "WHERE username == ? ",
                            (flask.session['username'], )
                        )
                        user_file = cur.fetchone()

                        upload_dir = insta485.app.config["UPLOAD_FOLDER"]
                        os.remove(upload_dir/user_file["filename"])
                        file = flask.request.files['file']
                        filename = file.filename

                        stem = uuid.uuid4().hex
                        suffix = pathlib.Path(filename).suffix.lower()
                        uuid_name = f"{stem}{suffix}"

                        # Save to disk
                        path = upload_dir/uuid_name
                        file.save(path)

                        username = flask.session['username']
                        fullname = flask.request.form.get("fullname")
                        email = flask.request.form.get("email")

                        cur = connection.execute(
                            "UPDATE users "
                            "SET fullname = ?, email = ?, filename = ? "
                            "WHERE username == ? ",
                            (fullname, email, uuid_name, username)
                        )
                    else:

                        username = flask.session['username']
                        fullname = flask.request.form.get("fullname")
                        email = flask.request.form.get("email")
                        cur = connection.execute(
                            "UPDATE users "
                            "SET fullname = ?, email = ? "
                            "WHERE username == ? ",
                            (fullname, email, username)
                        )
        elif flask.request.form.get("operation") == 'update_password':
            if "username" not in flask.session:
                flask.abort(403)
            else:
                connection = insta485.model.get_db()
                cur = connection.execute(
                    "SELECT COUNT(username) as is_user, "
                    "password AS hashed_password "
                    "FROM users AS u "
                    "WHERE u.username == ?",
                    (flask.session['username'], )
                )
                login_query = cur.fetchone()

                if login_query["is_user"] < 0:
                    flask.abort(403)
                elif flask.request.form.get("password") == "":
                    flask.abort(400)
                elif flask.request.form.get("new_password1") == "":
                    flask.abort(400)
                elif flask.request.form.get("new_password2") == "":
                    flask.abort(400)
                else:
                    hash = login_query["hashed_password"]
                    split_hash = hash.split("$")
                    salt_from_hash = split_hash[1]
                    algorithm = 'sha512'
                    salt = salt_from_hash
                    hash_obj = hashlib.new(algorithm)
                    password = flask.request.form.get("password")
                    password_salted = salt + password
                    hash_obj.update(password_salted.encode('utf-8'))
                    p_hash = hash_obj.hexdigest()
                    p_db_string = "$".join([algorithm, salt, p_hash])
                    if p_db_string == login_query["hashed_password"]:
                        new1 = flask.request.form.get("new_password1")
                        new2 = flask.request.form.get("new_password2")
                        if new1 == new2:
                            salt = uuid.uuid4().hex
                            hash_obj = hashlib.new(algorithm)
                            password = flask.request.form.get("new_password1")
                            password_salted = salt + password
                            hash_obj.update(password_salted.encode('utf-8'))
                            p_hash = hash_obj.hexdigest()
                            p_db_string = "$".join([algorithm, salt, p_hash])

                            cur = connection.execute(
                                "UPDATE users "
                                "SET password = ? "
                                "WHERE username == ? ",
                                (p_db_string, flask.session['username'])
                            )
                        else:
                            flask.abort(401)
                    else:
                        flask.abort(403)
        else:
            flask.abort(403)
        if "target" in flask.request.args:
            return flask.redirect(flask.request.args["target"])
        else:
            return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/uploads/<filename>')
def insert_image(filename):
    """Display the file at route."""
    if 'username' not in flask.session:
        flask.abort(403)
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
            flask.abort(403)

        cur = connection.execute(
            "SELECT COUNT(postid) as is_file "
            "FROM posts "
            "WHERE filename == ?",
            (filename, )
        )
        post_query = cur.fetchone()

        cur = connection.execute(
            "SELECT COUNT(username) as is_file "
            "FROM users "
            "WHERE filename == ?",
            (filename, )
        )
        user_query = cur.fetchone()
        is_file = post_query["is_file"]
        is_user = user_query["is_file"]

        if is_file < 1 and is_user < 1:
            flask.abort(404)

        upload_dir = insta485.app.config['UPLOAD_FOLDER']
        return flask.send_from_directory(upload_dir, filename)


@insta485.app.route('/accounts/login/')
def show_login():
    """Display /accounts/login/ page."""
    if 'username' in flask.session:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()
        if login_query["is_user"] > 0:
            return flask.redirect(flask.url_for('show_index'))

    context = {}
    return flask.render_template('login.html', **context)


@insta485.app.route('/accounts/create/')
def show_create():
    """Display /accounts/create/ page."""
    if 'username' in flask.session:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()

        if login_query["is_user"] > 0:
            return flask.redirect(flask.url_for('show_edit'))
    # Add database info to context
    context = {}
    return flask.render_template('create.html', **context)


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Display /accounts/edit/ page."""
    if 'username' in flask.session:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user, "
            "filename, fullname, email "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()
        if login_query["is_user"] < 1:
            return flask.redirect(flask.url_for('log_out'))
        else:
            logname = flask.session['username']
            filename = login_query["filename"]
            fullname = login_query["fullname"]
            email = login_query["email"]
            context = {"logname": logname, "filename": filename,
                       "fullname": fullname, "email": email}
            return flask.render_template('edit.html', **context)
    else:
        return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Display /accounts/delete/ page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']
    context = {"logname": logname}
    return flask.render_template('delete.html', **context)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def log_out():
    """Log the current user out and redirect them."""
    flask.session.clear()
    return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/password/')
def show_password():
    """Display /accounts/password/ page."""
    if 'username' in flask.session:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(username) as is_user "
            "FROM users AS u "
            "WHERE u.username == ?",
            (flask.session['username'], )
        )
        login_query = cur.fetchone()

        if login_query["is_user"] < 1:
            return flask.redirect(flask.url_for('log_out'))
        else:
            logname = flask.session['username']
            context = {"logname": logname}
            return flask.render_template('password.html', **context)
    else:
        return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Display user's page."""
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
            return flask.redirect(flask.url_for('log_out'))

    logname = flask.session['username']

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT u.username AS username, "
        "u.fullname AS fullname, "
        "COUNT(username) as is_user "
        "FROM users AS u "
        "WHERE u.username == ?",
        (user_url_slug, )
    )
    login_query = cur.fetchone()

    if login_query["is_user"] < 1:
        flask.abort(404)

    cur = connection.execute(
        "SELECT COUNT(p.postid) as total_posts "
        "FROM posts AS p "
        "WHERE p.owner == ? ",
        (user_url_slug, )
    )
    total_posts = cur.fetchone()

    cur = connection.execute(
        "SELECT p.postid AS postid, "
        "p.filename AS img_url "
        "FROM posts AS p "
        "WHERE p.owner == ? "
        "ORDER BY p.postid DESC ",
        (user_url_slug, )
    )
    posts = cur.fetchall()

    cur = connection.execute(
            "SELECT COUNT(f.username2) AS is_following "
            "FROM following AS f "
            "WHERE f.username1 == ? AND f.username2 == ? ",
            (logname, user_url_slug, )
    )
    is_following = cur.fetchone()

    cur = connection.execute(
            "SELECT COUNT(f.username2) AS following "
            "FROM following AS f "
            "WHERE f.username1 == ? ",
            (user_url_slug, )
    )
    following = cur.fetchone()

    cur = connection.execute(
            "SELECT COUNT(f.username1) AS followers "
            "FROM following AS f "
            "WHERE f.username2 == ? ",
            (user_url_slug, )
    )
    followers = cur.fetchone()

    username = login_query["username"]
    fullname = login_query["fullname"]
    is_follow = is_following["is_following"]
    total_p = total_posts["total_posts"]
    total_f = followers["followers"]
    total_fn = following["following"]
    context = {"logname": logname, "username": username,
               "fullname": fullname, "is_following": is_follow,
               "total_posts": total_p, "followers": total_f,
               "following": total_fn, "posts": posts}
    return flask.render_template('user.html', **context)


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_followers(user_url_slug):
    """Display user's followers ."""
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
            return flask.redirect(flask.url_for('log_out'))

    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT u.username AS username, "
        "u.fullname AS fullname, "
        "COUNT(username) as is_user "
        "FROM users AS u "
        "WHERE u.username == ?",
        (user_url_slug, )
    )
    login_query = cur.fetchone()

    if login_query["is_user"] < 1:
        flask.abort(404)

    cur = connection.execute(
        "SELECT u.username AS username, "
        "u.filename AS user_img_url "
        "FROM users AS u "
        "JOIN following AS f ON f.username1 = u.username "
        "WHERE f.username2 == ? "
        "ORDER BY u.username ASC ",
        (user_url_slug, )
    )
    followers_initial = cur.fetchall()

    followers_final = []
    for user in followers_initial:
        cur = connection.execute(
            "SELECT COUNT(f.username2) AS logged_follows "
            "FROM following AS f "
            "WHERE f.username1 == ? AND f.username2 == ? ",
            (logname, user["username"], )
        )
        logged_follows = cur.fetchone()

        username = user["username"]
        user_img_url = user["user_img_url"]
        logged_follows = logged_follows["logged_follows"]

        followers_final.append({"username": username,
                                "user_img_url": user_img_url,
                                "logged_follows": logged_follows})

    context = {"logname": logname,
               "username": user_url_slug,
               "followers": followers_final}
    return flask.render_template('followers.html', **context)


@insta485.app.route('/users/<user_url_slug>/following/')
def show_following(user_url_slug):
    """Display who user is following."""
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
            return flask.redirect(flask.url_for('log_out'))

    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT u.username AS username, "
        "u.fullname AS fullname, "
        "COUNT(username) as is_user "
        "FROM users AS u "
        "WHERE u.username == ?",
        (user_url_slug, )
    )
    login_query = cur.fetchone()
    if login_query["is_user"] < 1:
        flask.abort(404)
    cur = connection.execute(
            "SELECT u.username AS username, "
            "u.filename AS user_img_url "
            "FROM users AS u "
            "JOIN following AS f ON f.username2 == u.username "
            "WHERE f.username1 == ? "
            "ORDER BY u.username ",
            (user_url_slug, )
    )
    following_initial = cur.fetchall()

    following_final = []
    for user in following_initial:
        cur = connection.execute(
            "SELECT COUNT(f.username2) AS logged_follows "
            "FROM following AS f "
            "WHERE f.username1 == ? AND f.username2 == ? ",
            (logname, user["username"], )
        )
        logged_follows = cur.fetchone()

        username = user["username"]
        user_img_url = user["user_img_url"]
        logged_follows = logged_follows["logged_follows"]
        following_final.append({"username": username,
                                "user_img_url": user_img_url,
                                "logged_follows": logged_follows})

    context = {"logname": logname,
               "username": user_url_slug,
               "following": following_final}
    return flask.render_template('following.html', **context)


@insta485.app.route('/following/', methods=['POST'])
def following():
    """Update a following status in the database."""
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
        target = flask.request.form.get("username")

        if username == target:
            flask.abort(409)

        cur = connection.execute(
            "SELECT COUNT(username2) AS follows "
            "FROM following "
            "WHERE username1 == ? AND username2 == ? ",
            (username, target, )
        )
        follow_query = cur.fetchone()

        if flask.request.form.get("operation") == 'follow':
            if follow_query["follows"] > 0:
                flask.abort(409)
            cur = connection.execute(
                "INSERT INTO following "
                "(username1, username2, created) "
                "VALUES (?, ?, CURRENT_TIMESTAMP) ",
                (username, target, )
            )
        elif flask.request.form.get("operation") == 'unfollow':
            if follow_query["follows"] < 1:
                flask.abort(409)
            cur = connection.execute(
                "DELETE FROM following "
                "WHERE username1 == ? AND username2 == ? ",
                (username, target, )
            )
        else:
            flask.abort(403)
        if "target" in flask.request.args:
            return flask.redirect(flask.request.args["target"])
        else:
            return flask.redirect(flask.url_for('show_index'))
