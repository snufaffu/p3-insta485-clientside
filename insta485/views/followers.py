"""Insta485 followers view."""

import flask
import insta485


@insta485.app.route("/users/<user_url_slug>/followers/")
def show_followers(user_url_slug):
    """Display followers page."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    connection = insta485.model.get_db()
    logname = flask.session["username"]

    exists = connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (user_url_slug,),
    ).fetchone()
    if exists is None:
        flask.abort(404)

    followers = connection.execute(
        """
        SELECT u.username, u.fullname, u.filename
        FROM following f
        JOIN users u ON u.username = f.follower
        WHERE f.followee = ?
        ORDER BY u.username ASC
        """,
        (user_url_slug,),
    ).fetchall()

    follower_cards = []
    for row in followers:
        username = row["username"]
        relationship = ""
        is_following = False
        if username != logname:
            rel = connection.execute(
                "SELECT 1 FROM following WHERE follower = ? AND followee = ?",
                (logname, username),
            ).fetchone()
            is_following = rel is not None
            relationship = "following" if is_following else "not following"

        follower_cards.append(
            {
                "username": username,
                "fullname": row["fullname"],
                "filename": row["filename"],
                "relationship": relationship,
                "is_following": is_following,
            }
        )

    context = {
        "logname": logname,
        "user_url_slug": user_url_slug,
        "followers": follower_cards,
    }
    return flask.render_template("followers.html", **context)
