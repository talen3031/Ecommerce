import React, { useEffect, useState } from "react";
import { Table, Button, InputNumber, message, Popconfirm, Spin, Skeleton } from "antd";
import { PlusOutlined, MinusOutlined } from "@ant-design/icons";
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
    if (quantity < 1) return; // 防止數量小於1
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

  // 增加數量
  const increaseQuantity = (product_id, currentQuantity) => {
    updateQuantity(product_id, currentQuantity + 1);
  };

  // 減少數量
  const decreaseQuantity = (product_id, currentQuantity) => {
    if (currentQuantity > 1) {
      updateQuantity(product_id, currentQuantity - 1);
    }
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
      width: window.innerWidth <= 768 ? 60 : 80,
      render: (images, record) =>
        images && images.length > 0 ? (
          <img
            src={images[0]}
            alt={record.title}
            style={{ 
              width: window.innerWidth <= 768 ? 40 : 48, 
              height: window.innerWidth <= 768 ? 40 : 48, 
              objectFit: "cover", 
              borderRadius: 6, 
              cursor: "pointer" 
            }}
            onClick={() => navigate(`/products/${record.product_id}`)}
          />
        ) : (
          <span style={{ color: "#bbb", fontSize: window.innerWidth <= 768 ? '12px' : '14px' }}>無圖</span>
        )
    },
    { 
      title: "商品名稱", 
      dataIndex: "title",
      width: window.innerWidth <= 768 ? 120 : 200,
      ellipsis: window.innerWidth <= 768,
      render: (text, record) => (
        <span 
          style={{ 
            cursor: "pointer",
            fontSize: window.innerWidth <= 768 ? '13px' : '14px',
            lineHeight: window.innerWidth <= 768 ? '1.3' : '1.5'
          }}
          onClick={() => navigate(`/products/${record.product_id}`)}
          title={text}
        >
          {text}
        </span>
      )
    },
    { 
      title: "價格", 
      dataIndex: "price",
      width: window.innerWidth <= 768 ? 80 : 100,
      render: (price) => (
        <span style={{ 
          fontSize: window.innerWidth <= 768 ? '13px' : '14px',
          fontWeight: window.innerWidth <= 768 ? '600' : '500'
        }}>
          NT${price}
        </span>
      )
    },
    {
      title: "數量",
      dataIndex: "quantity",
      width: window.innerWidth <= 768 ? 120 : 160,
      render: (quantity, record) => (
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: window.innerWidth <= 768 ? '4px' : '8px',
          justifyContent: 'flex-star'
        }}>
          <Button
            size={window.innerWidth <= 768 ? "small" : "middle"}
            icon={<MinusOutlined />}
            onClick={() => decreaseQuantity(record.product_id, quantity)}
            disabled={itemUpdating[record.product_id] || quantity <= 1}
            style={{
              minWidth: window.innerWidth <= 768 ? '24px' : '32px',
              padding: window.innerWidth <= 768 ? '4px' : '4px 8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-star'
            }}
          />
          <InputNumber
            min={1}
            value={quantity}
            onChange={val => updateQuantity(record.product_id, val)}
            disabled={itemUpdating[record.product_id]}
            size={window.innerWidth <= 768 ? "small" : "middle"}
            style={{ 
              width: window.innerWidth <= 768 ? '50px' : '60px',
              fontSize: window.innerWidth <= 768 ? '12px' : '14px'
            }}
            controls={false}
          />
          <Button
            size={window.innerWidth <= 768 ? "small" : "middle"}
            icon={<PlusOutlined />}
            onClick={() => increaseQuantity(record.product_id, quantity)}
            disabled={itemUpdating[record.product_id]}
            style={{
              minWidth: window.innerWidth <= 768 ? '24px' : '32px',
              padding: window.innerWidth <= 768 ? '4px' : '4px 8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-star'
            }}
          />
        </div>
      )
    },
    {
      title: "小計",
      width: window.innerWidth <= 768 ? 80 : 100,
      render: (_, record) => (
        <span style={{ 
          fontSize: window.innerWidth <= 768 ? '13px' : '14px',
          fontWeight: window.innerWidth <= 768 ? '600' : '500',
        }}>
          NT${(record.price * record.quantity).toFixed(2)}
        </span>
      )
    },
    {
      title: "移除",
      width: window.innerWidth <= 768 ? 60 : 80,
      render: (_, record) => (
        <Popconfirm
          title="確定移除這個商品？"
          onConfirm={() => removeItem(record.product_id)}
          okText="確定"
          cancelText="取消"
        >
          <Button 
            danger 
            size={window.innerWidth <= 768 ? "small" : "middle"}
            loading={itemUpdating[record.product_id]}
            style={{
              fontSize: window.innerWidth <= 768 ? '12px' : '14px',
              padding: window.innerWidth <= 768 ? '4px 8px' : '4px 15px'
            }}
          >
            {window.innerWidth <= 768 ? '移除' : '移除'}
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
    columnWidth: window.innerWidth <= 768 ? 40 : 50,
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
      <h2 style={{ 
        fontSize: window.innerWidth <= 768 ? '1.5rem' : '2rem',
        marginBottom: window.innerWidth <= 768 ? '16px' : '24px',
        textAlign: window.innerWidth <= 768 ? 'center' : 'left'
      }}>
        我的購物車
      </h2>
      <div className="cart-table-scroll">
        {loading ? (
          <Skeleton
            active
            paragraph={false}
            title={false}
            style={{ margin: "24px 0" }}
          >
            <div style={{ height: window.innerWidth <= 768 ? 150 : 210 }}></div>
          </Skeleton>
        ) : (
          <Table
            rowSelection={rowSelection}
            columns={columns}
            dataSource={cart?.items || []}
            rowKey="product_id"
            pagination={false}
            size={window.innerWidth <= 768 ? "small" : "middle"}
            scroll={{ x: window.innerWidth <= 768 ? 600 : 800 }}
            footer={() => (
              <div style={{ 
                textAlign: "right",
                fontSize: window.innerWidth <= 768 ? '14px' : '16px',
                fontWeight: '600',
                padding: window.innerWidth <= 768 ? '8px 0' : '12px 0'
              }}>
                勾選商品總計：<span style={{ color: '#e53e3e', fontSize: window.innerWidth <= 768 ? '16px' : '18px' }}>NT$ {total.toFixed(2)}</span>
              </div>
            )}
          />
        )}
      </div>
      {/* 結帳按鈕 */}
      <div style={{ 
        textAlign: "right", 
        marginTop: window.innerWidth <= 768 ? 16 : 24,
        padding: window.innerWidth <= 768 ? '0 8px' : '0'
      }}>
        <Button
          className="checkout-btn"
          type="primary"
          size="large"
          onClick={handleGoCheckout}
          disabled={!cart || !cart.items || cart.items.length === 0}
          style={{
            width: window.innerWidth <= 768 ? '100%' : undefined,
            height: window.innerWidth <= 768 ? '44px' : '48px',
            fontSize: window.innerWidth <= 768 ? '1rem' : '1.2rem'
          }}
        >
          結帳
        </Button>
      </div>
      {/* 推薦商品 */}
      <div style={{ 
        marginTop: window.innerWidth <= 768 ? '24px' : '32px',
        padding: window.innerWidth <= 768 ? '0 8px' : '0'
      }}>
        <RecommendList 
          userId={userId} 
          mode={mode} 
          limit={window.innerWidth <= 768 ? 2 : 3} 
          onSelectProduct={handleGoDetail} 
        />
      </div>
    </div>
  );
}

export default CartList;