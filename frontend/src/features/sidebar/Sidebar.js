// src/Sidebar.js
import React from "react";
import { Menu } from "antd";
import {
  AppstoreOutlined,
  ShoppingCartOutlined,
  OrderedListOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import api from "../../api/api";

function Sidebar({ loggedIn, role }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    localStorage.clear();
    try {
      await api.post('/auth/logout');
    } catch (e) {}
    window.location.href = "/";
  };

  if (!loggedIn) return null;

  return (
    <div style={{
      position: "fixed",
      left: 0,
      top: 0,
      height: "100vh",
      width: 180,
      background: "#fff",
      boxShadow: "2px 0 8px #eee",
      zIndex: 100,
      paddingTop: 32
    }}>
      <Menu
        mode="inline"
        defaultSelectedKeys={["products"]}
        style={{ height: "100%", borderRight: 0 }}
        selectable={false}
      >
        <Menu.Item key="products" icon={<AppstoreOutlined />} onClick={() => navigate("/")}>
          商品列表
        </Menu.Item>
        <Menu.Item key="cart" icon={<ShoppingCartOutlined />} onClick={() => navigate("/cart")}>
          購物車清單
        </Menu.Item>
        <Menu.Item key="orders" icon={<OrderedListOutlined />} onClick={() => navigate("/orders")}>
          訂單查詢
        </Menu.Item>
        <Menu.Item key="profile" icon={<UserOutlined />} onClick={() => navigate("/profile")}>
          會員資訊
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
    </div>
  );
}

export default Sidebar;
