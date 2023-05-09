import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import "./sidebar.css";

export default function Sidebar() {
  const [cats, setCats] = useState([]);

  useEffect(() => {
    const getCats = async () => {
      const res = await axios.get("/categories");
      setCats(res.data);
    };
    getCats();
  }, []);
  return (
    <div className="sidebar">
      <div className="sidebarItem">
        <span className="sidebarTitle">ABOUT ME</span>
        <img
          src="https://i.pinimg.com/564x/6b/48/22/6b4822681acb45a01b63f43ca9335945.jpg"
          alt=""
        />
        <p>
          Hi there! It's my first blog app. 
          Hope u'll enjoy my project!
        </p>
      </div>
      <div className="sidebarItem">
        <span className="sidebarTitle">CATEGORIES</span>
        <ul className="sidebarList">
        {cats.map((c) => (
            <Link to={`/?cat=${c.name}`} className="link">
            <li className="sidebarListItem">{c.name}</li>
            </Link>
          ))}
        </ul>
      </div>
      <div className="sidebarItem">
        <span className="sidebarTitle">FOLLOW ME</span>
        <div className="sidebarSocial">
            <a href="https://vk.com/andrenalin_n">
                <i className="sidebarIcon fab fa-vk"></i>
            </a>
            <a href="https://github.com/AndreyNeveikov">
                <i className="sidebarIcon fab fa-github"></i>
            </a>
            <a href="https://www.instagram.com/andrenalin_n/">
                <i className="sidebarIcon fab fa-instagram"></i>
            </a>
        </div>
      </div>
    </div>
  );
}