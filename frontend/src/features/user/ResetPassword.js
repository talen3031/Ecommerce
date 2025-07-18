import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "../../api/api";
import { useNavigate, useSearchParams } from "react-router-dom";

function ResetPassword() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  // 密碼強度自訂驗證
  const validatePassword = (_, value) => {
    if (!value) return Promise.reject("請輸入新密碼");
    if (value.length < 10) return Promise.reject("密碼需大於 10 個字元");
    if (!/[A-Za-z]/.test(value) || !/\d/.test(value)) {
      return Promise.reject("密碼需同時包含英文字母與數字");
    }
    return Promise.resolve();
  };

  const onFinish = async (values) => {
    if (!token) {
      message.error("缺少驗證資訊，請重新操作");
      return;
    }
    setLoading(true);
    try {
      await api.post("auth/reset_password", {
        token,
        password: values.password
      });
      message.success("密碼重設成功，請重新登入");
      navigate("/login");
    } catch (err) {
      message.error("密碼重設失敗：" + (err.response?.data?.error || err.message));
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 350, margin: "40px auto" }}>
      <h2>重設密碼</h2>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item
          name="password"
          label="新密碼"
          rules={[
            { required: true, message: "請輸入新密碼" },
            { validator: validatePassword }
          ]}
          hasFeedback
        >
          <Input.Password />
        </Form.Item>
        <Form.Item
          name="confirm_password"
          label="再次輸入新密碼"
          dependencies={["password"]}
          hasFeedback
          rules={[
            { required: true, message: "請再次輸入新密碼" },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject("兩次輸入的密碼不一致");
              }
            })
          ]}
        >
          <Input.Password />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
            送出
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default ResetPassword;
