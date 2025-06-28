import React, { useEffect, useState } from "react";
import { Descriptions, Spin, message, Button } from "antd";
import api from "./api";
import EditProfile from "./EditProfile";

function UserProfile() {
  const userId = localStorage.getItem("user_id");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (!userId) {
      message.error("請先登入！");
      return;
    }
    setLoading(true);
    api.get(`/users/${userId}`)
      .then(res => {
        // 如果後端是 {id:..., username:..., email:..., ...}
        setUser(res.data);
      })
      .catch(() => message.error("查詢會員資訊失敗"))
      .finally(() => setLoading(false));
  }, [userId, editing]);

  if (editing) {
    return <EditProfile user={user} onBack={() => setEditing(false)} onSuccess={() => { setEditing(false); }}/>
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto" }}>
      <h2>會員個人資訊</h2>
      <Spin spinning={loading}>
        {user ? (
          <>
            <Descriptions bordered column={1}>
              <Descriptions.Item label="會員名稱">{user.full_name}</Descriptions.Item>
              <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
              <Descriptions.Item label="phone">{user.phone}</Descriptions.Item>
              <Descriptions.Item label="地址">{user.address}</Descriptions.Item>
              {/* 可依後端欄位再加 */}
            </Descriptions>
            <div style={{ marginTop: 24, textAlign: "right" }}>
              <Button type="primary" onClick={() => setEditing(true)}>更改會員資訊</Button>
            </div>
          </>
        ) : (
          <div>查無資料</div>
        )}
      </Spin>
    </div>
  );
}

export default UserProfile;
