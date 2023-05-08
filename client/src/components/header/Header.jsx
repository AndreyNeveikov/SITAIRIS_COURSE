import "./header.css";

export default function Header() {
    return (
        <div className="header">
        <div className="headerTitles">
          <span className="headerTitleSm">Innotter</span>
          <span className="headerTitleLg">BLOG</span>
        </div>
        <img
          className="headerImg"
          src="https://i.pinimg.com/564x/26/bc/2e/26bc2e1574c86990ec9f14ccd14a0378.jpg"
          alt=""
        />
      </div>
    )
}
