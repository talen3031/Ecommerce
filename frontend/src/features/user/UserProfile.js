import React, { useEffect, useState } from "react";
import { Descriptions, Spin, message, Button, Tag } from "antd";
import api from "../../api/api";
import EditProfile from "./EditProfile";
import { useNavigate, useLocation } from "react-router-dom";

import '../../styles/UserProfile.css'

function UserProfile() {
  const userId = localStorage.getItem("user_id");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const LINE_CHANNEL_ID = "2007730728";
  const STATE = userId;
  const REDIRECT_URI = encodeURIComponent("https://ecommerce-backend-production-a470.up.railway.app/linemessage/blinding");
  const lineLoginUrl = `https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=${LINE_CHANNEL_ID}&redirect_uri=${REDIRECT_URI}&scope=openid%20profile&state=${STATE}`;
  const navigate = useNavigate();
  const location = useLocation();

  function bindLine() {
    window.location.href = lineLoginUrl;
  }

  useEffect(() => {
    if (!userId) {
      message.error("請先登入！");
      return;
    }
    setLoading(true);
    api.get(`/users/${userId}`)
      .then(res => setUser(res.data))
      .catch(() => message.error("查詢會員資訊失敗"))
      .finally(() => setLoading(false));
  }, [userId, location.pathname]); // 監控網址（從編輯返回自動更新）

  // 若網址為 /profile/edit，就顯示編輯畫面
  const isEditMode = location.pathname.endsWith("/edit");

  if (isEditMode) {
    return (
      <EditProfile
        user={user}
        onBack={() => navigate("/profile")}
        onSuccess={() => navigate("/profile")}
      />
    );
  }

  return (
    <div className="form-container">
      <h2>會員個人資訊</h2>
      <Spin spinning={loading}>
        {user ? (
          <>
            <Descriptions bordered column={1}>
              <Descriptions.Item label="會員名稱">{user.full_name}</Descriptions.Item>
              <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
              <Descriptions.Item label="電話">{user.phone}</Descriptions.Item>
              <Descriptions.Item label="地址">{user.address}</Descriptions.Item>
              <Descriptions.Item label="LINE 綁定狀態">
                {user.line_user_id && user.line_picture_url ? (
                  <div style={{ textAlign: 'center', margin: '8px 0' }}>
                    <img
                      src={user.line_picture_url}
                      alt="LINE 頭像"
                      style={{
                        width: 78, height: 78, borderRadius: "50%",
                        border: "2px solid #2db400", boxShadow: "0 2px 10px #0002",
                        marginBottom: 6
                      }}
                    />
                    <div style={{ color: "#2db400", fontWeight: 600, margin: "4px 0" }}>
                      {user.line_display_name || "LINE 使用者"}
                    </div>
                    <Tag color="green">已綁定</Tag>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', margin: '8px 0' }}>
                    <Tag color="red" style={{ fontSize: 16, marginBottom: 6 }}>尚未綁定</Tag>
                    <div style={{ color: "#888", fontSize: 14 }}>請點下方「綁定 LINE 帳號」</div>
                  </div>
                )}
              </Descriptions.Item>
              {user.line_display_name &&
                <Descriptions.Item label="LINE 暱稱">{user.line_display_name}</Descriptions.Item>}
            </Descriptions>
            <div style={{ marginTop: 24, textAlign: "right" }}>
              <Button className="userprofile_edit-btn" type="primary" onClick={() => navigate("/profile/edit")}>
                更改會員資訊
              </Button>
              {user.line_user_id ? (
                <Button disabled style={{ background: "#eee", color: "#888", border: "1px solid #ddd" }}>
                  已綁定 LINE 帳號
                </Button>
              ) : (
                <Button type="dashed" onClick={bindLine}>
                  綁定 LINE 帳號
                </Button>
              )}
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
