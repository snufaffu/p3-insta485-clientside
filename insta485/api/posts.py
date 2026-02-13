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

@insta485.app.route("/api/v1/posts/<int:postid_url_slug>/", methods=["GET"])
def get_post(postid_url_slug):
    """Return details for one post."""
    logname = require_auth_or_403()
    connection = insta485.model.get_db()

    cur = connection.execute(
        """
        SELECT p.postid, p.filename AS post_filename, p.owner, p.created,
                u.filename AS owner_filename
        FROM posts AS p
        JOIN users AS u
          ON p.owner = u.username
        WHERE p.postid = ?
        """,
        (postid_url_slug,),
    )
    post = cur.fetchone()
    if post is None:
        flask.abort(404)

    cur = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid ASC
        """,
        (postid_url_slug,),
    )
    comment_rows = cur.fetchall()
    comments = []
    for row in comment_rows:
        owner = row["owner"]
        comments.append({
            "commentid": row["commentid"],
            "lognameOwnsThis": (owner == logname),
            "owner": owner,
            "ownerShowUrl": f"/users/{owner}/",
            "text": row["text"],
            "url": f"/api/v1/comments/{row['commentid']}/",
        })

    cur = connection.execute(
        "SELECT COUNT(*) AS numLikes FROM likes WHERE postid = ?",
        (postid_url_slug,),
    )
    num_likes = cur.fetchone()["numLikes"]

    cur = connection.execute(
        """
        SELECT likeid
        FROM likes
        WHERE postid = ? AND owner = ?
        """,
        (postid_url_slug, logname),
    )
    like_row = cur.fetchone()
    logname_likes = like_row is not None
    like_url = f"/api/v1/likes/{like_row['likeid']}/" if logname_likes else None

    context = {
        "comments": comments,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": post["created"],
        "imgUrl": f"/uploads/{post['post_filename']}",
        "likes": {
            "lognameLikesThis": logname_likes,
            "numLikes": num_likes,
            "url": like_url,
        },
        "owner": post["owner"],
        "ownerImgUrl": f"/uploads/{post['owner_filename']}",
        "ownerShowUrl": f"/users/{post['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": flask.request.path,
    }
    return flask.jsonify(**context)