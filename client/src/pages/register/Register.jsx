import axios from "axios";
import { useState } from "react";
import { Link } from "react-router-dom";
import "./register.css";
 import { ToastContainer, toast } from 'react-toastify';
import Cookies from "js-cookie";

export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(false);
    try {
      const res = await axios.post("http://localhost:8000/api/v1/user/", {
        username,
        email,
        password,
      });
      const res1 = await axios.post("http://localhost:8000/api/v1/user/login/", {
        email,
        password,
      });
       console.log( res.data.uuid)
      console.log(res1.data)
      const res2 = await axios.post("http://localhost:8000/api/v1/page/", {
        uuid: res.data.uuid,
        name: username,
        description: username
      }, {headers:
                    {"Authorization": `Bearer ${res1.data.access}`}});
      res.data && window.location.replace("/login");
    } catch (err) {
      setError(true);
    }
  };
  return (
    <div className="register">
      <span className="registerTitle">Registration</span>
      <form className="registerForm" onSubmit={handleSubmit}>
        <label>Username</label>
        <input
          className="registerInput"
          type="text"
          placeholder="Enter your username..."
          onChange={(e) => setUsername(e.target.value)}
        />
        <label>Email</label>
        <input
          className="registerInput"
          type="text"
          placeholder="Enter your email..."
          onChange={(e) => setEmail(e.target.value)}
        />
        <label>Password</label>
        <input
          className="registerInput"
          type="password"
          placeholder="Enter your password..."
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="registerButton"  type="submit">Registrate</button>
      </form>
      <button className="registerLoginButton">
        <Link className="link" to="/login">
          Login
        </Link>
      </button>
      {error && <span style={{color:"red", marginTop:"10px"}}>Something went wrong!</span>}
    </div>
  );
}
