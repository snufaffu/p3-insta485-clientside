"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if "username" not in flask.session:
        return flask.redirect("/accounts/login/")

    # # Connect to database
    # connection = insta485.model.get_db()

    # Query database (most stuff from p2 commented out)
    logname = flask.session["username"]
    # print(f"logged in user: {logname}")
    # cur = connection.execute(
    #     """
    #     SELECT postid, filename, owner, created
    #     FROM posts
    #     WHERE owner = ?
    #        OR owner IN (
    #            SELECT followee
    #            FROM following
    #            WHERE follower = ?
    #        )
    #     ORDER BY postid DESC
    #     """,
    #     (logname, logname),
    # )

    # post_rows = cur.fetchall()

    # posts = []
    # for post in post_rows:
    #     postid = post["postid"]

    #     # Owner icon
    #     cur = connection.execute(
    #         "SELECT filename FROM users WHERE username = ?",
    #         (post["owner"],),
    #     )
    #     owner_row = cur.fetchone()
    #     owner_img = owner_row["filename"]

    #     # Likes
    #     cur = connection.execute(
    #         "SELECT COUNT(*) AS num_likes FROM likes WHERE postid = ?",
    #         (postid,),
    #     )
    #     num_likes = cur.fetchone()["num_likes"]

    #     cur = connection.execute(
    #         "SELECT 1 FROM likes WHERE postid = ? AND owner = ?",
    #         (postid, logname),
    #     )
    #     logname_likes_this = cur.fetchone() is not None

    #     # Comments
    #     cur = connection.execute(
    #         """
    #         SELECT commentid, owner, text
    #         FROM comments
    #         WHERE postid = ?
    #         ORDER BY commentid ASC
    #         """,
    #         (postid,),
    #     )
    #     comments = cur.fetchall()

    #     posts.append(
    #         {
    #             "postid": postid,
    #             "owner": post["owner"],
    #             "owner_img": owner_img,
    #             "post_img": post["filename"],
    #             "created_human": arrow.get(post["created"]).humanize(),
    #             "num_likes": num_likes,
    #             "logname_likes_this": logname_likes_this,
    #             "comments": comments,
    #         }
    #     )

    context = {
            "logname": logname,
            # "posts": posts,
    }
    return flask.render_template("index.html", **context)
