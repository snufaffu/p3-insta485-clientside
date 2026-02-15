import React, { useState, useEffect } from "react";
import Post from "./post";

export default function Feed() {
  const [postUrls, setPostUrls] = useState([]);

  useEffect(() => {
    let ignoreStaleRequest = false;
    fetch("/api/v1/posts/", { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          if (data && data.results) {
            const urls = data.results.map((post) => post.url);
            setPostUrls(urls);
          }
        }
      })
      .catch((error) => console.log(error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, []);

  console.log("Current postUrls in state:", postUrls);
  return (
    <div className="feed">
      {postUrls.map((url) => (
        <Post key={url} url={url} />
      ))}
    </div>
  );
}
