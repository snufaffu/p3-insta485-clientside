import React, { useState, useEffect, useInsertionEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  // console.log("Hello??")
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState(null);
  const [owner, setOwner] = useState(null);
  const [ownerImg, setOwnerImg] = useState(null);
  const [ownerUrl, setOwnerUrl] = useState(null);
  const [postUrl, setPostUrl] = useState(null);
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState({ numLikes: 0, lognameLikesThis: false });
  const [timestamp, setTimestamp] = useState(null);
  const [postID, setPostID] = useState(null);
  // const [postComment, setComment] = useState(0);
  const [humantime, setHumanTime] = useState(() => Date.now());
  const [commentText, setCommentText] = useState("");
  const [commentsUrl, setCommentsUrl] = useState(null);

  const handleLikes = () => {
    // console.log("hello??");
    if (postID == null) {
      // console.log("bad things are happening here");
      return;
    }
    const isCurrentlyLiked = likes.lognameLikesThis;
    let target = `/api/v1/likes/?postid=${postID}`;
    if (isCurrentlyLiked) {
      if (!likes.url) {
        return;
      }
      let likeid = likes.url.split("/")[4];
      target = `/api/v1/likes/${likeid}/`;
    }
    // const notIsCurrentlyLiked = !isCurrentlyLiked;
    const method = isCurrentlyLiked ? "DELETE" : "POST";
    const newNumLikes = isCurrentlyLiked
      ? likes.numLikes - 1
      : likes.numLikes + 1;
    fetch(target, {
      method: method,
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.status === 204 ? {} : response.json();
      })
      .then((data) => {
        console.log("Like API Response:", data);
        setLikes((prev) => ({
          ...prev,
          numLikes: isCurrentlyLiked ? prev.numLikes - 1 : prev.numLikes + 1,
          lognameLikesThis: !isCurrentlyLiked,
          url: data.url || null,
        }));
      })
      .catch((error) => console.error("Error updating likes", error));
  };

  const handleDoubleClick = () => {
    if (!likes.lognameLikesThis) {
      handleLikes();
    }
  };

  const handleSubmitComment = (event) => {
    // Prevent page from reloading
    event.preventDefault();

    // Make sure comments url exists, so we know the url for the REST API
    if (!commentsUrl) {
      return;
    }

    // Get comment text (allow posting an empty comment)
    const text = commentText.trim();
    // if (!text) {
    //   return;
    // }

    // Send new comment to backend using REST API, then add comment to DOM
    fetch(commentsUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        setComments((prev) => [...prev, data]);
        setCommentText("");
      })
      .catch((error) => console.error("Error posting new comment", error));
  };

  const handleDeleteComment = (comment) => {
    fetch(comment.url, { method: "DELETE", credentials: "same-origin" })
      .then((response) => {
        if (response.status !== 204) {
          throw Error(response.statusText);
        }
      })
      .then(() => {
        setComments((prev) =>
          prev.filter((c) => c.commentid !== comment.commentid),
        );
      })
      .catch((error) => console.error("Error deleting comment", error));
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setHumanTime(Date.now());
    }, 60000);

    return () => clearInterval(interval);
  }, []);
  // Declare a boolean flag that we can use to cancel the API request.

  useEffect(() => {
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log("API DATA:", data);
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerImg(data.ownerImgUrl);
          setOwnerUrl(data.ownerShowUrl);
          setPostUrl(data.postShowUrl);
          setComments(data.comments);
          setLikes(data.likes);
          setTimestamp(data.created);
          setPostID(data.postid);
          setCommentsUrl(data.comments_url);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // Render post image and post owner
  return (
    <div className="post">
      <img src={imgUrl} alt="post_image" onDoubleClick={handleDoubleClick} />
      <p>
        <a href={ownerUrl}>
          {" "}
          <img src={ownerImg} alt="owner_image" />{" "}
        </a>
        <a href={ownerUrl}>{owner}</a>
      </p>
      <p>
        <a href={postUrl} data-testid="post-time-ago">
          {humantime && dayjs.utc(timestamp).local().fromNow()}
        </a>
      </p>
      <p>{likes.numLikes == 1 ? "1 like" : `${likes.numLikes} likes`}</p>
      <button
        onClick={handleLikes}
        data-testid="like-unlike-button"
        disabled={postID === null}
      >
        {likes.lognameLikesThis ? "unlike" : "like"}
      </button>
      <div className="comments">
        {comments.map((comment) => (
          <div key={comment.commentid} className="comment">
            <p>
              <a href={comment.ownerShowUrl}>
                <span>{comment.owner}</span>
              </a>
              <span data-testid="comment-text">{comment.text}</span>
              {comment.lognameOwnsThis ? (
                <button
                  type="button"
                  data-testid="delete-comment-button"
                  disabled={postID === null}
                  onClick={() => handleDeleteComment(comment)}
                >
                  Delete comment
                </button>
              ) : null}
            </p>
          </div>
        ))}
      </div>
      <form data-testid="comment-form" onSubmit={handleSubmitComment}>
        <input
          type="text"
          value={commentText}
          disabled={postID === null}
          onChange={(event) => setCommentText(event.target.value)}
        />
      </form>
    </div>
  );
}
