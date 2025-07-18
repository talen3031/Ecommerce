import React, { useState } from "react";
import { Drawer, Spin, Descriptions, Table, Button, Modal } from "antd";

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

// 工具函式可獨立一份 utils/date.js
function formatDate(str) {
  if (!str) return "";
  const d = new Date(str);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

// 金額區塊也可再獨立成元件
function OrderAmountInfo({ orderDetail, calcOriginalTotal }) {
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

function OrderDetailDrawer({
  open,
  onClose,
  orderDetail,
  detailLoading,
  onCancelOrder,
  showCancelConfirm,
  calcOriginalTotal
}) {
  // 預覽圖放大 Modal state
  const [previewImage, setPreviewImage] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  return (
    <Drawer
      title={`訂單明細`}
      placement="right"
      width={600}
      onClose={onClose}
      open={open}
    >
      <Spin spinning={detailLoading}>
        {orderDetail ? (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="訂單編號">{orderDetail.order_id}</Descriptions.Item>
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
            {orderDetail && orderDetail.shipping_info && (
              <div style={{ margin: "24px 0 0 0" }}>
                <h4>寄送資訊</h4>
                <Descriptions column={1} bordered size="small" style={{ maxWidth: 390 }}>
                  <Descriptions.Item label="寄送方式">{orderDetail.shipping_info.shipping_method}</Descriptions.Item>
                  <Descriptions.Item label="收件人">{orderDetail.shipping_info.recipient_name}</Descriptions.Item>
                  <Descriptions.Item label="收件人電話">{orderDetail.shipping_info.recipient_phone}</Descriptions.Item>
                  <Descriptions.Item label="門市/地址">{orderDetail.shipping_info.store_name}</Descriptions.Item>
                </Descriptions>
              </div>
            )}
            {/* 金額總結資訊依折扣條件顯示 */}
            <OrderAmountInfo orderDetail={orderDetail} calcOriginalTotal={calcOriginalTotal} />
            {/* 只有特定狀態才可取消 */}
            {orderDetail && !["cancelled", "delivered", "refunded", "returned"].includes(orderDetail.status) && (
              <div style={{ textAlign: "right", marginTop: 24 }}>
                <Button
                  danger
                  type="primary"
                  onClick={() => showCancelConfirm(orderDetail.order_id)}
                >
                  取消訂單
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div>無訂單資料</div>
        )}
      </Spin>
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
    </Drawer>
  );
}

export default OrderDetailDrawer;
