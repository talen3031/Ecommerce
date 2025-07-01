import React, { useState } from "react";
import { Button, Modal } from "antd";
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
  const [showLogin, setShowLogin] = useState(false);

  const handleLogout = () => {
    localStorage.clear();
    setLoggedIn(false);
    setRole("");
    setTab("products");
    setSelectedProductId(null);
    setPage("login");
  };

  let mainContent;
  if (!loggedIn) {
    // 未登入：只能逛商品
    mainContent = !selectedProductId
      ? <ProductList onSelectProduct={setSelectedProductId} />
      : <ProductDetail productId={selectedProductId} onBack={() => setSelectedProductId(null)} />;
  } else {
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
  }

  return (
    <div>
      {/* 未登入時右上角顯示登入按鈕 */}
      {!loggedIn && (
        <div style={{ textAlign: "right", padding: "16px 32px" }}>
          <Button type="primary" onClick={() => { setShowLogin(true); setPage("login"); }}>登入</Button>
        </div>
      )}

      {/* 已登入才有主導覽 */}
      {loggedIn && (
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
      )}

      {/* 主內容區 */}
      <div>
        {mainContent}
      </div>

      {/* 登入相關 Modal */}
      <Modal
        open={showLogin}
        onCancel={() => setShowLogin(false)}
        footer={null}
        title="會員登入"
      >
        {page === "login" && (
          <LoginForm
            onLogin={() => {
              setLoggedIn(true);
              setRole(localStorage.getItem("role") || "");
              setTab("products");
              setShowLogin(false);
            }}
            onGoRegister={() => setPage("register")}
            onGoForget={() => setPage("forget")}
          />
        )}
        {page === "register" && (
          <RegisterForm
            onRegisterSuccess={() => setPage("login")}
            onBackToLogin={() => setPage("login")}
          />
        )}
        {page === "forget" && (
          <ForgetForm
            onBackToLogin={() => setPage("login")}
          />
        )}
      </Modal>
    </div>
  );
}

export default App;
