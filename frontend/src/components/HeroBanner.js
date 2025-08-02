// src/components/HeroBanner.js
import React from "react";
import LoginButton from "../components/LoginButton";
import SidebarDrawer from "../../src/features/sidebar/SidebarDrawer";
import '@fontsource/luckiest-guy';
import '@fontsource/bangers';
import { Link } from "react-router-dom";
import "../styles/HeroBanner.css";

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
      <div className="hero-banner-content">
        <h1 className="hero-banner-title">
          <Link to="/">Nerd.com</Link>
        </h1>
      </div>
    </div>
  );
}
