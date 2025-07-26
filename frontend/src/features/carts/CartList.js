import React, { useEffect, useState } from "react";
import { Table, Button, InputNumber, message, Popconfirm, Spin, Skeleton, Input, Modal } from "antd";
import { PlusOutlined, MinusOutlined } from "@ant-design/icons";
import RecommendList from "../../components/RecommendList";
import api from "../../api/api";
import { useNavigate } from "react-router-dom";
import '../../styles/CartList.css'
import { getGuestId } from "../../api/api";;
function CartList() {
  const userId = localStorage.getItem("user_id");
  const guestId = getGuestId();
  const isLogin = !!userId;
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [itemUpdating, setItemUpdating] = useState({});
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [checkoutModalVisible, setCheckoutModalVisible] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);
  // 折扣碼相關
  const [discountCode, setDiscountCode] = useState("");
  const [discountInfo, setDiscountInfo] = useState(null);
  const [discountMsg, setDiscountMsg] = useState("");
  const [applyingDiscount, setApplyingDiscount] = useState(false);
  const [discountRuleMsg, setDiscountRuleMsg] = useState("");

  const navigate = useNavigate();

  // 取得購物車資料
  const fetchCart = async () => {
    setLoading(true);
    try {
      let res;
      if (isLogin) {
        res = await api.get(`/carts/${userId}`);
      } else {
        res = await api.get(`/carts/guest/${guestId}`);
      }
      setCart(res.data);
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
    if (quantity < 1) return;
    setItemUpdating(u => ({ ...u, [product_id]: true }));
    try {
      if (isLogin) {
        await api.put(`/carts/${userId}`, { product_id, quantity });
      } else {
        await api.put(`/carts/guest/${guestId}`, { product_id, quantity });
      }
      message.success("已更新數量");
      fetchCart();
    } catch (err) {
      message.error("更新數量失敗");
    }
    setItemUpdating(u => ({ ...u, [product_id]: false }));
  };

  // 增加/減少數量
  const increaseQuantity = (product_id, currentQuantity) => {
    updateQuantity(product_id, currentQuantity + 1);
  };
  const decreaseQuantity = (product_id, currentQuantity) => {
    if (currentQuantity > 1) {
      updateQuantity(product_id, currentQuantity - 1);
    }
  };

  // 移除商品
  const removeItem = async (product_id) => {
    setItemUpdating(u => ({ ...u, [product_id]: true }));
    try {
      if (isLogin) {
        await api.delete(`/carts/${userId}`, { data: { product_id } });
      } else {
        await api.delete(`/carts/guest/${guestId}`, { data: { product_id } });
      }
      message.success("已移除商品");
      fetchCart();
    } catch (err) {
      message.error("移除失敗");
    }
    setItemUpdating(u => ({ ...u, [product_id]: false }));
  };

  

  // 勾選操作
  const rowSelection = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys),
    columnWidth: window.innerWidth <= 768 ? 40 : 50,
  };

  // 計算勾選商品總金額
  const total = cart?.items
    ?.filter(item => selectedRowKeys.includes(item.product_id))
    .reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;

  // 推薦模式
  let mode;
  if (!cart?.items || cart.items.length === 0) {
    mode = isLogin ? "user" : "cart";
  } else {
    mode = "collaborative";
  }
  // 推薦商品點擊
  const handleGoDetail = (id) => navigate(`/products/${id}`);

  // 結帳
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
  // 跳轉到 CheckoutPage，帶勾選商品資料
  navigate("/checkout", {
    state: { cart: { ...cart, items: selectedItems } }
  });
  };


  // 真正送出結帳（後端如果需要 shipping_info，這裡可加一個簡單表單或填預設資料）
  const handleRealCheckout = async () => {
    setConfirmLoading(true);
    try {
      const items = cart.items.filter(item => selectedRowKeys.includes(item.product_id))
        .map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        }));
      const body = { items };
      if (discountInfo && discountInfo.success && discountInfo.discount_code?.code) {
        body.discount_code = discountInfo.discount_code.code;
      }
      // 若後端需要 shipping_info，這裡請用彈窗或預設資料
      body.shipping_info = { recipient_name: isLogin ? "會員" : "訪客", recipient_phone: "0912345678", store_name: "填寫地址" };
      let res;
      if (isLogin) {
        res = await api.post(`/carts/${userId}/checkout`, body);
      } else {
        res = await api.post(`/carts/guest/${guestId}/checkout`, body);
      }
      message.success(`結帳成功，訂單號：${res.data.order_id}`);
      setDiscountInfo(null);
      setDiscountCode("");
      setDiscountMsg("");
      setCheckoutModalVisible(false);
      fetchCart();
    } catch (err) {
      message.error("結帳失敗：" + (err.response?.data?.error || err.message));
    }
    setConfirmLoading(false);
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
            style={{ width: window.innerWidth <= 768 ? 40 : 48, height: window.innerWidth <= 768 ? 40 : 48, objectFit: "cover", borderRadius: 6, cursor: "pointer" }}
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
          style={{ cursor: "pointer", fontSize: window.innerWidth <= 768 ? '13px' : '14px', lineHeight: window.innerWidth <= 768 ? '1.3' : '1.5' }}
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
        <span style={{ fontSize: window.innerWidth <= 768 ? '13px' : '14px', fontWeight: window.innerWidth <= 768 ? '600' : '500' }}>
          NT${price}
        </span>
      )
    },
    {
      title: "數量",
      dataIndex: "quantity",
      width: window.innerWidth <= 768 ? 120 : 160,
      render: (quantity, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: window.innerWidth <= 768 ? '4px' : '8px', justifyContent: 'flex-star' }}>
          <Button
            size={window.innerWidth <= 768 ? "small" : "middle"}
            icon={<MinusOutlined />}
            onClick={() => decreaseQuantity(record.product_id, quantity)}
            disabled={itemUpdating[record.product_id] || quantity <= 1}
            style={{ minWidth: window.innerWidth <= 768 ? '24px' : '32px', padding: window.innerWidth <= 768 ? '4px' : '4px 8px', display: 'flex', alignItems: 'center', justifyContent: 'flex-star' }}
          />
          <InputNumber
            min={1}
            value={quantity}
            onChange={val => updateQuantity(record.product_id, val)}
            disabled={itemUpdating[record.product_id]}
            size={window.innerWidth <= 768 ? "small" : "middle"}
            style={{ width: window.innerWidth <= 768 ? '50px' : '60px', fontSize: window.innerWidth <= 768 ? '12px' : '14px' }}
            controls={false}
          />
          <Button
            size={window.innerWidth <= 768 ? "small" : "middle"}
            icon={<PlusOutlined />}
            onClick={() => increaseQuantity(record.product_id, quantity)}
            disabled={itemUpdating[record.product_id]}
            style={{ minWidth: window.innerWidth <= 768 ? '24px' : '32px', padding: window.innerWidth <= 768 ? '4px' : '4px 8px', display: 'flex', alignItems: 'center', justifyContent: 'flex-star' }}
          />
        </div>
      )
    },
    {
      title: "小計",
      width: window.innerWidth <= 768 ? 80 : 100,
      render: (_, record) => (
        <span style={{ fontSize: window.innerWidth <= 768 ? '13px' : '14px', fontWeight: window.innerWidth <= 768 ? '600' : '500', }}>
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
            style={{ fontSize: window.innerWidth <= 768 ? '12px' : '14px', padding: window.innerWidth <= 768 ? '4px 8px' : '4px 15px' }}
          >
            移除
          </Button>
        </Popconfirm>
      )
    }
  ];

  return (
    <div className="cart-container">
      <h2 style={{ fontSize: window.innerWidth <= 768 ? '1.5rem' : '2rem', marginBottom: window.innerWidth <= 768 ? '16px' : '24px', textAlign: window.innerWidth <= 768 ? 'center' : 'left' }}>
        {isLogin ? "我的購物車" : "訪客購物車"}
      </h2>
      <div className="cart-table-scroll">
        {loading ? (
          <Skeleton active paragraph={false} title={false} style={{ margin: "24px 0" }}>
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
              <div style={{ textAlign: "right", fontSize: window.innerWidth <= 768 ? '14px' : '16px', fontWeight: '600', padding: window.innerWidth <= 768 ? '8px 0' : '12px 0' }}>
                勾選商品總計：<span style={{ color: '#e53e3e', fontSize: window.innerWidth <= 768 ? '16px' : '18px' }}>NT$ {total.toFixed(2)}</span>
              </div>
            )}
          />
        )}
      </div>
      
      
      {/* 結帳按鈕 */}
      <div style={{ textAlign: "right", marginTop: window.innerWidth <= 768 ? 16 : 24, padding: window.innerWidth <= 768 ? '0 8px' : '0' }}>
        <Button
          className="checkout-btn"
          type="primary"
          size="large"
          onClick={handleGoCheckout}
          disabled={!cart || !cart.items || cart.items.length === 0}
          style={{ width: window.innerWidth <= 768 ? '100%' : undefined, height: window.innerWidth <= 768 ? '44px' : '48px', fontSize: window.innerWidth <= 768 ? '1rem' : '1.2rem' }}
        >
          結帳
        </Button>
      </div>
      {/* 結帳 Modal（確認明細、可擴充收件人欄位） */}
      <Modal
        open={checkoutModalVisible}
        title="訂單確認"
        onCancel={() => setCheckoutModalVisible(false)}
        onOk={handleRealCheckout}
        confirmLoading={confirmLoading}
        okText="確定結帳"
        cancelText="取消"
      >
        <div>
          <b>訂單內容：</b>
          <ul>
            {(cart?.items || []).filter(item => selectedRowKeys.includes(item.product_id)).map(item => (
              <li key={item.product_id}>
                {item.title} × {item.quantity}（NT${item.price}）小計：NT${(item.price * item.quantity).toFixed(2)}
              </li>
            ))}
          </ul>
          <div style={{ marginTop: 12 }}>
            原始總金額：NT$ {total.toFixed(2)}
            {discountInfo && discountInfo.success && (
              <div style={{ color: "#fa541c" }}>
                折扣後總計：NT$ {discountInfo.discounted_total}，已折抵 NT$ {discountInfo.discount_amount}
              </div>
            )}
          </div>
          {discountInfo && discountInfo.discount_code?.description && (
            <div style={{ color: "#888", fontSize: 12 }}>({discountInfo.discount_code.description})</div>
          )}
        </div>
      </Modal>
      {/* 推薦商品 */}
      {isLogin && (
          <div style={{ marginTop: window.innerWidth <= 768 ? '24px' : '32px', padding: window.innerWidth <= 768 ? '0 8px' : '0' }}>
            <RecommendList
              userId={userId}
              mode={mode}
              limit={window.innerWidth <= 768 ? 2 : 3}
              onSelectProduct={handleGoDetail}
            />
          </div>
        )}
      
    </div>
  );
}

export default CartList;
