// src/components/HeroBanner.js
import React from "react";
import LoginButton from "../components/LoginButton";
import SidebarDrawer from "../../src/features/sidebar/SidebarDrawer";
import "@fontsource/luckiest-guy";
import "@fontsource/bangers";
import { Link } from "react-router-dom";
import "../styles/HeroBanner.css";
import rawTypeLogo from "../assets/rawtype-logo2.png";

export default function HeroBanner() {
  const loggedIn = !!localStorage.getItem("token");
  const role = localStorage.getItem("role") || "";

  return (
    <div className="hero-banner">
      {/* 右上角按鈕群組 */}
      <div className="hero-banner-actions">
        {!loggedIn && <LoginButton />}
        <SidebarDrawer loggedIn={loggedIn} role={role} />
      </div>

      {/* 主內容區 */}
      <div className="hero-banner-content">
        <Link to="/" className="hero-banner-logo">
          <img src={rawTypeLogo} alt="RawType Logo" />
        </Link>
      </div>
    </div>
  );
}
