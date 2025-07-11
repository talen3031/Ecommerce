import React, { useEffect, useState } from "react";
import { Form, Input, Button, message, Spin } from "antd";
import api from "./api";
import { useNavigate } from "react-router-dom";

function EditProfile() {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const [user, setUser] = useState(null);
  const [fetching, setFetching] = useState(true);
  const navigate = useNavigate();
  const userId = localStorage.getItem("user_id");

  useEffect(() => {
    if (!userId) {
      message.error("請先登入！");
      navigate("/login");
      return;
    }
    setFetching(true);
    api.get(`/users/${userId}`)
      .then(res => setUser(res.data))
      .catch(() => message.error("查無會員資料"))
      .finally(() => setFetching(false));
  }, [userId, navigate]);

  const handleFinish = (values) => {
    setLoading(true);
    api.patch(`/users/${userId}`, values)
      .then(res => {
        message.success("會員資料已更新");
        navigate("/profile");
      })
      .catch(() => message.error("更新失敗"))
      .finally(() => setLoading(false));
  };

  if (fetching) {
    return <Spin spinning style={{ width: "100%", marginTop: 40 }} />;
  }

  return (
    <div style={{ maxWidth: 500, margin: "40px auto" }}>
      <h2>更改會員資訊</h2>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          full_name: user?.full_name,
          address: user?.address,
          phone: user?.phone
        }}
        onFinish={handleFinish}
      >
        <Form.Item label="姓名" name="full_name">
          <Input />
        </Form.Item>
        <Form.Item label="地址" name="address">
          <Input />
        </Form.Item>
        <Form.Item label="電話" name="phone">
          <Input />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} style={{ marginRight: 8 }}>儲存</Button>
          <Button onClick={() => navigate("/profile")}>取消</Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default EditProfile;
