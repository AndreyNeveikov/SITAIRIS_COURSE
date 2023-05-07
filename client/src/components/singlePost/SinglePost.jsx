import { Link, useLocation } from "react-router-dom";
import "./singlePost.css";
import axios from "axios";
import { useContext, useEffect, useState } from "react";
import { Context } from "../../context/Context";

export default function SinglePost() {
  const PF = "http://localhost:5000/images/";
  const { user } = useContext(Context);
  const path = useLocation().pathname.split("/")[2];
  const [post, setPost] = useState({})
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [updateMode, setUpdateMode] = useState(false);

  useEffect(()=>{
    const getPosts = async ()=>{
       const res = await axios.get("/posts/"+path)
       setPost(res.data)
       setTitle(res.data.title)
       setDescription(res.data.description)
    }
    getPosts()
  }, [path]);

const handleDelete = async () => {
  try {
    await axios.delete(`/posts/${post._id}`, {
      data: { username: user.username },
    });
    window.location.replace("/");
  } catch (err) {}
};

const handleUpdate = async () => {
  try {
    await axios.put(`/posts/${post._id}`, {
      username: user.username,
      title,
      description,
    });
    setUpdateMode(false)
  } catch (err) {}
};

  return (
    <div className="singlePost">
      <div className="singlePostWrapper">
      {post.photo ? (
        <img className="singlePostImg" src={PF + post.photo} alt="" />)
        :  (<img className="singlePostImg" src="https://i.pinimg.com/564x/d8/6c/ff/d86cfffe02f86626c379cfc38ede363b.jpg" alt="" />
          )}
        {updateMode ? (
          <input
            type="text"
            value={title}
            className="singlePostTitleInput"
            autoFocus
            onChange={(e) => setTitle(e.target.value)}
          />
        ) : (
        <h1 className="singlePostTitle">
          {title}
          {post.username === user.username && (
          <div className="singlePostEdit">
            <i className="singlePostIcon far fa-edit" onClick={() => setUpdateMode(true)}></i>
            <i className="singlePostIcon far fa-trash-alt" onClick={handleDelete}></i>
          </div>)}
        </h1> 
        )}
        <div className="singlePostInfo">
        <Link className="link" to={`/posts?username=${post.username}`}>
          <span>
            Author:
            <b className="singlePostAuthor">
                {post.username}
            </b>
          </span>
          </Link>
          <span className="singlePostDate">{new Date(post.createdAt).toDateString()}</span>
        </div>
        {updateMode ? (
          <textarea
            className="singlePostDescInput"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        ) : (
          <p className="singlePostDesc">{description}</p>
        )}
        {updateMode && (
          <button className="singlePostButton" onClick={handleUpdate}>
            Update
          </button>
        )}
      </div>
    </div>
  );
}