"""REST API for posts."""
import flask
import insta485
from insta485.api.main import require_auth_or_403

def _bad_request():
    """Abort with 400."""
    flask.abort(400)

@insta485.app.route("/api/v1/posts/", methods=["GET"])
def get_posts():
    """Return newest posts for logged-in user's feed with pagination."""
    logname = require_auth_or_403()
    connection = insta485.model.get_db()

    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get("postid_lte", default=None, type=int)

    if size is None or size <= 0:
        _bad_request()
    if page is None or page < 0:
        _bad_request()

    if postid_lte is None:
        cur = connection.execute("SELECT MAX(postid) AS maxid FROM posts")
        row = cur.fetchone()
        postid_lte = row["maxid"] if row and row["maxid"] is not None else 0

    offset = page * size

    cur = connection.execute(
        """
        SELECT p.postid
        FROM posts AS p
        WHERE p.postid <= ?
          AND (
            p.owner = ?
            OR p.owner IN (
              SELECT followee
              FROM following
              WHERE follower = ?
            )
          )
        ORDER BY p.postid DESC
        LIMIT ? OFFSET ?;
        """,
        (postid_lte, logname, logname, size, offset),
    )
    posts = cur.fetchall()

    results = [
        {"postid": row["postid"], "url": f"/api/v1/posts/{row['postid']}/"}
        for row in posts
    ]

    if len(results) < size:
        next_url = ""
    else:
        next_url = f"/api/v1/posts/?size={size}&page={page+1}&postid_lte={postid_lte}"

    url = flask.request.path
    qs = flask.request.query_string.decode("utf-8")
    if qs:
        url = f"{url}?{qs}"

    return flask.jsonify({
        "next": next_url,
        "results": results,
        "url": url,
    })