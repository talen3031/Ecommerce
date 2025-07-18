import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Table, Input, Button, Select, Form, message, Modal } from "antd";
import api from "../../api/api";
import '../../styles/CheckoutPage.css'

function CheckoutPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { cart } = location.state || {};
  const [loading, setLoading] = useState(false);

  // 折扣碼
  const [discountCode, setDiscountCode] = useState("");
  const [discountInfo, setDiscountInfo] = useState(null);
  const [discountMsg, setDiscountMsg] = useState("");
  const [discountRuleMsg, setDiscountRuleMsg] = useState("");
  const [applyingDiscount, setApplyingDiscount] = useState(false);

  // Modal 狀態（送出結果用）
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState({ title: "", content: "", success: false });

  // 新增：送出前確認 Modal
  const [confirmVisible, setConfirmVisible] = useState(false);
  const [pendingOrder, setPendingOrder] = useState(null);

  // Form 實例
  const [form] = Form.useForm();

  const [previewImage, setPreviewImage] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  // 商品列表欄位
  const columns = [
    {
      title: "",
      dataIndex: "images",
      render: (images, record) =>
        images && images.length > 0 ? (
          <img
            src={images[0]}
            alt={record.title}
            style={{ width: 48, height: 48, objectFit: "cover", borderRadius: 6, cursor: "zoom-in" }}
            onClick={() => {
              setPreviewImage(images[0]);
              setPreviewOpen(true);
            }}
          />
        ) : (
          <span style={{ color: "#bbb" }}>無圖</span>
        )
    },

    { title: "商品名稱", dataIndex: "title" },
    { title: "價格", dataIndex: "price" },
    { title: "數量", dataIndex: "quantity" },
    {
      title: "小計",
      render: (_, record) => (record.price * record.quantity).toFixed(2)
    }
  ];

  // 計算金額
  const total = cart?.items?.reduce((sum, item) => sum + item.price * item.quantity, 0) || 0;

  // 套用折扣碼
  const applyDiscount = async () => {
    if (!discountCode) {
      setDiscountMsg("請輸入折扣碼");
      setDiscountRuleMsg("");
      setDiscountInfo("");
      return;
    }
    setDiscountMsg("");
    setDiscountRuleMsg(""); // 清除前一次的規則訊息
    setApplyingDiscount(true);
    try {
      const userId = localStorage.getItem("user_id");
      const res = await api.post(`/carts/${userId}/apply_discount`, { code: discountCode });

      if (res.data.success && res.data.used_coupon) {
        setDiscountInfo(res.data);
        setDiscountMsg("折扣碼套用成功！");
        setDiscountRuleMsg(res.data.rule_msg || ""); // 顯示規則訊息
      } else if (res.data.success && !res.data.used_coupon) {
        setDiscountInfo(null);
        setDiscountMsg("折扣碼未套用");
        setDiscountRuleMsg(res.data.rule_msg || "");
      } else {
        setDiscountInfo(null);
        setDiscountMsg(res.data.message || "折扣碼無效");
        setDiscountRuleMsg(res.data.rule_msg || "");
      }
    } catch (err) {
      setDiscountInfo(null);
      setDiscountMsg("套用失敗：" + (err.response?.data?.error || err.message));
      setDiscountRuleMsg("");
    }
    setApplyingDiscount(false);
  };


  // **原本 onFinish 內容移到這**
  const handleCheckout = async (values) => {
    const userId = localStorage.getItem("user_id");
    setLoading(true);
    try {
      const items = cart.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity
      }));
      const body = {
        items,
        shipping_info: {
          shipping_method: values.shipping_method,
          recipient_name: values.recipient_name,
          recipient_phone: values.recipient_phone,
          store_name: values.store_name
        }
      };
      if (discountInfo && discountInfo.success && discountInfo.discount_code?.code) {
        body.discount_code = discountInfo.discount_code.code;
      }
      const res = await api.post(`/carts/${userId}/checkout`, body);
      setModalContent({
        title: "下單成功",
        content: `訂單號：${res.data.order_id}`,
        success: true
      });
      setModalOpen(true);
      setTimeout(() => {
      setModalOpen(false);
      navigate("/orders");
        }, 1200);
      } catch (err) {
        setModalContent({
          title: "結帳失敗",
          content: err.response?.data?.error || err.message,
          success: false
        });
        setModalOpen(true);
      }
      setLoading(false);
};

  // **新的 onFinish：先彈出確認 Modal**
  const handleFormFinish = (values) => {
    setPendingOrder(values);
    setConfirmVisible(true);
  };

  return (
    <div style={{ maxWidth: 580, margin: "40px auto" }}>
      <h2>訂單結帳</h2>
      <Table
        columns={columns}
        dataSource={cart?.items || []}
        rowKey="product_id"
        pagination={false}
        footer={() => (
          <div style={{ textAlign: "right" }}>
            總計：NT$ {total}
          </div>
        )}
      />

      {/* 折扣碼功能區 */}
      <div style={{ marginTop: 24, textAlign: "right" }}>
        <Input
          placeholder="輸入折扣碼"
          value={discountCode}
          style={{ width: 200, marginRight: 8 }}
          onChange={e => setDiscountCode(e.target.value)}
          disabled={applyingDiscount}
        />
        <Button className="dicount-btn" onClick={applyDiscount} loading={applyingDiscount}>
          套用折扣碼
        </Button>
        {discountMsg && (
          <div style={{ marginTop: 8, color: "#faad14" }}>
            {discountMsg && (
                <div style={{ marginTop: 8, color: "#faad14" }}>
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
                    textAlign: "right",
                    marginLeft: "auto"
                  }}
                >
                  {discountRuleMsg}
                </div>
              )}

          </div>
        )}
        {discountInfo && discountInfo.success && (
          <div style={{ marginTop: 8, color: "#fa541c" }}>
            折扣後總計：NT$ {discountInfo.discounted_total}，已折抵 NT$ {discountInfo.discount_amount}
            <br />
            <span style={{ color: "#888", fontSize: 12 }}>{discountInfo.discount_code?.description}</span>
          </div>
        )}
      </div>

      <h3 style={{ marginTop: 24 }}>寄送資訊</h3>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFormFinish} // 攔截、先不直接送出
        initialValues={{
          shipping_method: "711",
          recipient_name: "",
          recipient_phone: "",
          store_name: ""
        }}
        style={{ marginTop: 8 }}
      >
        <Form.Item
          label="寄送方式"
          name="shipping_method"
          rules={[{ required: true, message: "請選擇寄送方式" }]}
        >
          <Select>
            <Select.Option value="711">711 超商取貨</Select.Option>
            <Select.Option value="FamilyMart">全家超商取貨</Select.Option>
          </Select>
        </Form.Item>
        <Form.Item
          label="收件人姓名"
          name="recipient_name"
          rules={[{ required: true, message: "請輸入收件人姓名" }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="收件人電話"
          name="recipient_phone"
          rules={[
            { required: true, message: "請輸入收件人電話" },
            { pattern: /^09\d{8}$/, message: "請輸入正確的手機號碼格式（09開頭共10碼）" }
          ]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="取貨門市/地址"
          name="store_name"
          rules={[{ required: true, message: "請輸入取貨門市或地址" }]}
        >
          <Input />
        </Form.Item>
        <Form.Item>
          <Button className="final_checkout-btn" htmlType="submit" loading={loading} size="large" style={{ float: "right" }}>
          確定結帳
        </Button>
        </Form.Item>
      </Form>

      {/* ======= 新增：送出前確認 Modal ======= */}
      <Modal
        open={confirmVisible}
        title="請確認訂單資訊"
        onCancel={() => setConfirmVisible(false)}
        footer={[
          <Button key="back" className="cancel-btn" onClick={() => setConfirmVisible(false)}>
            取消
          </Button>,
          <Button
            key="submit"
            className="send_order-btn"
            loading={loading}
            onClick={() => {
              setConfirmVisible(false);
              handleCheckout(pendingOrder);
            }}
          >
            送出
          </Button>,
        ]}
        centered
      >
        <div>
          <b>商品明細：</b>
          <ul>
            {(cart?.items || []).map(item => (
              <li key={item.product_id}>
                {item.title} × {item.quantity}（NT${item.price}）小計：NT${(item.price * item.quantity).toFixed(2)}
              </li>
            ))}
          </ul>
          <div style={{ margin: "8px 0" }}>
            <b>寄送方式：</b> {pendingOrder?.shipping_method}<br />
            <b>收件人：</b> {pendingOrder?.recipient_name}<br />
            <b>電話：</b> {pendingOrder?.recipient_phone}<br />
            <b>取貨門市/地址：</b> {pendingOrder?.store_name}
          </div>
          <div>
            <b>原始總金額：</b> NT$ {total}
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

      {/* 結帳提示 Modal */}
    <Modal
        open={modalOpen}
        title={modalContent.title}
        // 成功時不能關閉（不能點外面，也沒按鈕）
        onCancel={() => {
          if (!modalContent.success) setModalOpen(false);
        }}
        footer={
          modalContent.success
            ? null // 成功時沒有按鈕
            : [
                <Button key="ok" type="primary" onClick={() => setModalOpen(false)}>
                  關閉
                </Button>
              ]
        }
        maskClosable={modalContent.success ? false : true}
        centered
      >
        <div style={{ textAlign: "center", fontSize: 17 }}>{modalContent.content}</div>
      </Modal>
      <Modal
        open={previewOpen}
        footer={null}
        onCancel={() => setPreviewOpen(false)}
        bodyStyle={{ textAlign: "center" }}
      >
        {previewImage && (
          <img
            src={previewImage}
            alt="放大圖"
            style={{ maxWidth: "92vw", maxHeight: "78vh", borderRadius: 12 }}
          />
        )}
      </Modal>
    </div>
  );
}

export default CheckoutPage;
