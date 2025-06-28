import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "./api";

function LoginForm({ onLogin, onGoRegister, onGoForget }) {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
  setLoading(true); // 1. 設定 loading 狀態為 true，讓畫面顯示「正在登入」(通常按鈕會轉圈)
  try {
    const res = await api.post("/auth/login", values);
    // 2. 用 axios 的 api 實例，對後端 /auth/login 發送 POST 請求
    //    values 是 { username: ..., password: ... }，由 Antd 表單自動帶入
    //    await 代表這是非同步請求，會等後端回應才往下執行
    // 3. 將後端回傳的 access_token 寫進瀏覽器的 localStorage

    localStorage.setItem("token", res.data.access_token);
    localStorage.setItem("user_id", res.data.user_id);
    localStorage.setItem("role", res.data.role);

    message.success("登入成功！");
    // 5. 用 Antd 的 message 組件，跳出提示訊息「登入成功！」

    onLogin && onLogin();
    // 6. 如果有傳入 onLogin 這個 callback（通常是父層 App.js 控制頁面切換），就呼叫它
    //    這會讓 App.js 把狀態設為已登入，顯示主頁內容

  } catch (err) {
    // 7. 如果上面的 API 請求出現錯誤（例如帳號密碼錯、後端沒開），會執行這裡
    message.error("登入失敗：" + (err.response?.data?.error || err.message));
    //    跳出錯誤提示，顯示後端回傳的 error 訊息，或錯誤內容
  }
  setLoading(false); // 8. 不論成功或失敗，結束時都把 loading 狀態設回 false
  };

  return (
    <div style={{ maxWidth: 350, margin: "40px auto" }}>
      <h2>會員登入</h2>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="username" label="使用者名稱" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="密碼" rules={[{ required: true }]}>
          <Input.Password />
        </Form.Item>
      
        <Form.Item>
          <Button htmlType="submit" type="primary" loading={loading} block>
            登入
          </Button>
        </Form.Item>
        <Form.Item>
          <Button type="link" block onClick={onGoRegister}>
            還沒有帳號？註冊
          </Button>
          <Button type="link" block onClick={onGoForget}>
            忘記密碼
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default LoginForm;
