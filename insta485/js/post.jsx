import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImg, setOwnerImg] = useState("");
  const [ownerUrl, setOwnerUrl] = useState("");
  const [postUrl, setPostUrl] = useState("");
  const [comments, setComments] = useState([]);
  const [likes, setLikes] = useState({ numLikes: 0, lognameLikesThis: false });
  const [timestamp, setTimestamp] = useState("");
  const [postComment, setComment] = useState("");

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
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
      <img src={imgUrl} alt="post_image" />
      <p>
        <a href={ownerUrl}>
          {" "}
          <img src={ownerImg} alt="owner_image" />{" "}
        </a>
        <a href={ownerUrl}>{owner}</a>
      </p>
      <p>
        <a href={postUrl}>{timestamp}</a>
      </p>
      <p>{likes.numLikes == 1 ? "1 like" : `${likes.numLikes} likes`}</p>
      <div className="comments">
        {comments.map((comment) => (
          <div key={comment.commentid} className="comment">
            <p>
              <a href={comment.ownerShowUrl}>
                <p>{comment.owner}</p>
              </a>
              {comment.text}
            </p>
          </div>
        ))}
        
      </div>
    </div>
  );
}
