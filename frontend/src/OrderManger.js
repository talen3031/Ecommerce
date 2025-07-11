import React, { useEffect, useState } from "react";
import { Table, Button, Spin, Descriptions, Drawer, Popconfirm, Select } from "antd";
import api from "./api";
import { message } from "antd";
import { useNavigate } from "react-router-dom";

const ORDER_STATUS_OPTIONS = [
  { value: "pending", label: "待處理" },
  { value: "paid", label: "已付款" },
  { value: "processing", label: "處理中" },
  { value: "shipped", label: "運送中" },
  { value: "delivered", label: "已到貨" },
  { value: "cancelled", label: "已取消" },
  { value: "refunded", label: "已退款" },
  { value: "returned", label: "已退貨" }
];

function AdminOrderList() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [orderDetail, setOrderDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [statusEditing, setStatusEditing] = useState({});
  const navigate = useNavigate(); // 未來可以用來導頁

  // 取得所有訂單
  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await api.get("/orders/all");
      setOrders(res.data.orders || []);
    } catch (err) {
      message.error("查詢訂單失敗");
    }
    setLoading(false);
  };

  // 取得訂單明細
  const fetchOrderDetail = async (orderId) => {
    setDetailLoading(true);
    try {
      const res = await api.get(`/orders/order/${orderId}`);
      setOrderDetail(res.data);
      setDrawerVisible(true);
    } catch (err) {
      message.error("查詢訂單明細失敗");
    }
    setDetailLoading(false);
  };

  // 更改訂單狀態
  const handleUpdateStatus = async (orderId) => {
    const newStatus = statusEditing[orderId];
    if (!newStatus) {
      message.warning("請選擇新狀態");
      return;
    }
    try {
      await api.patch(`/orders/${orderId}/status`, { status: newStatus });
      message.success("修改狀態成功！");
      fetchOrders();
    } catch (err) {
      message.error("狀態更新失敗：" + (err.response?.data?.error || err.message));
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const columns = [
    { title: "訂單編號", dataIndex: "id" },
    { title: "用戶ID", dataIndex: "user_id" },
    { title: "用戶名稱", dataIndex: "username" },
    {
      title: "訂單時間",
      dataIndex: "order_date",
      render: (value) => formatDateandhours(value),
    },
    { title: "狀態", dataIndex: "status" },
    { title: "總金額", dataIndex: "total" },
    {
      title: "更改狀態",
      render: (_, record) => (
        <span>
          <Select
            style={{ width: 110, marginRight: 8 }}
            value={statusEditing[record.id] || record.status}
            onChange={val =>
              setStatusEditing(editing => ({ ...editing, [record.id]: val }))
            }
            options={ORDER_STATUS_OPTIONS}
            disabled={record.status === "已取消"}
          />
          <Button
            type="primary"
            size="small"
            onClick={() => handleUpdateStatus(record.id)}
            disabled={record.status === "已取消"}
          >
            更新
          </Button>
        </span>
      ),
    },
    {
      title: "操作",
      render: (_, record) => (
        <Button
          style={{ marginRight: 8 }}
          onClick={() => fetchOrderDetail(record.id)}
        >
          查看明細
        </Button>
        // 若未來有詳細頁可改用：
        // onClick={() => navigate(`/admin/orders/${record.id}`)}
      ),
    },
  ];

  return (
    <div style={{ maxWidth: 1100, margin: "40px auto" }}>
      <h2>後台訂單管理</h2>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={orders}
          rowKey="id"
          pagination={false}
        />
      </Spin>
      <Drawer
        title={`訂單明細 ${orderDetail?.id || ""}`}
        placement="right"
        width={520}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        <Spin spinning={detailLoading}>
          {orderDetail ? (
            <div>
              <Descriptions column={1} bordered>
                <Descriptions.Item label="訂單編號">{orderDetail.order_id}</Descriptions.Item>
                <Descriptions.Item label="用戶ID">{orderDetail.user_id}</Descriptions.Item>
                <Descriptions.Item label="用戶名稱">{orderDetail.username}</Descriptions.Item>
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
    </div>
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
  return `${y}-${m}-${day}`;
}

export default AdminOrderList;
