import axios from "axios";
import {Context} from "../../context/Context";
import {useContext, useEffect, useState} from "react";
import "./write.css";
import Cookies from "js-cookie";

export default function Write() {
    const [title, setTitle] = useState("");
    const [description, setDesc] = useState("");
    const [file, setFile] = useState(null);
    const [tags, setTags] = useState([]);
    const {user} = useContext(Context);

    useEffect(async () => {
        const res1 = await axios.get(
            "http://localhost:8000/api/v1/tag/", {
                headers:
                    {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
            });
        setTags(res1[res1.length - 1].id)
        console.log(res1[res1.length - 1].id)
    }, [])

    const handleSubmit = async (e) => {
        const res1 = await axios.get(
            "http://localhost:8000/api/v1/user/me/", {
                headers:
                    {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
            });
        const res2 = await axios.get(
            `http://0.0.0.0:8000/api/v1/search2/?search=${res1.data.uuid}`, {
                headers:
                    {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
            });
        let pageId = res2.data?.Page[0].id;
        e.preventDefault();
        const newPost = {
            page: pageId,
            title,
            content: description
        };
        // const data = new FormData();
        // // data.append("name", filename);
        // data.append("image", file || null);
        // data.append("page", pageId);
        // data.append("content", title)
        // data.append("reply_to", null)
        try {
            let res = await axios.post("http://localhost:8000/api/v1/post/",   newPost,{
               headers:
                    {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
            });
            // const res = await axios.post("http://localhost:8000/api/v1/post/", {
            //     'Page': 2,
            //     'Content': 'dfgcdsfgh',
            //     'reply_to': null
            // },
            //     {
            //     headers:
            //         {"Authorization": `Bearer ${Cookies.get("Authorization")}`}
            // })
            //     {
            //     'Page': 2,
            //     'Content': 'dfgcdsfgh',
            //     'reply_to': null
            // });

            // window.location.replace("/post/" + res.data.id);
        } catch (err) {
            console.log(err)
        }
    };
    return (
        <div className="write">
            {file && (
                <img className="writeImg" src={URL.createObjectURL(file)} alt=""/>
            )}
            {/*<form className="writeForm" onSubmit={handleSubmit}>*/}
            <div className="writeFormGroup">
                <label htmlFor="fileInput">
                    <i className="writeIcon fas fa-plus"></i>
                </label>
                <input id="fileInput" type="file" style={{display: "none"}}
                       onChange={(e) => setFile(e.target.files[0])}/>
                <input
                    className="writeInput"
                    placeholder="Title"
                    type="text"
                    autoFocus={true}
                    onChange={e => setTitle(e.target.value)}
                />
            </div>
            <div className="writeFormGroup">
          <textarea
              className="writeInput writeText"
              placeholder="Tell your story..."
              type="text"
              onChange={e => setDesc(e.target.value)}
          />
            </div>
            <button className="writeSubmit" onClick={handleSubmit}>
                Publish
            </button>
            {/*</form>*/}
        </div>
    );
}

// https://i.pinimg.com/564x/8c/0d/92/8c0d92b294a9d2bfc5ca3fe6775e4b41.jpg
// pic href