import {useContext, useState} from "react"
import {Context} from "../../context/Context"
import './topbar.css'
import { Link } from "react-router-dom";
import axios from "axios";

export default function Topbar() {
    const { user, dispatch } = useContext(Context);
    const PF = "http://localhost:5000/images/"
    const [query, setQuery] = useState('')
    const handleLogout = () => {
      dispatch({ type: "LOGOUT" });
    };

    const handleSearch = async () => {
        let res = await axios.get(`http://0.0.0.0:8000/api/v1/search/?search=${query}`)
    }
    return (
        <div className="top">
            <div className='topLeft'>
                <a href="https://vk.com/andrenalin_n">
                    <i className="topIcon fab fa-vk"></i>
                </a>
                <a href="https://github.com/AndreyNeveikov">
                    <i className="topIcon fab fa-github"></i>
                </a>
                <a href="https://www.instagram.com/andrenalin_n/">
                    <i className="topIcon fab fa-instagram"></i>
                </a>
            </div>

            <div className='topCenter'>
                <ul className="topList">
                    <li className="topListItem">
                        <Link className="link" to="/">HOME</Link>
                    </li>
                    <li className="topListItem">ABOUT</li>
                    <li className="topListItem">CONTACT</li>
                    <li className="topListItem">
                        <Link className="link" to="/write">WRITE</Link>
                    </li>
                    {user && <li className="topListItem" onClick={handleLogout}>LOGOUT</li>}
                    </ul>
            </div>

            <div className='topRight'>
                {user ? (
                     <Link className="link" to="/settings"> 
                    <img  className="topImg"
                        src={user.profilePic ? PF+user.profilePic : "https://i.pinimg.com/564x/0e/7f/c4/0e7fc4e07efc98590d6bf008b79ec9a8.jpg"}
                        alt=""
                    />
                     </Link> 
                 ) : ( 
                <ul className="topList">
                    <li className="topListItem">
                         <Link className="link" to="/login"> LOGIN </Link> 
                    </li>
                    <li className="topListItem">
                         <Link className="link" to="/register"> REGISTER </Link> 
                    </li>
                </ul>
                )}
                <div className="topRight">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search..."
                    />
                     <Link to={`/?search=${query}`} className="link">
                         <i className="topSearchIcon fas fa-search" ></i>
                     {/*    onClick={handleSearch}*/}
                     </Link>
                </div>
            </div>
        </div>
    )
}
