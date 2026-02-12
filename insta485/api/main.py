"""REST API for general functions."""
import flask
import insta485
import hashlib

@insta485.app.route('/api/v1/')
def get_services():
    """Return list of services available."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)

def verify_password(connection, username, password):
    """Verify password against algorithm$salt$hash in DB; abort(403) if wrong."""
    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,),
    )

    row = cur.fetchone()
    if row is None:
        flask.abort(403)

    password_db_string = row["password"]

    try:
        algorithm, salt, stored_password_hash = password_db_string.split("$")
    except ValueError:
        flask.abort(403)

    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        # unknown algorithm in db
        flask.abort(403)

    hash_obj.update((salt + password).encode("utf-8"))
    computed_password_hash = hash_obj.hexdigest()

    if computed_password_hash != stored_password_hash:
        flask.abort(403)


def require_auth_or_403():
    """
    Return logname if authenticated via session or HTTP Basic, else abort(403).
    """
    # Session cookie auth (browser)
    if "username" in flask.session:
        return flask.session["username"]

    # HTTP Basic auth (tests/httpie)
    auth = flask.request.authorization
    if auth is None or not auth.username or not auth.password:
        flask.abort(403)

    connection = insta485.model.get_db()
    verify_password(connection, auth.username, auth.password)
    return auth.username
