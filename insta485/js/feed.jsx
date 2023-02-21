import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";
import Post from "./post";
import InfiniteScroll from "react-infinite-scroll-component";

export default function Feed({ url }) {
  console.log("Feed object initialized");

  const [allPostsFetched, setPostsFetched] = useState(false);
  const [hasNext, setHasNext] = useState(false);

  const [nextUrl, setNextUrl] = useState("");
  const [posts, setPosts] = useState([]);
  const [requestUrl, setRequestUrl] = useState("");

  function getNext() {
    if (hasNext) {
      console.log("Fetching more posts! from" + nextUrl);
      // Call REST API to get the post's information
      fetch(nextUrl, { credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // If ignoreStaleRequest was set to true, we want to ignore the results of the
          // the request. Otherwise, update the state to trigger a new render.
          setNextUrl(data.next);
          setPosts((prevPosts) => {
            return [...prevPosts, ...data.results];
          });
          setPostsFetched(true);
          if (data.next === "") {
            setHasNext(false);
          } else {
            setHasNext(true);
          }
        })
        .catch((error) => console.log(error));
    }
  }

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
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          console.log("Feed object found data, setting states");
          setNextUrl(data.next);
          setPosts(data.results);
          setRequestUrl(data.url);
          setPostsFetched(true);
          if (data.next === "") {
            setHasNext(false);
          } else {
            setHasNext(true);
          }
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
  console.log("Feed object rendering");
  return (
    <div className="mainPage">
      <div className="navigationbar">
        <span className="leftendtext">
          <a href="/">/</a> insta485
        </span>
      </div>
      <div className="feed">
        <InfiniteScroll
          dataLength={posts.length} // This is important field to render the next data
          next={getNext}
          hasMore={hasNext}
          loader={<h4>Loading...</h4>}
          endMessage={
            <p style={{ textAlign: "center" }}>
              <b>No more posts</b>
            </p>
          }
        >
          {posts.map((item) => (
            <Post
              key={item.postid}
              url={item.url}
              othersFetched={allPostsFetched}
            />
          ))}
        </InfiniteScroll>
      </div>
    </div>
  );
}
