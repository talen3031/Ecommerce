import React, { useEffect, useState } from "react";
import { Modal, Table, Button, InputNumber, message, Popconfirm, Spin, Input, Skeleton } from "antd";
import RecommendList from "./RecommendList";
import api from "./api";
import { useNavigate } from "react-router-dom";
import './CartList.css'

function CartList() {
  const userId = localStorage.getItem("user_id");
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [itemUpdating, setItemUpdating] = useState({});
  const [checkoutModalVisible, setCheckoutModalVisible] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);

  // 折扣碼功能
  const [discountCode, setDiscountCode] = useState("");
  const [discountInfo, setDiscountInfo] = useState(null);
  const [discountMsg, setDiscountMsg] = useState("");
  const [applyingDiscount, setApplyingDiscount] = useState(false);
  const [discountRuleMsg, setDiscountRuleMsg] = useState(""); // 新增
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

  // 套用折扣碼
  const applyDiscount = async () => {
    if (!discountCode) {
      setDiscountMsg("請輸入折扣碼");
      return;
    }
    setDiscountMsg("");
    setDiscountRuleMsg(""); 
    setApplyingDiscount(true);
    try {
      const res = await api.post(`/carts/${userId}/apply_discount`, { code: discountCode });
      if (res.data.success&&res.data.used_coupon) {
        setDiscountInfo(res.data);
        setDiscountMsg("折扣碼套用成功！");
        setDiscountRuleMsg(res.data.rule_msg || ""); // ← 這裡把rule_msg存起來
      }else if(res.data.success&&!res.data.used_coupon) {
        setDiscountInfo(null);
        setDiscountMsg("折扣碼未套用");
        setDiscountRuleMsg(res.data.rule_msg || ""); 
      }
      else {
        setDiscountInfo(null);
        setDiscountMsg(res.data.message || "折扣碼無效");
        setDiscountRuleMsg(res.data.rule_msg || ""); // ← 失敗時也顯示
      }
    } catch (err) {
      setDiscountInfo(null);
      setDiscountMsg("套用失敗：" + (err.response?.data?.error || err.message));
      setDiscountRuleMsg(""); // 發生錯誤時不顯示規則
    }
    setApplyingDiscount(false);
  };

  // 結帳 Modal 中按「確定結帳」才會送出訂單
  const handleRealCheckout = async () => {
    setConfirmLoading(true);
    try {
      const items = cart.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
      }));
      const body = { items };
      if (discountInfo && discountInfo.success && discountInfo.discount_code?.code) {
        body.discount_code = discountInfo.discount_code.code;
      }
      const res = await api.post(`/carts/${userId}/checkout`, body);
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

  // 計算原始總金額
  const total = cart?.items?.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;

  // 推薦模式
  let mode;
  if (!cart?.items || cart.items.length === 0) {
    mode = "user"; // 購物車空的，個人化推薦
  } else {
    mode = "collaborative"; // 有商品，協同過濾推薦
  }

  // 推薦商品點擊
  const handleGoDetail = (id) => navigate(`/products/${id}`);

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
                {/* 假裝有一個空的表格 */}
                <div style={{ height: 210 }}></div>
              </Skeleton>
            ) : (
              <Table
                columns={columns}
                dataSource={cart?.items || []}
                rowKey="product_id"
                pagination={false}
                footer={() => (
                  <div style={{ textAlign: "right" }}>
                    總計：NT$ {total.toFixed(2)}
                  </div>
                )}
              />
            )}
      </div>
      {/* 折扣碼功能區 */}
     <div className="cart-discount-area" style={{ marginTop: 16, textAlign: "right" }}>
      <Input
        placeholder="輸入折扣碼"
        value={discountCode}
        style={{ width: 200, marginRight: 8 }}
        onChange={e => setDiscountCode(e.target.value)}
        disabled={applyingDiscount}
      />
        <Button type="primary" onClick={applyDiscount} loading={applyingDiscount}>
          套用折扣碼
        </Button>
      </div>
      {/* 顯示後端回傳 message */}
      {discountMsg && (
        <div style={{ marginTop: 8, color: "#faad14", textAlign: "right" }}>
          {discountMsg}
        </div>
      )}
      {discountRuleMsg && (
          <div
            style={{
              marginTop: 4,
              color: "#666",
              fontSize: 13,
              maxWidth: 350,
              whiteSpace: "pre-line",
              wordBreak: "break-word",
              lineHeight: 1.7,
              textAlign: "right", // 跟 discountMsg 靠齊
              marginLeft: "auto", // 可加，讓它真的貼齊右邊
            }}
          >
            {discountRuleMsg}
          </div>
        )}
      {/* 顯示折扣資訊 */}
      {discountInfo && discountInfo.success && (
        <div style={{ marginTop: 8, color: "#fa541c", textAlign: "right" }}>
          折扣後總計：NT$ {discountInfo.discounted_total}，已折抵 NT$ {discountInfo.discount_amount}
          <br />
          <span style={{ color: "#888", fontSize: 12 }}>{discountInfo.discount_code?.description}</span>
        </div>
      )}
      {/* 結帳按鈕 */}
      <div style={{ textAlign: "right", marginTop: 24 }}>
        <Button
          type="primary"
          size="large"
          onClick={() => { setCheckoutModalVisible(true); }}
          disabled={!cart || !cart.items || cart.items.length === 0}
        >
          結帳
        </Button>
      </div>
      {/* 結帳前確認 Modal */}
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
            {(cart?.items || []).map(item => (
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
      <RecommendList userId={userId} mode={mode} limit={3} onSelectProduct={handleGoDetail} />
    </div>
  );
}

export default CartList;
