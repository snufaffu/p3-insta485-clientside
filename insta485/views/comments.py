"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/comments/", methods=["POST"])
def update_comments():
    """..."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    # LOGGER.debug("operation = %s", flask.request.form["operation"])
    # LOGGER.debug("postid = %s", flask.request.form["postid"])
    # LOGGER.debug("commentid = %s", flask.request.form["commentid"])
    # LOGGER.debug("text = %s", flask.request.form["text"])
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()
    logname = flask.session["username"]

    if operation == "delete":
        LOGGER.debug("commentid = %s", flask.request.form["commentid"])
        commentid = flask.request.form["commentid"]

        cur = connection.execute(
            "SELECT owner FROM comments "
            "WHERE commentid = ?",
            (commentid,)
        )
        comment_owner = cur.fetchone()
        LOGGER.debug("DEBUG: logname='%s', db_result=%s",
                     logname, comment_owner)
        if not comment_owner or comment_owner['owner'] != logname:
            flask.abort(403)

        cur = connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid,)
        )

    else:
        LOGGER.debug("postid = %s", flask.request.form["postid"])
        LOGGER.debug("text = %s", flask.request.form["text"])
        text = flask.request.form["text"]
        postid = flask.request.form["postid"]
        if not text:
            flask.abort(400)

        cur = connection.execute(
            "INSERT INTO comments "
            "(owner, postid, text) "
            "VALUES (?, ?, ?)",
            (logname, postid, text)
        )

    target = flask.request.args.get('target')

    if target:
        return flask.redirect(target)

    return flask.redirect('/')
