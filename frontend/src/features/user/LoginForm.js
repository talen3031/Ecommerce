// src/pages/auth/LoginForm.js  (路徑依你專案實際位置調整)
import React, { useEffect, useRef, useState } from "react";
import { Form, Input, Button, message, Divider, Typography } from "antd";
import api from "../../api/api";
import { useNavigate } from "react-router-dom";
import "../../styles/LoginForm.css";
import { REACT_APP_GOOGLE_CLIENT_ID } from "../../config"; 
const { Text } = Typography;

function LoginForm() {
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const navigate = useNavigate();
  const googleBtnRef = useRef(null);
  const gsiInitedRef = useRef(false);

  // 動態載入 Google Identity Services 並渲染按鈕
  useEffect(() => {
    // 若已存在 script，避免重複載入
    const existing = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
    if (existing) {
      existing.addEventListener("load", initGSI);
      if (existing.getAttribute("data-loaded") === "true") initGSI();
    } else {
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = () => {
        script.setAttribute("data-loaded", "true");
        initGSI();
      };
      document.head.appendChild(script);
    }

    function initGSI() {
      if (gsiInitedRef.current) return;
      if (!window.google || !google.accounts || !googleBtnRef.current) return;
      const clientId = REACT_APP_GOOGLE_CLIENT_ID;
      if (!clientId) {
        // 若忘了設定環境變數，給出友善提醒
        // (本地: .env 檔加入 REACT_APP_GOOGLE_CLIENT_ID=你的client_id)
        console.warn("Missing REACT_APP_GOOGLE_CLIENT_ID, Google Sign-In disabled.");
        return;
      }

      /* global google */
      google.accounts.id.initialize({
        client_id: clientId,
        callback: onGoogleCredential,
        ux_mode: "popup",
      });

      google.accounts.id.renderButton(googleBtnRef.current, {
        theme: "outline",
        size: "large",
        shape: "pill",
        width: 320,
      });

      // 如需 One Tap，可開啟：google.accounts.id.prompt();
      gsiInitedRef.current = true;
    }

    return () => {
      // 清理事件監聽（避免熱更新/重掛時重複）
      const existing = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
      if (existing) existing.removeEventListener("load", initGSI);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Google 回呼：把 credential 丟後端 /auth/google 換取 access/refresh
  const onGoogleCredential = async (resp) => {
    try {
      setGoogleLoading(true);
      const { credential } = resp || {};
      if (!credential) {
        message.error("Google 登入失敗：缺少憑證");
        return;
      }
      // 將 credential 傳到後端換取 token。注意帶上 Cookie。
      const r = await api.post(
        "/auth/google",
        { credential },
        { withCredentials: true }
      );

      const { access_token, user_id, role } = r.data || {};
      if (!access_token) {
        message.error("Google 登入失敗：後端未回傳 access_token");
        return;
      }

      localStorage.setItem("token", access_token);
      localStorage.setItem("user_id", user_id);
      localStorage.setItem("role", role);

      message.success("已透過 Google 登入！");
      // 與你原本行為一致：直接回首頁（避免殘留舊狀態）
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      message.error("Google 登入失敗：" + (err.response?.data?.error || err.message));
    } finally {
      setGoogleLoading(false);
    }
  };

  // 原本的 Email/密碼登入
  const onFinish = async (values) => {
    setLoading(true);
    try {
      const res = await api.post("/auth/login", values);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user_id", res.data.user_id);
      localStorage.setItem("role", res.data.role);
      window.location.href = "/";
      message.success("登入成功！");
    } catch (err) {
      message.error("登入失敗：" + (err.response?.data?.error || err.message));
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 360, margin: "40px auto" }}>
      <h2 style={{ textAlign: "center", marginBottom: 16 }}>會員登入</h2>



      {/* Email/密碼登入表單 */}
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: "請輸入 Email" },
            { type: "email", message: "Email 格式錯誤" },
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          name="password"
          label="密碼"
          rules={[{ required: true, message: "請輸入密碼" }]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item>
          <Button
            htmlType="submit"
            type="primary"
            loading={loading}
            block
            className="login-btn"
          >
            登入
          </Button>
        </Form.Item>
                     {/* Google Sign-In 區塊 */}

      <div style={{ display: "flex", justifyContent: "center", marginBottom: 8 }}>
        <div ref={googleBtnRef} aria-label="google-signin-button" />
      </div>
        <Form.Item style={{ marginBottom: 0 }}>
          <Button
            type="link"
            block
            className="login-link-btn"
            onClick={() => navigate("/register")}
          >
            還沒有帳號？註冊
          </Button>
          <Button
            type="link"
            block
            className="login-link-btn"
            onClick={() => navigate("/forget")}
          >
            忘記密碼
          </Button>
        </Form.Item>
      </Form>
 
  

      <Divider style={{ margin: "12px 0" }} />
      
    </div>
  );
}

export default LoginForm;
