import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import "./sidebar.css";

export default function Sidebar() {
  const [cats, setCats] = useState([]);

  useEffect(() => {
    const getCats = async () => {
      const res = await axios.get("http://0.0.0.0:8000/api/v1/tag/");
      setCats(res.data);
    };
    getCats();
  }, []);
  return (
    <div className="sidebar">
      <div className="sidebarItem">
        <span className="sidebarTitle">ADVERTISEMENT</span>
        <img
          src="https://storage.pravo.ru/image/193/96731.png?v=1676366029"
          alt=""
        />
        <p>
          Воспользуйтесь новым предложением от наших спосоров!
        </p>
      </div>
      <div className="sidebarItem">
        <span className="sidebarTitle">Key words</span>
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