"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/following/", methods=["POST"])
def update_following():
    """..."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    LOGGER.debug("username = %s", flask.request.form["username"])
    logname = flask.session["username"]
    print(f"DEBUG: Current logname is: {logname}")
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]
    print(f"target user is: {username}")
    if operation == "unfollow":
        cur = connection.execute(
            "SELECT COUNT(*) "
            "FROM following "
            "WHERE follower = ? AND followee = ?",
            (logname, username)
        )
        if cur.fetchone()['COUNT(*)'] == 0:
            return flask.abort(409)

        cur = connection.execute(
            "DELETE FROM following "
            "WHERE follower = ? AND followee = ?",
            (logname, username)
        )
    else:
        cur = connection.execute(
            "SELECT COUNT(*) "
            "FROM following "
            "WHERE follower = ? AND followee = ?",
            (logname, username)
        )
        if cur.fetchone()['COUNT(*)'] != 0:
            return flask.abort(409)
        cur = connection.execute(
            "INSERT INTO following "
            "(follower, followee) "
            "VALUES (?, ?)",
            (logname, username)
        )

    target = flask.request.args.get('target')

    if target:
        return flask.redirect(target)

    return flask.redirect('/')
