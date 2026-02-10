"""Insta485 uploads view."""

import pathlib
import flask
import insta485


@insta485.app.route("/uploads/<path:filename>")
def get_upload(filename):
    """Serve a file from var/uploads."""
    # When login is implemented:
    if "username" not in flask.session:
        flask.abort(403)

    upload_folder = insta485.app.config["UPLOAD_FOLDER"]

    # If file does not exist, abort(404)
    path = pathlib.Path(upload_folder) / filename
    if not path.exists():
        flask.abort(404)

    return flask.send_from_directory(upload_folder, filename)
