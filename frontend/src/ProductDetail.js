import React, { useEffect, useState } from "react";
import { Card, Spin, message, Button, Image, Tag } from "antd";
import api from "./api";

// 假設有 categoryMap 對照
const categoryMap = {
  1: "3C產品",
  2: "飾品",
  3: "男生衣服",
  4: "女生衣服"

};

function ProductDetail({ productId, onBack }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    api.get(`/products/${productId}`)
      .then(res => setProduct(res.data))
      .catch(() => message.error("查詢商品失敗"))
      .finally(() => setLoading(false));
  }, [productId]);

  if (!productId) return null;

  return (
    <div style={{ maxWidth: 600, margin: "40px auto" }}>
      <Spin spinning={loading}>
        {product && (
          <Card
            title={
              <span>
                {product.title}
                {product.on_sale && <Tag color="red" style={{ marginLeft: 15 }}>On Sale</Tag>}
              </span>
            }
            extra={<Button onClick={onBack}>返回</Button>}
            bordered={false}
          >
            {/* 多圖顯示 */}
            {product.images && product.images.length > 0 && (
              <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
                {product.images.map((url, idx) => (
                  <Image
                    key={idx}
                    src={url}
                    width={120}
                    height={120}
                    style={{ objectFit: "cover", borderRadius: 8 }}
                    alt={`商品圖${idx + 1}`}
                  />
                ))}
              </div>
            )}
            {/* 價格區塊 */}
            <div style={{ marginBottom: 8 }}>
              {product.on_sale ? (
                <>
                  <span style={{ color: "#fa541c", fontWeight: "bold", fontSize: 20 }}>
                    NT${product.sale_price}
                  </span>
                  <span style={{ color: "#888", marginLeft: 8, textDecoration: "line-through" }}>
                    NT${product.price}
                  </span>
        
                  {product.sale_start && product.sale_end && (
                    <div style={{ color: "#888", fontSize: 12, marginTop: 2 }}>
                      特價期間：{product.sale_start.slice(0,16).replace("T"," ")} ~ {product.sale_end.slice(0,16).replace("T"," ")}
                    </div>
                  )}
                </>
              ) : (
                <span style={{ fontWeight: "bold", fontSize: 20 }}>NT${product.price}</span>
              )}
            </div>
            <div>分類：{categoryMap[product.category_id] || product.category_id}</div>
            <div style={{ marginTop: 12, color: "#444" }}>{product.description}</div>
            {/* 你可以再加更多欄位（如庫存、規格、品牌等） */}
          </Card>
        )}
      </Spin>
    </div>
  );
}

export default ProductDetail;
