"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
import arrow

app = flask.Flask(__name__)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Connect to database
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

    # Query database
    logname = flask.session['username']

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT u.username AS username, "
        "u.filename AS user_img_url "
        "FROM following AS f "
        "JOIN users AS u ON f.username2 = u.username "
        "WHERE f.username1 == ? ",
        (logname, )
    )
    users = cur.fetchall()

    cur = connection.execute(
        "SELECT p.postid AS postid, "
        "p.filename AS img_url, "
        "p.owner AS owner, "
        "p.created AS timestamp, "
        "u.filename as owner_img_url "
        "FROM users AS u "
        "LEFT JOIN posts AS p ON p.owner = u.username "
        "ORDER BY p.postid DESC "
    )
    posts = cur.fetchall()

    postsinfo = []
    for post in posts:

        cur = connection.execute(
            "SELECT COUNT(f.username2) AS follows "
            "FROM following AS f "
            "WHERE f.username1 == ? AND f.username2 == ? ",
            (logname, post["owner"], )
        )
        follow_amt = cur.fetchone()

        if_follows = follow_amt["follows"]

        if (if_follows > 0 or logname == post["owner"]):
            cur = connection.execute(
                "SELECT COUNT(l.likeid) AS likes "
                "FROM posts AS p "
                "LEFT JOIN likes AS l ON l.postid = p.postid "
                "WHERE p.postid == ? ",
                (post["postid"],)
            )
            likes_amt = cur.fetchone()

            cur = connection.execute(
                "SELECT COUNT(l.likeid) AS liked_by "
                "FROM posts AS p "
                "LEFT JOIN likes AS l ON l.postid = p.postid "
                "WHERE p.postid == ? AND l.owner == ? ",
                (post["postid"], logname, )
            )
            logged_likes = cur.fetchone()

            cur = connection.execute(
                "SELECT c.owner AS owner, "
                "c.text AS text, "
                "c.commentid AS commentid "
                "FROM comments AS c "
                "WHERE c.postid == ? "
                "ORDER BY c.commentid ASC ",
                (post["postid"], )
            )
            comments = cur.fetchall()

            fmt = "YYYY-MM-DD HH:mm:ss"
            humanized = arrow.get(post["timestamp"], fmt)
            humanized = humanized.humanize()
            postsinfo.append({"postid": post["postid"],
                              "owner": post["owner"],
                              "owner_img_url": post["owner_img_url"],
                              "img_url": post["img_url"],
                              "timestamp": humanized,
                              "likes": likes_amt["likes"],
                              "liked_by": logged_likes["liked_by"],
                              "comments": comments})

    # Add database info to context
    context = {"logname": logname, "posts": postsinfo}

    return flask.render_template('index.html', **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ page."""
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

    # Query database
    logname = flask.session['username']

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT u.username AS username, "
        "u.filename AS user_img_url "
        "FROM users AS u "
        "WHERE u.username != ? ",
        (logname, )
    )
    all_users = cur.fetchall()

    users = []
    for user in all_users:
        cur = connection.execute(
            "SELECT COUNT(f.username2) as follows "
            "FROM following AS f "
            "WHERE f.username1 == ? AND f.username2 == ? ",
            (logname, user["username"], )
        )
        follow_query = cur.fetchone()

        if follow_query["follows"] < 1:
            users.append(user)

    context = {"logname": logname, "users": users}

    return flask.render_template('explore.html', **context)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
