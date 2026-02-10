"""
Account-related routes.

Uses:
Insta485
/accounts/login/ view
/accounts/create/ view
/accounts/delete/ view
/accounts/edit/ view
/accounts/password/ view
/accounts/show_auth/ view
/accounts/logout/ post
/accounts/?target=URL post
"""
import pathlib
import uuid
import hashlib
import flask
import insta485


@insta485.app.route("/accounts/login/", methods=["GET"])
def show_login():
    """..."""
    # If already logged in, redirect to index
    if "username" in flask.session:
        return flask.redirect("/")

    # Generate html
    context = {}
    return flask.render_template("login.html", **context)


@insta485.app.route("/accounts/create/", methods=["GET"])
def show_create():
    """..."""
    # If already logged in, redirect to edit
    if "username" in flask.session:
        return flask.redirect("/accounts/edit/")

    # Generate html
    context = {}
    return flask.render_template("create.html", **context)


@insta485.app.route("/accounts/delete/", methods=["GET"])
def show_delete():
    """..."""
    # If not yet logged in, abort 403
    if "username" not in flask.session:
        flask.abort(403)

    # Get session username
    username = flask.session["username"]

    # Generate html
    context = {"logname": username}
    return flask.render_template("delete.html", **context)


@insta485.app.route("/accounts/edit/", methods=["GET"])
def show_edit():
    """..."""
    # If not yet logged in, abort 403
    if "username" not in flask.session:
        flask.abort(403)

    # Get session username
    username = flask.session["username"]

    # Connect to database
    connection = insta485.model.get_db()

    # Get user info
    cur = connection.execute(
        "SELECT fullname, email, filename "
        "FROM users "
        "WHERE username = ? ",
        (username,)
    )
    row = cur.fetchone()
    if row is None:
        flask.abort(403)
    fullname = row["fullname"]
    email = row["email"]
    user_photo = row["filename"]

    # Generate html
    context = {"logname": username, "fullname": fullname, "email": email,
               "user_photo": user_photo}
    return flask.render_template("edit.html", **context)


@insta485.app.route("/accounts/password/", methods=["GET"])
def show_password():
    """..."""
    # If not yet logged in, abort 403
    if "username" not in flask.session:
        flask.abort(403)

    # Get session username
    username = flask.session["username"]

    # Generate html
    context = {"logname": username}
    return flask.render_template("password.html", **context)


@insta485.app.route("/accounts/auth/", methods=["GET"])
def show_auth():
    """..."""
    # If logged in, return 200 status code with no content
    # If not logged in, abort 403
    if "username" in flask.session:
        return flask.Response(status=200)
    flask.abort(403)


@insta485.app.route("/accounts/logout/", methods=["POST"])
def get_logout():
    """..."""
    # Clear flask session
    flask.session.clear()

    # Redirect to /accounts/login
    return flask.redirect("/accounts/login/")


def verify_password(connection, username, password):
    """..."""
    # Fetch password_db_string corresponding to username
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ? ",
        (username,)
    )
    row = cur.fetchone()
    if row is None:
        flask.abort(403)
    password_db_string = row["password"]

    # Split password_db_string into algorithm, salt, password_hash
    try:
        algorithm, salt, stored_password_hash = password_db_string.split("$")
    except ValueError:
        flask.abort(403)

    # Process password
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    computed_password_hash = hash_obj.hexdigest()

    # Authenticate password
    if computed_password_hash != stored_password_hash:
        flask.abort(403)


def process_password(password):
    """..."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def operation_login():
    """..."""
    # Take in fields
    username = flask.request.form.get("username", "").strip()
    password = flask.request.form.get("password", "")

    # Make sure no fields are empty
    if not (username and password):
        flask.abort(400)

    # Connect to database
    connection = insta485.model.get_db()

    # Verify password
    verify_password(connection, username, password)

    # Update session
    flask.session["username"] = username


def operation_create():
    """..."""
    # Take in fields
    photo = flask.request.files.get("file")
    fullname = flask.request.form.get("fullname", "").strip()
    username = flask.request.form.get("username", "").strip()
    email = flask.request.form.get("email", "").strip()
    password = flask.request.form.get("password", "")

    # Make sure no fields are empty
    if not (photo and photo.filename and fullname and
            username and email and password):
        flask.abort(400)

    # Connect to database
    connection = insta485.model.get_db()

    # Make sure username isn't taken
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username = ? ",
        (username,)
    )
    if cur.fetchone() is not None:
        flask.abort(409)

    # Process photo (using code from spec)
    photo_filename = photo.filename

    stem = uuid.uuid4().hex
    suffix = pathlib.Path(photo_filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    photo.save(path)

    # Process password
    password_db_string = process_password(password)

    # Add account to database
    connection.execute(
        "INSERT INTO users (username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?) ",
        (username, fullname, email, uuid_basename, password_db_string)
    )

    # Update session
    flask.session["username"] = username


def operation_delete():
    """..."""
    # If not yet logged in, abort 403
    if "username" not in flask.session:
        flask.abort(403)

    # Connect to database
    connection = insta485.model.get_db()

    # Get session username
    username = flask.session["username"]

    # Get uploads directory
    upload_dir = insta485.app.config["UPLOAD_FOLDER"]

    # Delete photo file
    cur = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ? ",
        (username,)
    )
    row = cur.fetchone()
    if row is not None:
        try:
            (upload_dir / row["filename"]).unlink()
        except FileNotFoundError:
            pass

    # Delete any post image files
    cur = connection.execute(
        "SELECT filename "
        "FROM posts "
        "WHERE owner = ? ",
        (username,)
    )
    all_rows = cur.fetchall()
    for row in all_rows:
        try:
            (upload_dir / row["filename"]).unlink()
        except FileNotFoundError:
            pass

    # Delete account from database
    connection.execute(
        "DELETE FROM users "
        "WHERE username = ? ",
        (username,)
    )

    # Clear session
    flask.session.clear()


def operation_edit_account():
    """..."""
    # If not yet logged in, abort 403
    if "username" not in flask.session:
        flask.abort(403)

    # Get session username
    username = flask.session["username"]

    # Get uploads directory
    upload_dir = insta485.app.config["UPLOAD_FOLDER"]

    # Take in fields
    photo = flask.request.files.get("file")
    fullname = flask.request.form.get("fullname", "").strip()
    email = flask.request.form.get("email", "").strip()

    # Make sure fullname and email field aren't empty
    if not (fullname and email):
        flask.abort(400)

    # Connect to database
    connection = insta485.model.get_db()

    if photo and photo.filename:
        # Delete previous photo file
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ? ",
            (username,)
        )
        row = cur.fetchone()
        if row is not None:
            try:
                (upload_dir / row["filename"]).unlink()
            except FileNotFoundError:
                pass

        # Process photo (using code from spec)
        photo_filename = photo.filename

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(photo_filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        photo.save(path)

        # Update filename, fullname, email in database
        connection.execute(
            "UPDATE users "
            "SET filename = ?, fullname = ?, email = ? "
            "WHERE username = ? ",
            (uuid_basename, fullname, email, username)
        )
    else:
        # Update fullname, email in database
        connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ? ",
            (fullname, email, username)
        )


def operation_update_password():
    """..."""
    # If not yet logged in, abort 403
    if "username" not in flask.session:
        flask.abort(403)

    # Get session username
    username = flask.session["username"]

    # Take in fields
    password = flask.request.form.get("password", "")
    new_password1 = flask.request.form.get("new_password1", "")
    new_password2 = flask.request.form.get("new_password2", "")

    # Make sure no fields are empty
    if not (password and new_password1 and new_password2):
        flask.abort(400)

    # Connect to database
    connection = insta485.model.get_db()

    # Verify old password
    verify_password(connection, username, password)

    # Verify new passwords match
    if new_password1 != new_password2:
        flask.abort(401)

    # Process password
    password_db_string = process_password(new_password1)

    # Update password in database
    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ? ",
        (password_db_string, username)
    )


@insta485.app.route("/accounts/", methods=["POST"])
def get_accounts():
    """..."""
    # Get operation type
    operation = flask.request.form.get("operation")

    if operation == "login":
        operation_login()
    elif operation == "create":
        operation_create()
    elif operation == "delete":
        operation_delete()
    elif operation == "edit_account":
        operation_edit_account()
    elif operation == "update_password":
        operation_update_password()

    # Get target
    target = flask.request.args.get("target")

    # Redirect to target if it exists; otherwise, redirect to index
    if target is None:
        return flask.redirect("/")
    return flask.redirect(target)
