import React, { useEffect, useState } from "react";
import { Table, Button, InputNumber, message, Popconfirm, Spin } from "antd";
import RecommendList from "./RecommendList";

import api from "./api";

function CartList() {
  const userId = localStorage.getItem("user_id");
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [itemUpdating, setItemUpdating] = useState({}); // 控制每一列 loading

  // 取得購物車資料
  const fetchCart = async () => {
    if (!userId) {
      message.error("請先登入");
      return;
    }
    setLoading(true);
    try {
      const res = await api.get(`/carts/${userId}`);
      setCart(res.data);
    } catch (err) {
      message.error("取得購物車失敗");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCart();
    // eslint-disable-next-line
  }, []);

  // 更新數量
  const updateQuantity = async (product_id, quantity) => {
    setItemUpdating(u => ({ ...u, [product_id]: true }));
    try {
      await api.put(`/carts/${userId}`, { product_id, quantity });
      message.success("已更新數量");
      fetchCart();
    } catch (err) {
      message.error("更新數量失敗");
    }
    setItemUpdating(u => ({ ...u, [product_id]: false }));
  };

  // 移除商品
  const removeItem = async (product_id) => {
    setItemUpdating(u => ({ ...u, [product_id]: true }));
    try {
      await api.delete(`/carts/${userId}`, { data: { product_id } });
      message.success("已移除商品");
      fetchCart();
    } catch (err) {
      message.error("移除失敗");
    }
    setItemUpdating(u => ({ ...u, [product_id]: false }));
  };

  // 結帳
  const handleCheckout = async () => {
    if (!cart || !cart.items || cart.items.length === 0) {
      message.warning("購物車沒有商品");
      return;
    }
    try {
      const items = cart.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
      }));
      const res = await api.post(`/carts/${userId}/checkout`, { items });
      message.success(`結帳成功，訂單號：${res.data.order_id}`);
      fetchCart();
    } catch (err) {
      message.error("結帳失敗：" + (err.response?.data?.error || err.message));
    }
  };

  const columns = [
    { title: "商品名稱", dataIndex: "title" },
    { title: "價格", dataIndex: "price" },
    {
      title: "數量",
      dataIndex: "quantity",
      render: (quantity, record) => (
        <InputNumber
          min={1}
          value={quantity}
          onChange={val => updateQuantity(record.product_id, val)}
          disabled={itemUpdating[record.product_id]}
        />
      )
    },
    {
      title: "小計",
      render: (_, record) => <span>{(record.price * record.quantity).toFixed(2)}</span>
    },
    {
      title: "移除",
      render: (_, record) => (
        <Popconfirm
          title="確定移除這個商品？"
          onConfirm={() => removeItem(record.product_id)}
        >
          <Button danger size="small" loading={itemUpdating[record.product_id]}>
            移除
          </Button>
        </Popconfirm>
      )
    }
  ];

  const total = cart?.items?.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;
  
  let mode;
  if (!cart?.items || cart.items.length === 0) {
    mode = "user"; 
    console.log("mode:",mode) // 購物車空的，個人化推薦
  } else {
    mode = "collaborative";  
    console.log("mode:",mode) ;// 購物車有商品，協同過濾推薦
  }
  
  return (
    <div style={{ maxWidth: 700, margin: "40px auto" }}>
      <h2>我的購物車</h2>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={cart?.items || []}
          rowKey="product_id"
          pagination={false}
          footer={() => <div style={{ textAlign: "right" }}>總計：NT$ {total.toFixed(2)}</div>}
        />
      </Spin>
  
      <div style={{ textAlign: "right", marginTop: 24 }}>
        <Button type="primary" size="large" onClick={handleCheckout} disabled={!cart || !cart.items || cart.items.length === 0}>
          結帳
        </Button>
      </div>
      <RecommendList
        userId={localStorage.getItem("user_id")}
        mode={mode}
        limit={3}
      />
    </div>
  );
}

export default CartList;
