"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Display likes."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    LOGGER.debug("postid = %s", flask.request.form["postid"])
    logname = flask.session["username"]
    print(f"DEBUG: Current logname is: {logname}")
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]
    print(f"post id is: {postid}")
    if operation == "unlike":
        cur = connection.execute(
            "SELECT COUNT(*) "
            "FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid, logname)
        )
        if cur.fetchone()['COUNT(*)'] == 0:
            return flask.abort(409)

        cur = connection.execute(
            "DELETE FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid, logname)
        )
    else:
        cur = connection.execute(
            "SELECT COUNT(*) "
            "FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid, logname)
        )
        if cur.fetchone()['COUNT(*)'] != 0:
            return flask.abort(409)
        cur = connection.execute(
            "INSERT INTO likes "
            "(postid, owner) "
            "VALUES (?, ?)",
            (postid, logname)
        )

    target = flask.request.args.get('target')

    if target:
        return flask.redirect(target)

    return flask.redirect('/')
