import React, { useEffect, useState } from "react";
import { Button } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";

function LoginButton() {
  const navigate = useNavigate();
  const location = useLocation();
  const [show, setShow] = useState(true);

  // Banner高度（依你自己的 banner 調整, px 單位）
  const BANNER_HEIGHT = 148;  // 例如 140px

  useEffect(() => {
    function onScroll() {
      // 捲動超過 Banner 高度就隱藏
      setShow(window.scrollY < BANNER_HEIGHT);
    }
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (
    location.pathname === "/login" ||
    location.pathname === "/register" ||
    location.pathname === "/forget"
  ) return null;

  if (!show) return null; // 捲下去就隱藏

  return (
    <div style={{
      position: "fixed",
      top: 24,
      right: 36,
      zIndex: 2000,
    }}>
      <Button
        icon={<UserOutlined style={{ color: "#090909ff", fontSize: 22 }} />}
        style={{
          color: "#0d0d0dff",
          background: "#FFD900",
          border: "1.5px solid #FFD900",
          borderRadius: 18,
          fontWeight: 700,
          fontSize: 17,
          padding: "0 22px",
          boxShadow: "0 2px 8px #ffd90033"
        }}
        onClick={() => navigate("/login")}
      >
        登入
      </Button>
    </div>
  );
}

export default LoginButton;
