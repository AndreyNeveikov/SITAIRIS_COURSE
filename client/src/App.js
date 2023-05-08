import TopBar from "./components/topbar/topbar";
import Homepage from "./pages/homepage/Home";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Write from "./pages/write/Write";
import Settings from "./pages/settings/Settings";
import Login from "./pages/login/Login";
import Register from "./pages/register/Register";
import Single from "./pages/single/Single";
import {useContext} from "react"
import {Context} from "./context/Context"
import {ToastContainer} from "react-toastify";

function App() {
  const {user} = useContext(Context);
  console.log(user)
  return (
    <Router>
    <TopBar/>
        <ToastContainer />
    <Routes>
        <Route exact path="/" element={<Homepage />}/>
        <Route path="/posts" element={<Homepage />}/>
        <Route path="/register" element={user ?  <Homepage /> :  <Register />}/>
        <Route path="/login" element={user ? <Homepage /> : <Login />}/>
        <Route path="/post/:id" element={<Single />}/>
        <Route path="/write" element={user ? <Write /> : <Login />}/>
        <Route path="/settings" element={user ? <Settings /> : <Login />}/>
      </Routes>
    </Router>
  );
}

export default App;
