import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export function LikeButton({ isLiked, onClicked }) {
  /* Display image and post owner of a single post */

  console.log(
    "Like component rendered as " + (isLiked ? "Unlike" : "Like") + " "
  );
  // Render post image and post owner
  if (isLiked) {
    return (
      <button className="like-unlike-button" onClick={onClicked}>
        Unlike
      </button>
    );
  } else {
    return (
      <button className="like-unlike-button" onClick={onClicked}>
        Like
      </button>
    );
  }
}

export default function Likes({
  lognameLikesThis,
  likesAmount,
  likesUrl,
  handleLikeClicked,
}) {
  /* Display image and post owner of a single post */
  // Render post image and post owner

  console.log(
    "Like component made with input " +
      lognameLikesThis +
      " " +
      likesAmount +
      " " +
      likesUrl
  );

  if (likesAmount === 1) {
    return (
      <div className="likes">
        {" "}
        {likesAmount} like{" "}
        <LikeButton isLiked={lognameLikesThis} onClicked={handleLikeClicked} />{" "}
      </div>
    );
  } else {
    return (
      <div className="likes">
        {" "}
        {likesAmount} likes{" "}
        <LikeButton isLiked={lognameLikesThis} onClicked={handleLikeClicked} />{" "}
      </div>
    );
  }
}
