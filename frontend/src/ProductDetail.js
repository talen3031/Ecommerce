import React, { useEffect, useState } from "react";
import { Card, Spin, message, Button, Image, Tag, InputNumber, Row } from "antd";
import api from "./api";

const categoryMap = {
  1: "3C產品",
  2: "飾品",
  3: "男生衣服",
  4: "女生衣服"
};

function ProductDetail({ productId, onBack }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cartLoading, setCartLoading] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [currentImage, setCurrentImage] = useState(0);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    api.get(`/products/${productId}`)
      .then(res => {
        setProduct(res.data);
        setCurrentImage(0); // 每次進入詳細頁都回到第一張
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

  const handlePrevImage = () => {
    setCurrentImage((prev) => prev > 0 ? prev - 1 : (product.images.length - 1));
  };

  const handleNextImage = () => {
    setCurrentImage((prev) => prev < product.images.length - 1 ? prev + 1 : 0);
  };

  if (!productId) return null;

  return (
    <div style={{ maxWidth: 540, margin: "40px auto" }}>
      <Spin spinning={loading}>
        {product && (
          <Card
            bordered={false}
            bodyStyle={{ padding: 32, paddingBottom: 24 }}
            style={{ borderRadius: 16, boxShadow: "0 2px 16px #eee" }}
            extra={<Button onClick={onBack}>返回</Button>}
          >
            {/* 單張圖片加切換按鈕 */}
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 12, marginBottom: 32 }}>
              {product.images && product.images.length > 0 ? (
                <>
                  <Button
                    onClick={handlePrevImage}
                    disabled={product.images.length <= 1}
                  >
                    ←
                  </Button>
                  <Image
                    src={product.images[currentImage]}
                    width={300}
                    height={300}
                    style={{ objectFit: "cover", borderRadius: 12 }}
                    alt={`商品圖${currentImage + 1}`}
                  />
                  <Button
                    onClick={handleNextImage}
                    disabled={product.images.length <= 1}
                  >
                    →
                  </Button>
                </>
              ) : (
                <div style={{ width: 300, height: 300, background: "#f5f5f5", borderRadius: 12, lineHeight: "300px", textAlign: "center", color: "#bbb" }}>無圖</div>
              )}
            </div>
            {/* 圖片下方顯示當前張數 */}
            {product.images && product.images.length > 1 && (
              <div style={{ textAlign: "center", color: "#888", marginBottom: 8, fontSize: 15 }}>
                {currentImage + 1} / {product.images.length}
              </div>
            )}

            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 700, fontSize: 26, marginBottom: 8 }}>
                {product.title}
                {product.on_sale && <Tag color="red" style={{ marginLeft: 12 }}>特價</Tag>}
              </div>

              <div style={{ marginBottom: 12 }}>
                {product.on_sale ? (
                  <>
                    <span style={{ color: "#fa541c", fontWeight: "bold", fontSize: 22 }}>NT${product.sale_price}</span>
                    <span style={{ color: "#888", marginLeft: 10, textDecoration: "line-through", fontSize: 16 }}>NT${product.price}</span>
                  </>
                ) : (
                  <span style={{ fontWeight: "bold", fontSize: 22 }}>NT${product.price}</span>
                )}
              </div>

              <div style={{ color: "#999", fontSize: 16, marginBottom: 8 }}>
                分類：{categoryMap[product.category_id] || product.category_id}
              </div>

              {/* 美化商品描述 */}
              <div
                style={{
                  background: "#fafbfc",
                  borderRadius: 10,
                  padding: "18px 20px",
                  margin: "16px 0 24px 0",
                  color: "#444",
                  fontSize: 17,
                  lineHeight: 2,
                  boxShadow: "0 1px 6px #f0f1f3",
                  textAlign: "left",
                  maxHeight: 180,
                  overflowY: "auto",
                  whiteSpace: "pre-line",
                  letterSpacing: 0.5
                }}
              >
                <div style={{fontWeight: 600, fontSize: 18, marginBottom: 4, color: "#2070ca", letterSpacing:1}}>
                  <span role="img" aria-label="desc" style={{marginRight:6}}>📦</span>
                  Description...
                </div>
                <div style={{textIndent: "1em"}}>
                  {product.description}
                </div>
              </div>


              <div style={{ marginBottom: 20 }}>
                <Row justify="center" align="middle">
                  <InputNumber
                    min={1}
                    max={99}
                    value={quantity}
                    onChange={val => setQuantity(val)}
                    style={{ width: 100, marginRight: 20 }}
                  />
                  <Button
                    type="primary"
                    size="large"
                    loading={cartLoading}
                    onClick={handleAddToCart}
                    style={{ minWidth: 140 }}
                  >
                    加入購物車
                  </Button>
                </Row>
              </div>
            </div>
          </Card>
        )}
      </Spin>
    </div>
  );
}

export default ProductDetail;
