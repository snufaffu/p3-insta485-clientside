"""Insta485 user profile view."""

import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/")
def show_user(user_url_slug):
    """Display user profile page."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    connection = insta485.model.get_db()

    logname = flask.session["username"]

    user = connection.execute(
        "SELECT username, fullname, filename FROM users WHERE username = ?",
        (user_url_slug,),
    ).fetchone()
    if user is None:
        flask.abort(404)

    # Posts
    posts = connection.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner = ? ORDER BY postid DESC",
        (user_url_slug,),
    ).fetchall()

    # Counts
    num_posts = connection.execute(
        "SELECT COUNT(*) AS n FROM posts WHERE owner = ?",
        (user_url_slug,),
    ).fetchone()["n"]

    num_followers = connection.execute(
        "SELECT COUNT(*) AS n FROM following WHERE followee = ?",
        (user_url_slug,),
    ).fetchone()["n"]

    num_following = connection.execute(
        "SELECT COUNT(*) AS n FROM following WHERE follower = ?",
        (user_url_slug,),
    ).fetchone()["n"]

    # Relationship
    relationship = ""
    is_following = False
    if logname != user_url_slug:
        row = connection.execute(
            "SELECT 1 FROM following WHERE follower = ? AND followee = ?",
            (logname, user_url_slug),
        ).fetchone()
        is_following = row is not None
        relationship = "following" if is_following else "not following"

    context = {
        "logname": logname,
        "user": user,
        "posts": posts,
        "num_posts": num_posts,
        "num_followers": num_followers,
        "num_following": num_following,
        "relationship": relationship,
        "is_following": is_following,
        "is_own_page": (logname == user_url_slug),
    }
    return flask.render_template("user.html", **context)
