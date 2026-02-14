"""REST API for likes."""
import flask
import insta485
from insta485.api.main import require_auth_or_403


def _abort_404_if_post_missing(connection, postid: int) -> None:
    cur = connection.execute("SELECT 1 FROM posts WHERE postid = ?", (postid,))
    if cur.fetchone() is None:
        flask.abort(404)


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def create_like():
    """Create a like for a post. Return 201 if created, 200 if already exists."""
    logname = require_auth_or_403()
    connection = insta485.model.get_db()

    postid = flask.request.args.get("postid", type=int)
    if postid is None:
        flask.abort(400) 

    _abort_404_if_post_missing(connection, postid)

    cur = connection.execute(
        """
        SELECT likeid
        FROM likes
        WHERE owner = ? AND postid = ?
        """,
        (logname, postid),
    )
    row = cur.fetchone()
    if row is not None:
        likeid = row["likeid"]
        return flask.jsonify({"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"}), 200

    connection.execute(
        "INSERT INTO likes(owner, postid) VALUES(?, ?)",
        (logname, postid),
    )
    cur = connection.execute("SELECT last_insert_rowid() AS likeid")
    likeid = cur.fetchone()["likeid"]
    return flask.jsonify({"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"}), 201


@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def delete_like(likeid):
    """Delete a like. Return 204 on success, 404 if missing, 403 if not owner."""
    logname = require_auth_or_403()
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT owner FROM likes WHERE likeid = ?",
        (likeid,),
    )
    row = cur.fetchone()
    if row is None:
        flask.abort(404)
    if row["owner"] != logname:
        flask.abort(403)

    connection.execute("DELETE FROM likes WHERE likeid = ?", (likeid,))
    return ("", 204)
