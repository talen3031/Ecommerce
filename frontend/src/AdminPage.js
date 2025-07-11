import React, { useState, useEffect } from "react";
import { Tabs, message } from "antd";
import UserList from "./UserList";
import ProductManager from "./ProductManager";
import OrderManger from "./OrderManger";
import DiscountCodeManger from "./DiscountCodeManger";
import { useNavigate } from "react-router-dom";

function AdminPage() {
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const role = localStorage.getItem("role");
    if (role === "admin") {
      setIsAdmin(true);
    } else {
      message.error("無管理員權限！");
      // 可改導到首頁或登入
      navigate("/login", { replace: true });
    }
    // eslint-disable-next-line
  }, []);

  if (!isAdmin) return null;

  return (
    <div style={{ maxWidth: 1100, margin: "40px auto" }}>
      <h2>管理者後台</h2>
      <Tabs
        defaultActiveKey="products"
        items={[
          { key: "users", label: "會員管理", children: <UserList /> },
          { key: "products", label: "商品管理", children: <ProductManager /> },
          { key: "orders", label: "訂單管理", children: <OrderManger /> },
          { key: "discount", label: "折扣碼管理", children: <DiscountCodeManger /> },
        ]}
      />
    </div>
  );
}

export default AdminPage;
