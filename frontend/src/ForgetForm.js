import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "./api";

function ForgetForm({ onBackToLogin }) {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await api.post("/auth/forgot_password", values); 
      message.success("已寄送重設密碼信！");
      onBackToLogin && onBackToLogin();
    } catch (err) {
      message.error("寄送失敗：" + (err.response?.data?.error || err.message));
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 350, margin: "40px auto" }}>
      <h2>忘記密碼</h2>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="email" label="註冊信箱" rules={[{ required: true, type: "email" }]}>
          <Input />
        </Form.Item>
        <Form.Item>
          <Button htmlType="submit" type="primary" loading={loading} block>送出</Button>
        </Form.Item>
        <Form.Item>
          <Button onClick={onBackToLogin} block>返回登入</Button>
        </Form.Item>
      </Form>
    </div>
  );
}
export default ForgetForm;
