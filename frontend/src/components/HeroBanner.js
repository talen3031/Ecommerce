// src/components/HeroBanner.js
import LoginButton from "../components/LoginButton";
import SidebarDrawer from "../../src/features/sidebar/SidebarDrawer";
import '@fontsource/luckiest-guy';
import '@fontsource/bangers';
import { Link } from "react-router-dom";
export default function HeroBanner() {
  // 判斷登入狀態
  const loggedIn = !!localStorage.getItem("token");
  const role = localStorage.getItem("role") || "";

  return (
    <div style={{
      background: 'linear-gradient(135deg, #090909ff 0%, #0d0d0dff 100%)',
      padding: '22px 0 12px',
      textAlign: 'center',
      color: 'white',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* 右上角按鈕群組（並排、永遠貼在 Banner 右上角，垂直置中） */}
      <div style={{
        position: "absolute",
        top: "50%",
        right: 36,
        transform: "translateY(-50%)",
        zIndex: 2,
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        gap: 8
      }}>
        {/* LoginButton 只在未登入時顯示 */}
        {!loggedIn && <LoginButton />}
        {/* SidebarDrawer 漢堡菜單（一直顯示） */}
        <SidebarDrawer loggedIn={loggedIn} role={role} />
        
      </div>

      {/* 主要內容 */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 20px'
      }}>
        
        <h1 style={{
        fontFamily: "'Bangers', cursive",
        color: "#FFD900",
        fontSize: "clamp(4rem, 6vw, 4rem)",
        letterSpacing: "-0.02em",
        margin: 0,
        textShadow: `
          -3px -3px 0 #E0341B,
          2px -2px 0 #E0341B,
          -2px  2px 0 #E0341B,
          2px  2px 0 #E0341B,
          0px  3px 0 #E0341B,
          0px -3px 0 #E0341B
        `
      }}>
        <Link to="/" style={{
          color: "#FFD900",
          textDecoration: "none",
          cursor: "pointer"
        }}>
          Nerd.com
        </Link>
</h1>
      </div>
    </div>
  );
}
