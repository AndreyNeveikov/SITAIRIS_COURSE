import { Link, useLocation } from "react-router-dom";
import "./singlePost.css";
import axios from "axios";
import { useContext, useEffect, useState } from "react";
import { Context } from "../../context/Context";
import Cookies from "js-cookie";

export default function SinglePost() {
  const PF = "http://localhost:5000/images/";
  const { user } = useContext(Context);
  const path = useLocation().pathname.split("/")[2];
  const [post, setPost] = useState({})
  const [page, setPage] = useState({})
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [updateMode, setUpdateMode] = useState(false);
  const [author, setAuthor] = useState("privat page");
  const [liked, setLiked] = useState(false);
  const [likes, setLikes] = useState(0);

  useEffect(()=>{
    const getPosts = async ()=>{
      console.log(user)
      const res = await axios.get("http://localhost:8000/api/v1/post/" + path,
          {headers: {"Authorization": `Bearer ${Cookies.get("Authorization")}`},})
      console.log(path)

      setPost(res.data)
      setTitle(res.data.title)
      setDescription(res.data.content)
      const author = await axios.get("http://localhost:8000/api/v1/page/" + res.data.page,
          {headers: {"Authorization": `Bearer ${Cookies.get("Authorization")}`},})
      console.log(author.data.name)
      setAuthor(author.data.owner.email)
      setPage(author.data)

      const likes = await axios.get("http://0.0.0.0:8000/api/v1/post/" + path + "/total_likes/",
          {headers: {"Authorization": `Bearer ${Cookies.get("Authorization")}`},})
      setLikes(likes.data.total_likes)
    }
    getPosts()
  }, [path]);

const handleDelete = async () => {
  try {
    await axios.delete(`http://localhost:8000/api/v1/post/${post.id}`, {
      data: { username: user.username },
    });
    window.location.replace("/");
  } catch (err) {}
};

const handleLike = async () => {
  try {
    await axios.get(`http://localhost:8000/api/v1/post/${post.id}/like`, {
      headers: {"Authorization": `Bearer ${Cookies.get("Authorization")}`},
    });
  } catch (err) {}
};

const handleUpdate = async () => {
  try {
    await axios.put(`http://localhost:8000/api/v1/post/${post.id}/`, {
      title,
      content: description,
    }, {
      headers: {"Authorization": `Bearer ${Cookies.get("Authorization")}`}} );
    setUpdateMode(false)
  } catch (err) {}
};

  return (
    <div className="singlePost">
      <div className="singlePostWrapper">
      {page.image ? (
        <img className="singlePostImg" src={page.image} alt="" />)
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
          {author === user.email && (
          <div className="singlePostEdit">
            <i className="singlePostIcon far fa-edit" onClick={() => setUpdateMode(true)}></i>
            <i className="singlePostIcon far fa-trash-alt" onClick={handleDelete}></i>
          </div>)}
        </h1> 
        )}
        <div className="singlePostInfo">
        <Link className="link" to={`/posts?username=${author}`}>
          <span>
            Author:
            <b className="singlePostAuthor">
                {author}
            </b>
          </span>
          </Link>
          <span className="singlePostDate">{new Date(post.created_at).toDateString()}</span>
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
         <button className="singlePostLike" onClick={handleLike}>
            Like: {likes}
         </button>
      </div>
    </div>
  );
}