import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Likes, { LikeButton } from "./like";

import { PostImage } from "./postimg";
import moment from "moment";
import Comments from "./comment";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url, othersFetched }) {
  /* Display image and post owner of a single post */
  console.log("Post object initialized");

  const [comments, setComments] = useState([]);
  const [commentsUrl, setCommentsUrl] = useState("");
  const [created, setCreated] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [lognameLikes, setLognameLikes] = useState(false);
  const [numLikes, setNumLikes] = useState(0);
  const [likesUrl, setLikesUrl] = useState("");

  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [postId, setPostId] = useState("");

  const [likesApiUrl, setLikesApiUrl] = useState("");
  const [commentsApiUrl, setCommentsApiUrl] = useState("");

  function OnPostDoubleLiked() {
    if (!lognameLikes) {
      console.log("Like button clicked! User doesn't like so we are liking");

      // Call REST API to get the post's information
      fetch(likesApiUrl + postId, {
        credentials: "same-origin",
        method: "POST",
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // If ignoreStaleRequest was set to true, we want to ignore the results of the
          // the request. Otherwise, update the state to trigger a new render.
          setLognameLikes(true);
          setLikesUrl(data.url);
          setNumLikes(numLikes + 1);
        })
        .catch((error) => console.log(error));
    }
  }

  function OnPostLiked() {
    if (lognameLikes) {
      console.log(
        "Like button clicked! User already likes, so we are unliking"
      );
      // Call REST API to get the post's information
      fetch(likesUrl, { credentials: "same-origin", method: "DELETE" })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response;
        })
        .then(() => {
          // If ignoreStaleRequest was set to true, we want to ignore the results of the
          // the request. Otherwise, update the state to trigger a new render.
          setLognameLikes(false);
          setNumLikes(numLikes - 1);
        })
        .catch((error) => console.log(error));
    } else {
      console.log("Like button clicked! User doesn't like so we are liking");

      // Call REST API to get the post's information
      fetch(likesApiUrl + postId, {
        credentials: "same-origin",
        method: "POST",
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // If ignoreStaleRequest was set to true, we want to ignore the results of the
          // the request. Otherwise, update the state to trigger a new render.
          setLognameLikes(true);
          setLikesUrl(data.url);
          setNumLikes(numLikes + 1);
        })
        .catch((error) => console.log(error));
    }
  }

  function OnCommentCreated(text) {
    console.log("Comment created!");
    fetch(commentsUrl, {
      credentials: "same-origin",
      method: "POST",
      headers: {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        setComments((prevComments) => {
          return [...prevComments, data];
        });
      })
      .catch((error) => console.log(error));
  }

  function OnCommentDeleted(deleteUrl, comment_id) {
    console.log("Comment deleted!");
    fetch(deleteUrl, { credentials: "same-origin", method: "DELETE" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response;
      })
      .then(() => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        setComments(comments.filter((c_id) => c_id.commentid !== comment_id));
      })
      .catch((error) => console.log(error));
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
          console.log("Post object got data");
          setComments(data.comments);
          setCommentsUrl(data.comments_url);
          setCreated(moment.utc(data.created).fromNow());
          setImgUrl(data.imgUrl);
          setLognameLikes(data.likes.lognameLikesThis);
          setNumLikes(data.likes.numLikes);
          setLikesUrl(data.likes.url);
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl);
          setOwnerShowUrl(data.ownerShowUrl);
          setPostShowUrl(data.postShowUrl);
          setPostId(data.postid);
          setLikesApiUrl("/api/v1/likes/?postid=");
          setCommentsApiUrl("/api/v1/comments/?postid=");
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

  if (postId !== "") {
    console.log("Post object rendering");
    return (
      <div className="post">
        <a href={ownerShowUrl}>
          <img src={ownerImgUrl} alt="" /> <p>{owner}</p>
        </a>
        <a href={postShowUrl}> {created} </a>
        <PostImage url={imgUrl} handleDoubleClick={OnPostDoubleLiked} />
        <Likes
          lognameLikesThis={lognameLikes}
          likesAmount={numLikes}
          likesUrl={likesUrl}
          handleLikeClicked={OnPostLiked}
        />
        <Comments
          commentsToShow={comments}
          commentsUrl={commentsUrl}
          handleCommentMade={OnCommentCreated}
          handleCommentDeleted={OnCommentDeleted}
        />
      </div>
    );
  } else {
    console.log("Post object not rendered: id not found");
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
