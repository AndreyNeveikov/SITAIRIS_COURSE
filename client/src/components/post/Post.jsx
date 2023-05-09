import "./post.css"
import { Link } from "react-router-dom";

export default function Post({post}) {
  const PF = "http://localhost:5000/images/"
    return (
        <div className="post">
            {/*{post?.content}*/}
          {post.photo ? (
        <img className="postImg" src={PF + post.photo} alt="" />)
        :  (<img className="postImg" src="https://i.pinimg.com/564x/d8/6c/ff/d86cfffe02f86626c379cfc38ede363b.jpg" alt="" />
          )}
        <div className="postInfo">
        <div className="postCats">
         {post.tags?.map((c) => (
           <span className="postCat">{c.name}</span>
         ))}
        </div>
        <Link to={`/post/${post.id}`} className="link">
        <span className="postTitle">
            {post.content}
        </span>
        </Link>
        <hr />
        {post.created_at &&
        <span className="postDate">{new Date(post.created_at).toDateString()}</span>}
      </div>
        <p className="postDesc">
          {post.content}
      </p>
        </div>
    )
}
