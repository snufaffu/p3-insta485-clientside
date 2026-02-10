"""Explore page routes."""
import flask
import insta485


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/explore/", methods=["GET"])
def explore_page():
    """..."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session["username"]
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT u.username, u.filename "
        "FROM users u "
        "LEFT JOIN following f ON u.username = f.followee AND f.follower = ? "
        "WHERE f.followee IS NULL "
        "AND u.username != ?;",
        (logname, logname)
    )

    follow_people = cur.fetchall()

    context = {
        "follow_people": follow_people,
        'logname': logname
    }
    return flask.render_template("explore.html", **context)
