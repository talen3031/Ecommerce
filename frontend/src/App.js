import { useNavigate } from "react-router-dom";
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import ForgetForm from "./ForgetForm";
import ProductList from "./ProductList";
import ProductDetail from "./ProductDetail";
import CartList from "./CartList";
import OrderList from "./OrderList";
import UserProfile from "./UserProfile";
import AdminPage from "./AdminPage";
import EditProfile from "./EditProfile";
import SidebarDrawer from "./SidebarDrawer";
import LoginButton from "./LoginButton";
import UserDetail from "./UserDetail"; // 記得import

import 'antd/dist/reset.css';

function App() {
  const loggedIn = !!localStorage.getItem("token");
  const role = localStorage.getItem("role") || "";

  return (
     <BrowserRouter>
      {/* 右上登入按鈕，只有未登入時出現 */}
      {!loggedIn && <LoginButton />}

      {/* SidebarDrawer 只有登入時出現 */}
      {loggedIn && <SidebarDrawer loggedIn={loggedIn} role={role} />}

      {/* 主內容往右偏移（空出 Sidebar 空間），未登入時 marginLeft 設0 */}
      <div >
        <Routes>
          <Route path="/" element={<ProductListWrapper />} />
          <Route path="/products" element={<ProductListWrapper />} />
          <Route path="/products/:id" element={<ProductDetail />} />

          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/forget" element={<ForgetForm />} />

          <Route path="/cart" element={loggedIn ? <CartList /> : <Navigate to="/login" />} />
          <Route path="/orders" element={loggedIn ? <OrderList /> : <Navigate to="/login" />} />
          <Route path="/orders/:orderId" element={loggedIn ? <OrderList /> : <Navigate to="/login" />} />

          <Route path="/profile" element={loggedIn ? <UserProfile /> : <Navigate to="/login" />} />
          <Route path="/profile/edit" element={loggedIn ? <EditProfile /> : <Navigate to="/login" />} />
          <Route path="/admin/users/:id" element={<UserDetail />} />
          <Route path="/admin" element={loggedIn && role === "admin" ? <AdminPage /> : <Navigate to="/login" />} />

          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

// 商品列表頁（點擊商品可導到詳情頁）
function ProductListWrapper() {
  const navigate = useNavigate();
  return <ProductList onSelectProduct={id => navigate(`/products/${id}`)} />;
}

export default App;
