// src/SidebarDrawer.js
import React, { useState } from "react";
import { Drawer, Menu, Button } from "antd";
import {
  MenuOutlined,
  AppstoreOutlined,
  ShoppingCartOutlined,
  OrderedListOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,InfoCircleOutlined ,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import api from "../../api/api";

function SidebarDrawer({ loggedIn, role }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout", {}, { withCredentials: true });
    } catch (e) {
      // 可以忽略錯誤（無論如何都清除本地端）
    }
    localStorage.clear();
    navigate("/");
    window.location.reload();
  };


  if (!loggedIn) return null;

  return (
    <>
        {/* 只有 Drawer 關閉時才顯示漢堡按鈕 */}
      {!open && (
        <Button
          icon={<MenuOutlined />}
          style={{
            position: "fixed", top: 24, left: 24, zIndex: 2000, width: 42, height: 42,
            fontSize: 20, background: "#fff", border: "1px solid #eee", boxShadow: "0 1px 6px #ddd"
          }}
          onClick={() => setOpen(true)}
        />
      )}
      <Drawer
        placement="left"
        closable={false}
        onClose={() => setOpen(false)}
        open={open}
        width={210}
        bodyStyle={{ padding: 0 }}
      >
        <Menu
          mode="inline"
          style={{ height: "100%", borderRight: 0 }}
          selectable={false}
          onClick={() => setOpen(false)}
        >
          <Menu.Item key="products" icon={<AppstoreOutlined />} onClick={() => navigate("/")}>
            商品列表
          </Menu.Item>
          <Menu.Item key="cart" icon={<ShoppingCartOutlined />} onClick={() => navigate("/cart")}>
            購物車
          </Menu.Item>
          <Menu.Item key="orders" icon={<OrderedListOutlined />} onClick={() => navigate("/orders")}>
            訂單查詢
          </Menu.Item>
          <Menu.Item key="profile" icon={<UserOutlined />} onClick={() => navigate("/profile")}>
            會員資訊
          </Menu.Item>
          <Menu.Item
            key="about"
            icon={<InfoCircleOutlined />}
            onClick={() => navigate("/about")}
          >
            關於我
          </Menu.Item>

          {role === "admin" && (
            <Menu.Item key="admin" icon={<SettingOutlined />} onClick={() => navigate("/admin")}>
              管理後台
            </Menu.Item>
          )}
          <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout} style={{ color: "#f5222d" }}>
            登出
          </Menu.Item>
        </Menu>
      </Drawer>
    </>
  );
}

export default SidebarDrawer;
