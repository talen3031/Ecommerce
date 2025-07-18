import React, { useEffect, useState } from "react";
import { Table, Button, InputNumber, message, Popconfirm, Spin, Skeleton } from "antd";
import RecommendList from "../../components/RecommendList";
import api from "../../api/api";
import { useNavigate } from "react-router-dom";
import '../../styles/CartList.css'

function CartList() {
  const userId = localStorage.getItem("user_id");
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [itemUpdating, setItemUpdating] = useState({});
  const [selectedRowKeys, setSelectedRowKeys] = useState([]); // 勾選項目
  const navigate = useNavigate();

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
      // 預設全選
      setSelectedRowKeys((res.data.items || []).map(item => item.product_id));
    } catch (err) {
      message.error("取得購物車失敗");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCart();
    // eslint-disable-next-line
  }, []);

  // 更新商品數量
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

  const columns = [
    {
      title: "",
      dataIndex: "images",
      render: (images, record) =>
        images && images.length > 0 ? (
          <img
            src={images[0]}
            alt={record.title}
            style={{ width: 48, height: 48, objectFit: "cover", borderRadius: 6, cursor: "pointer" }}
            onClick={() => navigate(`/products/${record.product_id}`)}
          />
        ) : (
          <span style={{ color: "#bbb" }}>無圖</span>
        )
    },
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

  // 勾選操作
  const rowSelection = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys),
    getCheckboxProps: record => ({
      // 這邊可加 disabled 等限制條件
    }),
  };

  // 計算勾選商品總金額
  const total = cart?.items
    ?.filter(item => selectedRowKeys.includes(item.product_id))
    .reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;

  // 推薦模式
  let mode;
  if (!cart?.items || cart.items.length === 0) {
    mode = "user"; // 購物車空的，個人化推薦
  } else {
    mode = "collaborative"; // 有商品，協同過濾推薦
  }

  // 推薦商品點擊
  const handleGoDetail = (id) => navigate(`/products/${id}`);

  // 結帳跳轉，只帶勾選商品
  const handleGoCheckout = () => {
    if (!cart || !cart.items || cart.items.length === 0) {
      message.error("購物車為空！");
      return;
    }
    const selectedItems = cart.items.filter(item => selectedRowKeys.includes(item.product_id));
    if (selectedItems.length === 0) {
      message.error("請至少勾選一項商品！");
      return;
    }
    // 結帳頁只帶勾選商品
    navigate("/checkout", {
      state: { cart: { ...cart, items: selectedItems } }
    });
  };

  return (
    <div className="cart-container">
      <h2>我的購物車</h2>
      <div className="cart-table-scroll">
        {loading ? (
          <Skeleton
            active
            paragraph={false}
            title={false}
            style={{ margin: "24px 0" }}
          >
            <div style={{ height: 210 }}></div>
          </Skeleton>
        ) : (
          <Table
            rowSelection={rowSelection}
            columns={columns}
            dataSource={cart?.items || []}
            rowKey="product_id"
            pagination={false}
            footer={() => (
              <div style={{ textAlign: "right" }}>
                勾選商品總計：NT$ {total.toFixed(2)}
              </div>
            )}
          />
        )}
      </div>
      {/* 結帳按鈕 */}
      <div style={{ textAlign: "right", marginTop: 24 }}>
        <Button
          className="checkout-btn"
          type="primary"
          size="large"
          onClick={handleGoCheckout}
          disabled={!cart || !cart.items || cart.items.length === 0}
        >
          結帳
        </Button>

      </div>
      {/* 推薦商品 */}
      <RecommendList userId={userId} mode={mode} limit={3} onSelectProduct={handleGoDetail} />
    </div>
  );
}

export default CartList;
