import React, { useState } from "react";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import ForgetForm from "./ForgetForm";
import ProductList from "./ProductList";
import CartList from "./CartList";
import OrderList from "./OrderList";
import UserProfile from "./UserProfile";
import AdminPage from "./AdminPage";
import { Button } from "antd";

function App() {
  // 1. 判斷是否已登入，根據 localStorage 裡有沒有 token 如果 token 存在，loggedIn 為 true；否則為 false
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));
  const [role, setRole] = useState(localStorage.getItem("role") || "");

  // 2. 控制主頁顯示哪個 tab（"products"：商品列表；"cart"：購物車清單）
  const [tab, setTab] = useState("products");

  // 3. 控制登入/註冊/忘記密碼頁的顯示狀態
  //    "login"：登入頁，"register"：註冊頁，"forget"：忘記密碼頁
  const [page, setPage] = useState(null); // null: 不顯示登入相關頁
  // 未登入時，右上角顯示登入按鈕，按下才顯示登入/註冊/忘記密碼頁
  const renderAuthButtons = () => {
    // 只在未登入且沒在登入/註冊/忘記密碼頁時顯示登入按鈕
    if (!loggedIn && page === null) {
      return (
        <div style={{ position: "absolute", top: 16, right: 24 }}>
          <Button type="primary" onClick={() => setPage("login")}>登入</Button>
        </div>
      );
    } else if (loggedIn) {
      return (
        <div style={{ position: "absolute", top: 16, right: 24 }}>
          <Button danger onClick={() => { localStorage.clear(); setLoggedIn(false); setRole(""); setTab("products"); }}>登出</Button>
        </div>
      );
    }
    // 其他情況（登入/註冊/忘記密碼頁）不顯示任何按鈕
    return null;
  };

  // 登入/註冊/忘記密碼彈窗
  if (page === "login") {
    return (
      <div>
        {renderAuthButtons()}
        <LoginForm
          onLogin={() => {setLoggedIn(true); 
                          setPage(null); 
                          setRole(localStorage.getItem("role") || "");
          }}
          onGoRegister={() => setPage("register")}
          onGoForget={() => setPage("forget")}
        />
      </div>
    );
  }
  if (page === "register") {
    return (
      <div>
        {renderAuthButtons()}
        <RegisterForm
          onRegisterSuccess={() => setPage("login")}
          onBackToLogin={() => setPage("login")}
        />
      </div>
    );
  }
  if (page === "forget") {
    return (
      <div>
        {renderAuthButtons()}
        <ForgetForm onBackToLogin={() => setPage("login")} />
      </div>
    );
  }

  // 5. 邏輯：如果「已登入」則顯示主內容
  return (
    <div style={{ position: "relative" }}>
      {renderAuthButtons()}
      <div style={{ margin: "24px 0", textAlign: "center" }}>
        {loggedIn && (
          <>
            <Button onClick={() => setTab("products")}>商品列表</Button>
            <Button onClick={() => setTab("cart")}>購物車清單</Button>
            <Button onClick={() => setTab("orders")}>訂單查詢</Button>
            <Button onClick={() => setTab("profile")}>會員資訊</Button>
            {role === "admin" && (
              <Button onClick={() => setTab("admin")}>管理後台</Button>
            )}
          </>
        )}
      </div>
      {/* 未登入時只顯示商品列表 */}
      {(!loggedIn || tab === "products") && <ProductList />}
      {loggedIn && tab === "cart" && <CartList />}
      {loggedIn && tab === "orders" && <OrderList />}
      {loggedIn && tab === "profile" && <UserProfile />}
      {loggedIn && tab === "admin" && <AdminPage />}
    </div>
  );
}
export default App;
