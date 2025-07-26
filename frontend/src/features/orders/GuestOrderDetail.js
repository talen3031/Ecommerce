import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Card, Spin, Table, Button, Modal, Descriptions, message } from "antd";
import api from "../../api/api";

const STATUS_LABEL_MAP = {
  pending: "待處理",
  paid: "已付款",
  processing: "處理中",
  shipped: "運送中",
  delivered: "已到貨",
  cancelled: "已取消",
  refunded: "已退款",
  returned: "已退貨"
};

function formatDate(str) {
  if (!str) return "";
  const d = new Date(str);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

// 計算原始總金額
function calcOriginalTotal(items = []) {
  return items.reduce(
    (sum, r) =>
      sum +
      (r.sale_price && r.sale_price !== r.price ? r.sale_price : r.price) * r.quantity,
    0
  );
}

// 顯示金額區塊
function OrderAmountInfo({ orderDetail }) {
  if (!orderDetail) return null;
  const hasDiscount =
    orderDetail.discount_amount && Number(orderDetail.discount_amount) > 0;
  const total = calcOriginalTotal(orderDetail.items);

  if (hasDiscount) {
    return (
      <div style={{
        marginTop: 16,
        background: "#fafbfc",
        border: "1px solid #e5e6e8",
        borderRadius: 8,
        padding: "14px 18px 8px 18px",
        maxWidth: 380,
        marginLeft: "auto"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
          <div style={{ color: "#555" }}>總金額：</div>
          <div>NT$ {total}</div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
          <div style={{ color: "#fa541c" }}>折扣金額：</div>
          <div>- NT$ {orderDetail.discount_amount}</div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700 }}>
          <div style={{ color: "#1890ff" }}>折扣後金額：</div>
          <div>NT$ {orderDetail.total}</div>
        </div>
      </div>
    );
  } else {
    return (
      <div style={{
        marginTop: 16,
        background: "#fafbfc",
        border: "1px solid #e5e6e8",
        borderRadius: 8,
        padding: "14px 18px 8px 18px",
        maxWidth: 380,
        marginLeft: "auto"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700 }}>
          <div style={{ color: "#555" }}>總金額：</div>
          <div>NT$ {orderDetail.total}</div>
        </div>
      </div>
    );
  }
}

function GuestOrderDetail() {
  const [searchParams] = useSearchParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [cancelling, setCancelling] = useState(false);
  // 圖片預覽
  const [previewImage, setPreviewImage] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  // 重新查詢訂單
  const fetchOrder = () => {
    setLoading(true);
    const guest_id = searchParams.get("guest_id");
    const order_id = searchParams.get("order_id");
    const email =searchParams.get("email") 
    if (!guest_id || !order_id || !email) {
      setErrorMsg("訂單明細查詢失敗");
      setLoading(false);
      return;
    }
    api.get(`/orders/guest/${guest_id}/${order_id}?email=${encodeURIComponent(email)}`)
      .then(res => {
        setOrder(res.data);
        setErrorMsg("");
      })
      .catch(() => {
        setOrder(null);
        setErrorMsg("找不到訂單或資訊錯誤");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchOrder();
    // eslint-disable-next-line
  }, [searchParams]);

  const handleCancelOrder = () => {
    Modal.confirm({
      title: "確定要取消訂單嗎？",
      okText: "確定取消",
      cancelText: "返回",
      onOk: async () => {
        setCancelling(true);
        const guest_id = searchParams.get("guest_id");
        const order_id = searchParams.get("order_id");
        const email = searchParams.get("email");
        try {
          await api.post(`/orders/guest/${guest_id}/${order_id}/cancel`, { email });
          message.success("訂單已取消");
          fetchOrder();
        } catch (err) {
          message.error("取消訂單失敗：" + (err.response?.data?.error || err.message));
        }
        setCancelling(false);
      }
    });
  };

  if (loading) {
    return <Spin style={{ marginTop: 48 }} />;
  }

  if (errorMsg) {
    return <div style={{ color: "#f5222d", fontSize: 18, textAlign: "center", marginTop: 48 }}>{errorMsg}</div>;
  }

  if (!order) return null;

  return (
    <div style={{ maxWidth: 600, margin: "32px auto", background: "#fff", borderRadius: 12, boxShadow: "0 4px 24px #eee", padding: 28 }}>
      <h2 style={{ marginBottom: 16 }}>訂單明細</h2>
      <Descriptions column={1} bordered>
        <Descriptions.Item label="訂單編號">{order.order_id}</Descriptions.Item>
        <Descriptions.Item label="下單時間">{formatDate(order.order_date)}</Descriptions.Item>
        <Descriptions.Item label="訂單狀態">
          <span style={{
            color: order.status === "cancelled" ? "#f5222d" : "#222",
            fontWeight: order.status === "cancelled" ? 600 : 400
          }}>
            {STATUS_LABEL_MAP[order.status] || order.status}
          </span>
        </Descriptions.Item>
        <Descriptions.Item label="訂單金額">NT$ {order.total}</Descriptions.Item>
      </Descriptions>

      <h4 style={{ marginTop: 24 }}>商品清單</h4>
      <Table
        dataSource={order.items || []}
        rowKey="product_id"
        pagination={false}
        size="small"
        columns={[
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
                  title="點擊可放大"
                />
              ) : (
                <span style={{ color: "#bbb" }}>無圖</span>
              )
          },
          { title: "商品名稱", dataIndex: "title" },
          {
            title: "單價",
            render: (_, r) => (
              r.sale_price && r.sale_price !== r.price ? (
                <>
                  <span style={{ color: "#fa541c", fontWeight: 600 }}>NT${r.sale_price}</span>
                  <span style={{ textDecoration: "line-through", color: "#888", marginLeft: 7, fontSize: 13 }}>NT${r.price}</span>
                </>
              ) : (
                <span>NT${r.price}</span>
              )
            )
          },
          { title: "數量", dataIndex: "quantity" },
          {
            title: "小計",
            render: (_, r) => {
              const subtotal = (r.sale_price && r.sale_price !== r.price ? r.sale_price : r.price) * r.quantity;
              return <span>NT${subtotal}</span>;
            }
          },
        ]}
      />

      {/* 寄送資訊 */}
      {order.shipping_info && (
        <div style={{ margin: "24px 0 0 0" }}>
          <h4>寄送資訊</h4>
          <Descriptions column={1} bordered size="small" style={{ maxWidth: 390 }}>
            <Descriptions.Item label="寄送方式">{order.shipping_info.shipping_method}</Descriptions.Item>
            <Descriptions.Item label="收件人">{order.shipping_info.recipient_name}</Descriptions.Item>
            <Descriptions.Item label="收件人電話">{order.shipping_info.recipient_phone}</Descriptions.Item>
            <Descriptions.Item label="Email">{order.shipping_info.recipient_email}</Descriptions.Item>
            <Descriptions.Item label="門市/地址">{order.shipping_info.store_name}</Descriptions.Item>
          </Descriptions>
        </div>
      )}
      {/* 金額總結資訊依折扣條件顯示 */}
      <OrderAmountInfo orderDetail={order} />

      {/* 只有特定狀態才可取消 */}
      {order && !["cancelled", "delivered", "refunded", "returned"].includes(order.status) && (
        <div style={{ textAlign: "right", marginTop: 24 }}>
          <Button
            danger
            type="primary"
            loading={cancelling}
            onClick={handleCancelOrder}
          >
            取消訂單
          </Button>
        </div>
      )}

      {/* 放大圖 Modal */}
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

export default GuestOrderDetail;
