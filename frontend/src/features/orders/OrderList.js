import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Table, Button, Spin, Descriptions, Drawer, message, Modal } from "antd";
import '../../styles/OrderList.css'

import api from "../../api/api";
import OrderDetailDrawer from "./OrderDetailDrawer";

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
const STATUS_LABEL_MAP = Object.fromEntries(ORDER_STATUS_OPTIONS.map(opt => [opt.value, opt.label]));

function OrderList() {
  const userId = localStorage.getItem("user_id");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [orderDetail, setOrderDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // 加總原始金額
  const calcOriginalTotal = (items) => {
    if (!items) return 0;
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };
  const showCancelConfirm = (orderId) => {
  Modal.confirm({
    title: "取消訂單",
    content: "確定要取消這筆訂單嗎？",
    okText: "確定取消",
    cancelText: "返回",
    okType: "danger",
    onOk: () => handleCancelOrder(orderId)
  });
};

  const handleCancelOrder = async(orderId) => {
    try {
      await api.post(`/orders/${orderId}/cancel`);
      message.success("訂單已取消");
      setDrawerOpen(false); // 關閉詳情
      fetchOrders();        // 重新載入訂單
    } catch (err) {
      message.error("取消失敗：" + (err.response?.data?.error || err.message));
    }
  };
  // 取得所有訂單
  const fetchOrders = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const res = await api.get(`/orders`);
      setOrders(res.data.orders || []);
    } catch (err) {
      // 可自訂錯誤處理
    }
    setLoading(false);
  };

  // 取得訂單詳情
  const fetchOrderDetail = async (orderId) => {
    setDetailLoading(true);
    try {
      const res = await api.get(`/orders/${orderId}`);
      setOrderDetail(res.data);
      setDrawerOpen(true);
    } catch (err) {
      // 可自訂錯誤處理
    }
    setDetailLoading(false);
  };

  useEffect(() => {
    fetchOrders();
    // eslint-disable-next-line
  }, []);

  // Drawer 展開的 orderId（取自路徑或狀態）
  const match = location.pathname.match(/^\/orders\/(\d+)/);
  const drawerOrderId = match ? match[1] : null;

  useEffect(() => {
    if (drawerOrderId) {
      fetchOrderDetail(drawerOrderId);
    }
  }, [drawerOrderId]);

  const columns = [


    { title: "訂單編號", dataIndex: "id" },
    {
      title: "訂單時間",
      dataIndex: "order_date",
      render: (value) => formatDateandhours(value),
    },
    {
      title: "狀態",
      dataIndex: "status",
      render: value => STATUS_LABEL_MAP[value] || value
    },
    { title: "總金額", dataIndex: "total" },
    {
      title: "操作",
      render: (_, record) => (
        <Button onClick={() => {
          setDrawerOpen(true);
          fetchOrderDetail(record.id);
          navigate(`/orders/${record.id}`);
        }}>
          查看明細
        </Button>
      ),
    },
  ];

  // 依需求：有折扣才顯示三行，沒折扣只顯示總金額
  function renderAmountInfo() {
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

  return (
   
    <div className="orderlist-container">
      <h2>我的訂單</h2>
      <div className="order-table-scroll">
      <Spin spinning={loading}>
        <div className="order-table-scroll">
          <Table
            columns={columns}
            dataSource={orders}
            rowKey="id"
            pagination={false}
          />
        </div>
      </Spin>
      </div>
      {/* Drawer 詳情 */}
      <OrderDetailDrawer
        open={drawerOpen}
        onClose={() => {
          setDrawerOpen(false);
          navigate("/orders");
        }}
        orderDetail={orderDetail}
        detailLoading={detailLoading}
        onCancelOrder={handleCancelOrder}
        showCancelConfirm={showCancelConfirm}
        calcOriginalTotal={calcOriginalTotal}
      />
      
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

export default OrderList;
