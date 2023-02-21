import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export function PostImage({ url, handleDoubleClick }) {
  /* Display image and post owner of a single post */

  return (
    <div className="Image">
      <img src={url} alt="" onDoubleClick={handleDoubleClick} />
    </div>
  );
}
