// src/LoginButton.js
import React from "react";
import { Button } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

function LoginButton() {
  const navigate = useNavigate();

  return (
    <Button
      type="text" // 讓按鈕純 icon、沒背景
      icon={<UserOutlined style={{ color: "#FFD900", fontSize: 26 }} />}
      style={{
        background: "transparent",
        border: "none",
        boxShadow: "none",
        padding: 0,
        minWidth: 0,
        height: 38,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}
      onClick={() => navigate("/login")}
      aria-label="登入"
    />
  );
}

export default LoginButton;
