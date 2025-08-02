import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "../../api/api";

import { useNavigate } from "react-router-dom";

function RegisterForm() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // 密碼強度自訂驗證：必須有英文字母與數字
  const validatePassword = (_, value) => {
    if (!value) return Promise.reject("請輸入密碼");
    if (value.length < 8) return Promise.reject("密碼需大於 8 個字元");
    if (!/[A-Za-z]/.test(value) || !/\d/.test(value)) {
      return Promise.reject("密碼需同時包含英文字母與數字");
    }
    return Promise.resolve();
  };

  return (
    <div style={{ maxWidth: 350, margin: "40px auto" }}>
      <h2>註冊新帳號</h2>
      <Form
        onFinish={async (values) => {
          setLoading(true);
          try {
            await api.post("/auth/register", values);
            message.success("註冊成功，請登入！");
            navigate("/login");
          } catch (err) {
            message.error("註冊失敗：" + (err.response?.data?.error || err.message));
          }
          setLoading(false);
        }}
        layout="vertical"
      >
        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: "請輸入 Email" },
            { type: "email", message: "Email 格式錯誤" },
            {
              pattern: /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/,
              message: "請輸入正確的 Email 格式",
            },
          ]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="password"
          label="密碼"
          rules={[
            { required: true, message: "請輸入密碼" },
            { validator: validatePassword }
          ]}
          hasFeedback
        >
          <Input.Password />
        </Form.Item>
        <Form.Item>
          <Button htmlType="submit" type="primary" className="login-btn" loading={loading} block>
            註冊
          </Button>
        </Form.Item>
        <Form.Item>
          <Button onClick={() => navigate("/login")} block>
            返回登入
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default RegisterForm;
