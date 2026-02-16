import React, { useState, useEffect } from "react";
import Post from "./post";
import InfiniteScroll from "react-infinite-scroll-component";

export default function Feed() {
  const [postUrls, setPostUrls] = useState([]);
  const [nextUrl, setNextUrl] = useState("/api/v1/posts/");
  const [hasMore, setHasMore] = useState(true);

  const fetchMorePosts = () => {
    // Check if there is no next url
    if (!nextUrl) {
      setHasMore(false);
      return;
    }

    // Fetch more posts
    fetch(nextUrl, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) {
          throw Error(response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        if (data && data.results) {
          const urls = data.results.map((post) => post.url);
          setPostUrls((prev) => [...prev, ...urls]);
          setNextUrl(data.next);
          setHasMore(data.next !== "");
        }
      })
      .catch((error) => console.log(error));
  };

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
            setNextUrl(data.next);
            setHasMore(data.next !== "");
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
    <InfiniteScroll
      dataLength={postUrls.length}
      next={fetchMorePosts}
      hasMore={hasMore}
      loader={<h4>Loading...</h4>}
      //   endMessage={
      //     <p style={{ textAlign: "center" }}>
      //       <b>Yay! You have seen it all</b>
      //     </p>
      //   }
    >
      <div className="feed">
        {postUrls.map((url) => (
          <Post key={url} url={url} />
        ))}
      </div>
    </InfiniteScroll>
  );
}
