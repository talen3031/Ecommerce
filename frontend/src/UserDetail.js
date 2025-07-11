// src/UserDetail.js
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Spin, Descriptions, message } from "antd";
import api from "./api";

function UserDetail() {
  const { id } = useParams();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api.get(`/users/${id}`)
      .then(res => setUser(res.data))
      .catch(() => message.error("查無用戶資料"))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) return <div>找不到會員</div>;

  return (
    <div style={{ maxWidth: 520, margin: "40px auto" }}>
      <h2>會員詳細資料</h2>
      <Spin spinning={loading}>
        {user ? (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="會員名稱">{user.full_name || user.username}</Descriptions.Item>
            <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
            <Descriptions.Item label="電話">{user.phone}</Descriptions.Item>
            <Descriptions.Item label="地址">{user.address}</Descriptions.Item>
            {/* 可以再加更多欄位 */}
          </Descriptions>
        ) : (
          <div>查無資料</div>
        )}
      </Spin>
    </div>
  );
}

export default UserDetail;
