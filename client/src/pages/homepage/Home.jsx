import "./home.css";
import Header from "../../components/header/Header";
import Posts from "../../components/posts/Posts";
import Sidebar from "../../components/sidebar/Sidebar";
import SinglePost from "../../components/singlePost/SinglePost";
import Single from "../single/Single";
import axios from "axios";
import { useEffect, useState } from "react";
import { useLocation } from "react-router";
import Cookies from 'js-cookie';


export default function Home() {
  const [posts, setPosts] = useState([]);
  const { search } = useLocation();

  useEffect(() => {
    const fetchPosts = async () => {
      console.log(search)
      if (search.includes('search') || search.includes('cat')){
        const res = await axios.get(`http://localhost:8000/api/v1/search/?search=${search.split('=')[1]}`, {
          headers:
              {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
        });
        let posts = []
        res.data?.Page?.map(p => {
          posts = [...posts, ...p?.posts.map(post => {
            post.tags = p.tags
            return post
          })]
        })
        setPosts(posts)
        console.log(posts)
      } else {
        const res = await axios.get("http://localhost:8000/api/v1/feed/", {
          headers:
              {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
        });
        setPosts(res.data);
      }
    };
    fetchPosts();
  }, [search]);



  return (
    <>
      <Header />
      <div className="home">
        <Posts posts={posts} />
        <Sidebar />
      </div>
    </>
  );
}
