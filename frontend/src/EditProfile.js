import React, { useState } from "react";
import { Form, Input, Button, message } from "antd";
import api from "./api";

function EditProfile({ user, onBack, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleFinish = (values) => {
    setLoading(true);
    api.patch(`/users/${user.id}`, values)
      .then(res => {
        message.success("會員資料已更新");
        if (onSuccess) onSuccess();
      })
      .catch(() => message.error("更新失敗"))
      .finally(() => setLoading(false));
  };

  return (
    <div style={{ maxWidth: 500, margin: "40px auto" }}>
      <h2>更改會員資訊</h2>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          full_name: user.full_name,
          address: user.address,
          phone: user.phone
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
          <Button onClick={onBack}>取消</Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default EditProfile; 