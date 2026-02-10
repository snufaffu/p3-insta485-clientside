"""
User Following view.

URLs include:
/users/<user_url_slug>/following/
"""

import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/following/', methods=["GET"])
def show_following(user_url_slug):
    """Display following page."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    connection = insta485.model.get_db()
    logname = flask.session["username"]
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug,)
    )
    user_check = cur.fetchone()
    if not user_check:
        flask.abort(404)

    cur = connection.execute(
        "SELECT u.username, u.filename AS user_img_url "
        "FROM users u "
        "JOIN following f ON u.username = f.followee "
        "WHERE f.follower = ?",
        (user_url_slug,)
    )
    following_list = cur.fetchall()

    for user in following_list:
        cur = connection.execute(
            "SELECT 1 FROM following WHERE follower = ? AND followee = ?",
            (logname, user['username']),
        )
        user['logname_follows_username'] = cur.fetchone() is not None

    context = {
        "logname": logname,
        "following": following_list,
        "user_url_slug": user_url_slug,
    }
    return flask.render_template("following.html", **context)
