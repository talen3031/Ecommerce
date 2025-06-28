import React, { useState, useEffect } from "react";
import { Tabs, message } from "antd";
import UserList from "./UserList";         // 可以直接重用前面做的會員清單
import ProductManager from "./ProductManager"; // 可自己做個商品管理元件
import OrderList from "./OrderList";       // 也可重用訂單查詢頁

function AdminPage() {
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // 假設你 user 資料存在 localStorage 或有專屬 API 查詢
    // 這裡用 localStorage 為例
    const role = localStorage.getItem("role");
    console.log("",role)
    if (role === "admin") setIsAdmin(true);
    else message.error("無管理員權限！");
  }, []);

  if (!isAdmin) return null;

  return (
    <div style={{ maxWidth: 1100, margin: "40px auto" }}>
      <h2>管理者後台</h2>
      <Tabs defaultActiveKey="users"
        items={[
          //{ key: "users", label: "會員管理", children: <UserList /> },
          { key: "products", label: "商品管理", children: <ProductManager /> },
          //{ key: "orders", label: "訂單管理", children: <OrderList /> },
        ]}
      />
    </div>
  );
}

export default AdminPage;
