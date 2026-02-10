"""Post routes."""

import pathlib
import uuid
import flask
import arrow
import insta485

LOGGER = flask.logging.create_logger(insta485.app)


def require_login_and_db():
    """
    Redirect to login if not logged in.

    Otherwise return (connection, logname).
    """
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    log = flask.session["username"]
    connection = insta485.model.get_db()

    return connection, log


@insta485.app.route('/posts/<postid_url_slug>/', methods=["GET"])
def show_posts(postid_url_slug):
    """..."""
    result = require_login_and_db()
    if isinstance(result, flask.Response):
        return result
    connection, logname = result

    cur = connection.execute(
        """
        SELECT filename AS img_filename, owner, created
        FROM posts
        WHERE postid = ?
        """,
        (postid_url_slug,)
    )
    post = cur.fetchone()

    # print(f"user is {logname}")

    if not post:
        # print(f"post is {post}")
        flask.abort(404)

    cur = connection.execute(
        "SELECT commentid, owner, text, created "
        "FROM comments WHERE postid = ?",
        (postid_url_slug,)
    )
    comments = cur.fetchall()

    cur = connection.execute(
            "SELECT 1 FROM likes WHERE postid = ? AND owner = ?",
            (postid_url_slug, logname),
        )
    logname_likes_this = cur.fetchone() is not None

    cur = connection.execute(
        "SELECT COUNT(*) as count FROM likes WHERE postid = ?",
        (postid_url_slug,)
    )
    num_likes = cur.fetchone()["count"]

    cur = connection.execute(
        "SELECT filename AS user_filename FROM users WHERE username = ?",
        (post["owner"],)
    )
    owner_img_url = cur.fetchone()

    context = {
        "logname": logname,
        "post": post,
        "owner": post["owner"],
        "owner_img_url": f"/uploads/{owner_img_url['user_filename']}",
        "img_url": f"/uploads/{post['img_filename']}",
        "postid": postid_url_slug,
        "timestamp": arrow.get(post["created"]).humanize(),
        "likes": num_likes,
        "comments": comments,
        "logname_likes_this": logname_likes_this
    }

    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=["POST"])
def update_posts():
    """..."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")
    connection = insta485.model.get_db()
    logname = flask.session["username"]
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    operation = flask.request.form["operation"]
    if operation == "create":
        fileobj = flask.request.files["file"]
        if not fileobj:
            flask.abort(400)
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

# Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        cur = connection.execute(
            "INSERT INTO posts "
            "(filename, owner) "
            "VALUES (?, ?)",
            (uuid_basename, logname)
        )
        target = flask.request.args.get('target')
        if target:
            return flask.redirect(target)

        return flask.redirect(f'/users/{logname}/')

    postid = flask.request.form['postid']
    cur = connection.execute(
        "SELECT owner, filename "
        "FROM posts "
        "WHERE postid = ?",
        (postid,)
    )
    post = cur.fetchone()
    if post['owner'] != logname:
        flask.abort(403)

    uuid_basename = post['filename']
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    path.unlink()
    cur = connection.execute(
        "DELETE FROM posts "
        "WHERE filename = ? ",
        (uuid_basename,)
    )
    target = flask.request.args.get('target')
    if target:
        return flask.redirect(target)

    return flask.redirect(f'/users/{logname}/')
