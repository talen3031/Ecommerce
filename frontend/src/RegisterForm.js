import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "./api";
import { useNavigate } from "react-router-dom";

function RegisterForm() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await api.post("/auth/register", values);
      message.success("註冊成功，請登入！");
      navigate("/login");
    } catch (err) {
      message.error("註冊失敗：" + (err.response?.data?.error || err.message));
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 350, margin: "40px auto" }}>
      <h2>註冊新帳號</h2>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="使用者名稱" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true, type: "email" }]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="密碼" rules={[{ required: true, min: 6 }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item name="address" label="地址" rules={[{ required: false}]}>
          <Input />
        </Form.Item>
        <Form.Item name="phone" label="手機號碼" rules={[{ required: false}]}>
          <Input />
        </Form.Item>
        <Form.Item>
          <Button htmlType="submit" type="primary" loading={loading} block>註冊</Button>
        </Form.Item>
        <Form.Item>
          <Button onClick={() => navigate("/login")} block>返回登入</Button>
        </Form.Item>
      </Form>
    </div>
  );
}
export default RegisterForm;
