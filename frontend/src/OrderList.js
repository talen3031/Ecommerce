import React, { useEffect, useState } from "react";
import { Table, Button, message, Spin, Descriptions, Drawer, Popconfirm } from "antd";
import api from "./api";
import { useNavigate, useParams, useLocation } from "react-router-dom";

function OrderList() {
  const userId = localStorage.getItem("user_id");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams();

  // 取得所有訂單
  const fetchOrders = async () => {
    if (!userId) {
      message.error("請先登入");
      return;
    }
    setLoading(true);
    try {
      const res = await api.get(`/orders/${userId}`);
      setOrders(res.data.orders || []);
    } catch (err) {
      message.error("查詢訂單失敗");
    }
    setLoading(false);
  };

  // 取消訂單
  const handleCancelOrder = async (orderId) => {
    try {
      await api.post(`/orders/${orderId}/cancel`);
      message.success("已取消訂單！");
      fetchOrders();
    } catch (err) {
      message.error("取消失敗：" + (err.response?.data?.error || err.message));
    }
  };

  useEffect(() => {
    fetchOrders();
    // eslint-disable-next-line
  }, []);

  const columns = [
    { title: "訂單編號", dataIndex: "id" },
    {
      title: "訂單時間",
      dataIndex: "order_date",
      render: (value) => formatDateandhours(value),
    },
    { title: "狀態", dataIndex: "status" },
    { title: "總金額", dataIndex: "total" },
    {
      title: "操作",
      render: (_, record) => (
        <span>
          <Button
            style={{ marginRight: 8 }}
            onClick={() => navigate(`/orders/${record.id}`)}
          >
            查看明細
          </Button>
          {/* 只要訂單不是已取消才顯示取消按鈕 */}
          {record.status !== "已取消" && (
            <Popconfirm
              title="你確定要取消這筆訂單嗎？"
              okText="確定"
              cancelText="取消"
              onConfirm={() => handleCancelOrder(record.id)}
            >
              <Button danger type="primary">取消</Button>
            </Popconfirm>
          )}
        </span>
      ),
    },
  ];

  // 判斷有沒有 orderId（顯示 drawer）
  const match = location.pathname.match(/^\/orders\/(\d+)/);
  const drawerOrderId = match ? match[1] : null;

  return (
    <div style={{ maxWidth: 900, margin: "40px auto" }}>
      <h2>我的訂單</h2>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          pagination={false}
        />
      </Spin>
      {/* drawer 根據網址是否為 /orders/:orderId 顯示 */}
      <OrderDetailDrawer
        open={!!drawerOrderId}
        orderId={drawerOrderId}
        onClose={() => navigate("/orders")}
      />
    </div>
  );
}

// Drawer元件，根據 orderId 讀取訂單詳情
function OrderDetailDrawer({ open, orderId, onClose }) {
  const [detailLoading, setDetailLoading] = useState(false);
  const [orderDetail, setOrderDetail] = useState(null);

  useEffect(() => {
    if (!open || !orderId) return;
    setDetailLoading(true);
    api.get(`/orders/order/${orderId}`)
      .then(res => setOrderDetail(res.data))
      .catch(() => setOrderDetail(null))
      .finally(() => setDetailLoading(false));
  }, [open, orderId]);

  return (
    <Drawer
      title={`訂單明細 ${orderDetail?.id || ""}`}
      placement="right"
      width={520}
      onClose={onClose}
      open={open}
    >
      <Spin spinning={detailLoading}>
        {orderDetail ? (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="訂單編號">{orderDetail.order_id}</Descriptions.Item>
              <Descriptions.Item label="下單時間">{formatDate(orderDetail.order_date)}</Descriptions.Item>
              <Descriptions.Item label="訂單狀態">{orderDetail.status}</Descriptions.Item>
              <Descriptions.Item label="總金額">{orderDetail.total}</Descriptions.Item>
            </Descriptions>
            <h4 style={{ marginTop: 24 }}>商品清單</h4>
            <Table
              dataSource={orderDetail.items || []}
              rowKey="product_id"
              pagination={false}
              size="small"
              columns={[
                { title: "商品名稱", dataIndex: "title" },
                { title: "單價", dataIndex: "price" },
                { title: "數量", dataIndex: "quantity" },
                { title: "小計", render: (_, r) => r.price * r.quantity },
              ]}
            />
            <div style={{ textAlign: "right", marginTop: 12, fontWeight: "bold" }}>
              總金額：NT$ {orderDetail.total}
            </div>
          </div>
        ) : (
          <div>無訂單資料</div>
        )}
      </Spin>
    </Drawer>
  );
}

function formatDateandhours(str) {
  if (!str) return "";
  const d = new Date(str);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hour = d.getHours();
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${y}-${m}-${day} ${hour}:${min}`;
}
function formatDate(str) {
  if (!str) return "";
  const d = new Date(str);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hour = d.getHours();
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export default OrderList;