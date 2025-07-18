import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "../../api/api";

import { useNavigate } from "react-router-dom";
import '../../styles/LoginForm.css'
function LoginForm() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
    <div style={{ maxWidth: 350, margin: "40px auto" }}>
      <h2>會員登入</h2>
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
        <Form.Item>
          <Button type="link" block className="login-link-btn" onClick={() => navigate("/register")}>
            還沒有帳號？註冊
          </Button>
          <Button type="link" block className="login-link-btn" onClick={() => navigate("/forget")}>
            忘記密碼
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default LoginForm;
