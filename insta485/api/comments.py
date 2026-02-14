"""REST API for comments."""
import flask
import insta485
from insta485.api.main import require_auth_or_403


def _abort_404_if_post_missing(connection, postid: int) -> None:
    cur = connection.execute("SELECT 1 FROM posts WHERE postid = ?", (postid,))
    if cur.fetchone() is None:
        flask.abort(404)


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def create_comment():
    """Create a comment on a post. Return 201 and the new comment object."""
    logname = require_auth_or_403()
    connection = insta485.model.get_db()

    postid = flask.request.args.get("postid", type=int)
    if postid is None:
        flask.abort(400)

    _abort_404_if_post_missing(connection, postid)

    text = None
    if flask.request.is_json:
        data = flask.request.get_json(silent=True) or {}
        text = data.get("text")
    if text is None:
        text = flask.request.form.get("text")
    if text is None:
        flask.abort(400)

    connection.execute(
        "INSERT INTO comments(owner, postid, text) VALUES(?, ?, ?)",
        (logname, postid, text),
    )
    cur = connection.execute("SELECT last_insert_rowid() AS commentid")
    commentid = cur.fetchone()["commentid"]

    resp = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": f"/users/{logname}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/",
    }
    return flask.jsonify(resp), 201


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete a comment. Return 204 on success, 404 if missing, 403 if not owner."""
    logname = require_auth_or_403()
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?",
        (commentid,),
    )
    row = cur.fetchone()
    if row is None:
        flask.abort(404)
    if row["owner"] != logname:
        flask.abort(403)

    connection.execute("DELETE FROM comments WHERE commentid = ?", (commentid,))
    return ("", 204)
