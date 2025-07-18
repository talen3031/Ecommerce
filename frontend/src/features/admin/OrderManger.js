import React, { useEffect, useState } from "react";
import { Table, Button, Spin, Descriptions, Drawer, Select, Modal, Form, Input, message } from "antd";
import api from "../../api/api";
import { useNavigate } from "react-router-dom";
import '../../styles/AdminPage.css'

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
  const [previewImage, setPreviewImage] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [orderDetail, setOrderDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [statusEditing, setStatusEditing] = useState({});
  const [shippingModalOpen, setShippingModalOpen] = useState(false);
  const [shippingForm] = Form.useForm();
  const navigate = useNavigate();
  const STATUS_LABEL_MAP = Object.fromEntries(ORDER_STATUS_OPTIONS.map(opt => [opt.value, opt.label]));

  // 計算原始金額
  const calcOriginalTotal = (items) => {
    if (!items) return 0;
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  useEffect(() => {
    fetchOrders();
  }, []);

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
      const res = await api.get(`/orders/${orderId}`);
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

  // 更改運送資訊
  const handleUpdateShipping = async () => {
    try {
      const values = await shippingForm.validateFields();
      await api.patch(`/orders/${orderDetail.order_id}/shipping`, values);
      message.success("運送資訊更新成功");
      setShippingModalOpen(false);
      fetchOrderDetail(orderDetail.order_id); // 重新載入明細
    } catch (err) {
      message.error("更新失敗：" + (err.response?.data?.error || err.message));
    }
  };

  const columns = [

    { title: "訂單編號", dataIndex: "id" },
    { title: "用戶ID", dataIndex: "user_id" },
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
      ),
    },
  ];

  // 金額資訊條件顯示
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
    <div className="admin-container">
      <h2>後台訂單管理</h2>
      <Spin spinning={loading}>
        <div className="admin-table-scroll">
          <Table
            columns={columns}
            dataSource={orders}
            rowKey="id"
            pagination={false}
          />
        </div>
      </Spin>
      <Drawer
        title={`訂單明細`}
        placement="right"
        width={600}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        <Spin spinning={detailLoading}>
          {orderDetail ? (
            <div>
              <Descriptions column={1} bordered>
                <Descriptions.Item label="訂單編號">{orderDetail.order_id}</Descriptions.Item>
                <Descriptions.Item label="用戶ID">{orderDetail.user_id}</Descriptions.Item>
                <Descriptions.Item label="下單時間">{formatDate(orderDetail.order_date)}</Descriptions.Item>
                <Descriptions.Item label="訂單狀態">
                  <span style={{
                    color: orderDetail.status === "cancelled" ? "#f5222d" : "#222",
                    fontWeight: orderDetail.status === "cancelled" ? 600 : 400
                  }}>
                    {STATUS_LABEL_MAP[orderDetail.status] || orderDetail.status}
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label="訂單金額">NT$ {orderDetail.total}</Descriptions.Item>
         
              </Descriptions>
              
              <h4 style={{ marginTop: 24 }}>商品清單</h4>
              <Table
                dataSource={orderDetail.items || []}
                rowKey="product_id"
                pagination={false}
                size="small"
                columns={[
                {
                  title: "圖片",
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
                {orderDetail && orderDetail.shipping_info && (
                  <div style={{ margin: "24px 0 0 0" }}>
                    <h4>寄送資訊</h4>
                    <Descriptions column={1} bordered size="small" style={{ maxWidth: 390 }}>
                      <Descriptions.Item label="寄送方式">{orderDetail.shipping_info.shipping_method}</Descriptions.Item>
                      <Descriptions.Item label="收件人">{orderDetail.shipping_info.recipient_name}</Descriptions.Item>
                      <Descriptions.Item label="收件人電話">{orderDetail.shipping_info.recipient_phone}</Descriptions.Item>
                      <Descriptions.Item label="門市/地址">{orderDetail.shipping_info.store_name}</Descriptions.Item>
                      {/* 只有未取消才能更改 */}
                      {orderDetail.status !== "cancelled" && (
                        <Descriptions.Item label="運送資訊">
                          <Button danger onClick={() => {
                            shippingForm.setFieldsValue(orderDetail.shipping_info || {});
                            setShippingModalOpen(true);
                          }}>
                            更改
                          </Button>
                        </Descriptions.Item>
                      )}
                    </Descriptions>
                    <Modal
                      title="運送資訊"
                      open={shippingModalOpen}
                      onCancel={() => setShippingModalOpen(false)}
                      onOk={handleUpdateShipping}
                      okText="儲存"
                      cancelText="取消"
                    >
                      <Form form={shippingForm} layout="vertical">
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
                          rules={[
                            { required: true, message: "請輸入收件人電話" }
                          ]}
                        >
                          <Input />
                        </Form.Item>
                      </Form>
                    </Modal>
                  </div>
                )}
              {/* 金額總結資訊依折扣條件顯示 */}
              {renderAmountInfo()}
              
            </div>
          ) : (
            <div>無訂單資料</div>
          )}
        </Spin>
      </Drawer>
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
