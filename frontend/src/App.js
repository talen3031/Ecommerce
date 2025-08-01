import { useNavigate } from "react-router-dom";
import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ProductList from "./features/products/ProductList";
import ProductDetail from "./features/products/ProductDetail";
import CartList from "./features/carts/CartList";
import OrderList from "./features/orders/OrderList";
import GuestOrderDetail from './features/orders/GuestOrderDetail';

import UserProfile from "./features/user/UserProfile";
import EditProfile from "./features/user/EditProfile";
import LoginForm from "./features/user/LoginForm";
import RegisterForm from "./features/user/RegisterForm";
import ForgetForm from "./features/user/ForgetForm";
import UserDetail from "./features/user/UserDetail"; 
import ResetPassword from "./features/user/ResetPassword"; 
import CustomerChat from "./features/user/CustomerChat";

import AdminPage from "./features/admin/AdminPage";
import AdminReply from "./features/admin/AdminReply";

import SidebarDrawer from "./features/sidebar/SidebarDrawer";


import CheckoutPage from "./features/carts/CheckoutPage";
import LoginButton from "./components/LoginButton";
import HeroBanner from './components/HeroBanner';
import About from "./About";

import { getGuestId } from "./api/api";
import 'antd/dist/reset.css';

function App() {
  useEffect(() => {
    getGuestId(); // 頁面一進來就確保 guest_id 已存在
  }, []);

  const loggedIn = !!localStorage.getItem("token");
  const role = localStorage.getItem("role") || "";
  return (
    
     <BrowserRouter>
      {/* 右上登入按鈕，只有未登入時出現 */}
      
      {!loggedIn && <LoginButton />}

       {/* SidebarDrawer 不分登入都顯示 */}
      <SidebarDrawer loggedIn={loggedIn} role={role} />

      {/* 主內容往右偏移（空出 Sidebar 空間），未登入時 marginLeft 設0 */}
      <div >
         <HeroBanner />
        {/* 這裡接下來才是 Router 的內容 */}
        <Routes>
          <Route path="/" element={<ProductListWrapper />} />
          <Route path="/products" element={<ProductListWrapper />} />
          <Route path="/products/:id" element={<ProductDetail />} />

          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/forget" element={<ForgetForm />} />
          <Route path="/reset_password" element={<ResetPassword />} />
          <Route path="/cart" element={<CartList />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/orders" element={loggedIn ? <OrderList /> : <Navigate to="/login" />} />
          <Route path="/orders/:orderId" element={loggedIn ? <OrderList /> : <Navigate to="/login" />} />
          <Route path="/guest-order-detail" element={<GuestOrderDetail />} />
          <Route path="/profile" element={loggedIn ? <UserProfile /> : <Navigate to="/login" />} />
          <Route path="/profile/edit" element={loggedIn ? <EditProfile /> : <Navigate to="/login" />} />
          <Route path="/chat" element={loggedIn ? <CustomerChat /> : <Navigate to="/login" />} />
          
          <Route path="/about" element={<About />} />
          <Route path="/admin/users/:id" element={<UserDetail />} />
          <Route path="/admin" element={loggedIn && role === "admin" ? <AdminPage /> : <Navigate to="/login" />} />
          <Route path="/admin/reply" element={loggedIn && role === "admin" ? <AdminReply /> : <Navigate to="/login" />} />

          <Route path="/reset_password" element={<ResetPassword />} />
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
