import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export function Comment({
  commentid,
  lognameOwnsThis,
  owner,
  ownerShowUrl,
  text,
  url,
  handleDeleteClicked,
}) {
  /* Display image and post owner of a single post */
  // Render post image and post owner

  const handleDelete = (event) => {
    handleDeleteClicked(url, commentid);
    // prevents website from refreshing (default action of form submission)
    event.preventDefault();
  };

  if (lognameOwnsThis) {
    return (
      <div className="comment">
        <a href={ownerShowUrl}>{owner}</a>
        <span className="comment-text">{text}</span>
        <button className="delete-comment-button" onClick={handleDelete}>
          Delete comment
        </button>
      </div>
    );
  } else {
    return (
      <div className="comment">
        <a href={ownerShowUrl}>{owner}</a>
        <span className="comment-text">{text}</span>
      </div>
    );
  }
}

export default function Comments({
  commentsToShow,
  commentsUrl,
  handleCommentMade,
  handleCommentDeleted,
}) {
  /* Display image and post owner of a single post */
  // Render post image and post owner

  const [inputValue, setToValue] = useState("");

  const handleChange = (event) => {
    setToValue(event.target.value);
    console.log(event.target.value);
  };

  //function called when user submits
  const handleSubmit = (event) => {
    handleCommentMade(inputValue);
    //prevents website from refreshing (default action of form submission)
    event.preventDefault();
    setToValue("");
  };

  return (
    <div className="comments">
      {commentsToShow.map((item) => (
        <Comment
          key={item.commentid}
          commentid={item.commentid}
          lognameOwnsThis={item.lognameOwnsThis}
          owner={item.owner}
          ownerShowUrl={item.ownerShowUrl}
          text={item.text}
          url={item.url}
          handleDeleteClicked={handleCommentDeleted}
        />
      ))}

      <form className="comment-form" onSubmit={handleSubmit}>
        <input type="text" value={inputValue} onChange={handleChange} />
      </form>
    </div>
  );
}
