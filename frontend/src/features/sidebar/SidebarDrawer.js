import React, { useState } from "react";
import { Drawer, Menu, Button } from "antd";
import {
  MenuOutlined,
  AppstoreOutlined,
  ShoppingCartOutlined,
  OrderedListOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  InfoCircleOutlined,CustomerServiceOutlined
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import api from "../../api/api";

function SidebarDrawer({ loggedIn, role }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout", {}, { withCredentials: true });
    } catch (e) {}
    localStorage.clear();
    navigate("/");
    window.location.reload();
  };

  // ====== 這裡不再 return null，讓訪客也能拉出側邊欄 ======
  return (
  <>
    {/*漢堡按鈕 */}
      <Button
        type="text" // 純 icon 無底色
        icon={<MenuOutlined style={{ color: "#FFD900", fontSize: 26 }} />}
        style={{
          background: "transparent",
          border: "none",
          boxShadow: "none",
          padding: 0,
          minWidth: 0,
          height: 38,
          lineHeight: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        }}
        onClick={() => setOpen(true)}
        aria-label="主選單"
      />
    <Drawer
      placement="right"
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
        {/* 只有登入才顯示會員專屬選單 */}
        {loggedIn && (
          <>
            <Menu.Item key="orders" icon={<OrderedListOutlined />} onClick={() => navigate("/orders")}>
              訂單查詢
            </Menu.Item>
            <Menu.Item key="profile" icon={<UserOutlined />} onClick={() => navigate("/profile")}>
              會員資訊
            </Menu.Item>
            <Menu.Item
              key="chat"
              icon={<CustomerServiceOutlined />}
              onClick={() =>
                role === "admin"
                  ? navigate("/admin/reply")
                  : navigate("/chat")
              }
            >
              客服聊天室
            </Menu.Item>
          </>
        )}
        <Menu.Item key="about" icon={<InfoCircleOutlined />} onClick={() => navigate("/about")}>
          關於Nerd.com
        </Menu.Item>
        {/* 只有管理員才有後台 */}
        {loggedIn && role === "admin" && (
          <Menu.Item key="admin" icon={<SettingOutlined />} onClick={() => navigate("/admin")}>
            管理後台
          </Menu.Item>
        )}
        {/* 登入才有登出 */}
        {loggedIn && (
          <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout} style={{ color: "#f5222d" }}>
            登出
          </Menu.Item>
        )}
      </Menu>
    </Drawer>
  </>
);

}

export default SidebarDrawer;
