import React, { useEffect, useState } from "react";
import { Card, Spin, message, Row, Col } from "antd";
import api from "./api";

function RecommendList({ userId, mode = "cart", limit = 5 ,onSelectProduct}) {
  // mode: "cart"（購物車推薦），"collaborative"（協同過濾），"user"（購買紀錄）
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    let url;
    if (mode === "cart") {
      url = `/carts/${userId}/recommend?limit=${limit}`;
    } else if (mode === "collaborative") {
      url = `/carts/${userId}/recommend/collaborative?limit=${limit}`;
    } else if (mode === "user") {
      url = `/users/${userId}/recommend?limit=${limit}`;
    }
    api.get(url)
      .then(res => setProducts(res.data || []))
      .catch(() => message.error("推薦商品取得失敗"))
      .finally(() => setLoading(false));
  }, [userId, mode, limit]);

  if (!userId) return null;

  return (
    <div style={{ marginTop: 32 }}>
      <h3>你可能喜歡...</h3>
      <Spin spinning={loading}>
        <Row gutter={16}>
          {(products || []).map(product => (
            <Col key={product.id} span={8} style={{ marginBottom: 16 }}>
              <Card
                hoverable
                onClick={() => onSelectProduct && onSelectProduct(product.id)}
                cover={
                  <img
                    src={product.images[0]}
                    alt={product.title}
                    style={{ height: 120, objectFit: "cover", cursor: "pointer" }}
                  />
                }
                style={{ cursor: "pointer" }}
              >
                <Card.Meta
                  title={product.title}
                  description={
                    <div>
                      <div>價格：NT${product.price}</div>
                      <div style={{ fontSize: 12, color: "#999" }}>{product.description}</div>
                    </div>
                  }
                />
              </Card>
            </Col>
          ))}
          {(products.length === 0 && !loading) && (
            <div style={{ color: "#aaa", margin: 16 }}>暫無推薦商品</div>
          )}
        </Row>
      </Spin>
    </div>
  );
}
export default RecommendList;
