import React, { useEffect, useState } from "react";
import { Card, Spin, message, Button, InputNumber, Row, Modal } from "antd";
import api from "./api";
import { useNavigate, useParams } from "react-router-dom";

const categoryMap = {
  1: "3C產品",
  2: "飾品",
  3: "男生衣服",
  4: "女生衣服"
};

function ProductDetail() {
  const { id } = useParams();
  const productId = id;
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cartLoading, setCartLoading] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [currentImage, setCurrentImage] = useState(0);

  // Modal 狀態
  const [modalOpen, setModalOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    api.get(`/products/${productId}`)
      .then(res => {
        setProduct(res.data);
        setCurrentImage(0);
      })
      .catch(() => message.error("查詢商品失敗"))
      .finally(() => setLoading(false));
  }, [productId]);

  const handleAddToCart = async () => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      message.error("請先登入");
      return;
    }
    setCartLoading(true);
    try {
      await api.post(`/carts/${userId}`, {
        product_id: productId,
        quantity: quantity
      });
      message.success("已加入購物車！");
    } catch (err) {
      message.error("加入購物車失敗：" + (err.response?.data?.error || err.message));
    }
    setCartLoading(false);
  };

  if (!productId) return null;

  return (
    <div style={{
      maxWidth: 440, margin: "44px auto", background: "#fff",
      borderRadius: 16, border: "1.5px solid #e2e2e2",
      boxShadow: "0 2px 32px #0000", padding: "36px 20px 24px 20px", position: "relative",
      fontFamily: "'Inter', 'Roboto', 'sans-serif'"
    }}>
      <Spin spinning={loading}>
        {product && (
          <div>
            <div style={{
              display: "flex", flexDirection: "column", alignItems: "center"
            }}>
              {/* 主圖（可點擊放大） */}
              <div style={{
                width: "100%", display: "flex", justifyContent: "center",
                alignItems: "center", background: "#f4f4f4", borderRadius: 12,
                minHeight: 260, marginBottom: 18, border: "1px solid #ececec"
              }}>
                <img
                  src={product.images?.[currentImage]}
                  alt="商品圖"
                  style={{
                    maxWidth: 340, maxHeight: 260, borderRadius: 12,
                    cursor: "zoom-in", opacity: 0.97, transition: "opacity 0.12s"
                  }}
                  title="點擊放大"
                  onClick={() => setModalOpen(true)}
                />
              </div>
              {/* 縮圖列 */}
              {product.images && product.images.length > 1 && (
                <div style={{
                  display: "flex", gap: 10, marginBottom: 14, justifyContent: "center"
                }}>
                  {product.images.map((img, idx) => (
                    <img
                      key={img + idx}
                      src={img}
                      alt={"縮圖" + (idx + 1)}
                      style={{
                        width: 48, height: 48, objectFit: "cover", borderRadius: 6,
                        border: idx === currentImage ? "2.5px solid #222" : "1.5px solid #ccc",
                        cursor: "pointer", filter: idx === currentImage ? "" : "grayscale(0.7)",
                        opacity: idx === currentImage ? 1 : 0.66, transition: "all .14s"
                      }}
                      onClick={() => setCurrentImage(idx)}
                    />
                  ))}
                </div>
              )}

              {/* 商品名稱 */}
              <div style={{
                fontWeight: 700, fontSize: 27, color: "#222",
                letterSpacing: 0.2, margin: "8px 0 10px 0"
              }}>
                {product.title}
              </div>
              {/* 價格 */}
              <div style={{ marginBottom: 13 }}>
                {product.on_sale ? (
                  <>
                    <span style={{ color: "#111", fontWeight: "bold", fontSize: 23 }}>NT${product.sale_price}</span>
                    <span style={{ color: "#b2b2b2", marginLeft: 12, textDecoration: "line-through", fontSize: 16 }}>NT${product.price}</span>
                  </>
                ) : (
                  <span style={{ fontWeight: 600, fontSize: 21, color: "#1a1a1a" }}>NT${product.price}</span>
                )}
              </div>
              <div style={{ color: "#909090", fontSize: 15, marginBottom: 13 }}>
                {categoryMap[product.category_id] || product.category_id}
              </div>
              {/* 描述 */}
              <div style={{
                background: "#f7f7f7",
                borderRadius: 9,
                padding: "14px 13px",
                margin: "13px 0 19px 0",
                color: "#444", fontSize: 15.5, lineHeight: 1.95, boxShadow: "0 0px 0px #f0f1f3",
                maxHeight: 120, overflowY: "auto", whiteSpace: "pre-line", width: "100%"
              }}>
                {product.description}
              </div>
              {/* 數量與加入購物車 */}
              <div style={{ marginBottom: 12 }}>
                <Row justify="center" align="middle">
                  <InputNumber
                    min={1}
                    max={99}
                    value={quantity}
                    onChange={val => setQuantity(val)}
                    style={{ width: 80, marginRight: 13 }}
                  />
                  <Button
                    type="primary"
                    size="large"
                    loading={cartLoading}
                    onClick={handleAddToCart}
                    style={{
                      minWidth: 130, background: "#222", borderRadius: 8,
                      border: "none", fontWeight: 500, fontSize: 16, boxShadow: "0 1px 5px #2221"
                    }}
                  >
                    加入購物車
                  </Button>
                </Row>
              </div>
            </div>

            {/* 單純大圖 Modal（只有一張圖） */}
            <Modal
              open={modalOpen}
              onCancel={() => setModalOpen(false)}
              footer={null}
              bodyStyle={{
                display: "flex", alignItems: "center", justifyContent: "center", background: "#fff"
              }}
              centered
            >
              <img
                src={product.images?.[currentImage]}
                alt="大圖預覽"
                style={{
                  maxHeight: 500, maxWidth: "95vw", width: "auto", borderRadius: 10
                }}
              />
            </Modal>
          </div>
        )}
      </Spin>
    </div>
  );
}

export default ProductDetail;
