import React, { useState } from "react";
import { Button } from "antd";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import ForgetForm from "./ForgetForm";
import ProductList from "./ProductList";
import ProductDetail from "./ProductDetail";
import CartList from "./CartList";
import OrderList from "./OrderList";
import UserProfile from "./UserProfile";
import AdminPage from "./AdminPage";

function App() {
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));
  const [role, setRole] = useState(localStorage.getItem("role") || "");
  const [tab, setTab] = useState("products");
  const [page, setPage] = useState("login"); // login, register, forget
  const [selectedProductId, setSelectedProductId] = useState(null);

  // 登出
  const handleLogout = () => {
    localStorage.clear();
    setLoggedIn(false);
    setRole("");
    setTab("products");
    setSelectedProductId(null);
    setPage("login");
  };

  // 處理登入表單切換
  if (!loggedIn) {
    if (page === "register") return <RegisterForm onRegisterSuccess={() => setPage("login")} onBackToLogin={() => setPage("login")} />;
    if (page === "forget") return <ForgetForm onBackToLogin={() => setPage("login")} />;
    return (
      <LoginForm
        onLogin={() => {
          setLoggedIn(true);
          setRole(localStorage.getItem("role") || "");
          setTab("products");
        }}
        onGoRegister={() => setPage("register")}
        onGoForget={() => setPage("forget")}
      />
    );
  }

  // 主內容區域
  let mainContent;
  if (tab === "products") {
    mainContent = !selectedProductId
      ? <ProductList onSelectProduct={setSelectedProductId} />
      : <ProductDetail productId={selectedProductId} onBack={() => setSelectedProductId(null)} />;
  } else if (tab === "cart") {
    mainContent = <CartList />;
  } else if (tab === "orders") {
    mainContent = <OrderList />;
  } else if (tab === "profile") {
    mainContent = <UserProfile />;
  } else if (tab === "admin") {
    mainContent = <AdminPage />;
  }

  return (
    <div>
      {/* 上方導覽按鈕區 */}
      <div style={{ margin: "24px 0", textAlign: "center" }}>
        <Button onClick={() => { setTab("products"); setSelectedProductId(null); }}>商品列表</Button>
        <Button onClick={() => setTab("cart")}>購物車清單</Button>
        <Button onClick={() => setTab("orders")}>訂單查詢</Button>
        <Button onClick={() => setTab("profile")}>會員資訊</Button>
        {role === "admin" && (
          <Button onClick={() => setTab("admin")}>管理後台</Button>
        )}
        <Button danger onClick={handleLogout}>登出</Button>
      </div>
      {/* 主頁內容區 */}
      <div>
        {mainContent}
      </div>
    </div>
  );
}

export default App;
