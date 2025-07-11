// src/LoginButton.js
import React from "react";
import { Button } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";

function LoginButton() {
  const navigate = useNavigate();
  const location = useLocation();

  // 如果目前就是 /login 頁面，則不顯示按鈕
  if (
    location.pathname === "/login" ||
    location.pathname === "/register" ||
    location.pathname === "/forget"
  ) return null;

  return (
    <div style={{
      position: "fixed",
      top: 24,
      right: 36,
      zIndex: 2000,
    }}>
      <Button
        icon={<UserOutlined style={{ color: "#fff", fontSize: 22 }} />}
        style={{
          color: "#fff",
          background: "rgba(0,0,0,0.16)",
          border: "1.5px solid #fff",
          borderRadius: 18,
          fontWeight: 700,
          fontSize: 17,
          padding: "0 22px",
        }}
        onClick={() => navigate("/login")}
      >
        登入
      </Button>
    </div>
  );
}

export default LoginButton;
