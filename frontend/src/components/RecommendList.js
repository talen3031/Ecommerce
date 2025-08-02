import React, { useEffect, useState } from "react";
import { Card, Row, Col, Spin } from "antd";
import api from "../api/api";
import { useNavigate } from "react-router-dom";

const categoryOptions = [
  { label: "全部", value: "" },
  { label: "褲子", value: 1 },
  { label: "帽子", value: 2 },
  { label: "上衣", value: 3 },
  { label: "外套", value: 4 },
];
const categoryMap = Object.fromEntries(categoryOptions.map(opt => [opt.value, opt.label]));

function RecommendList({ userId, mode = "cart", limit = 5, onSelectProduct }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
    } else if (mode === "guest") {
      url = `/products/guest/recommend?limit=${limit}`;
    }

    api.get(url)
      .then(res => setProducts(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId, mode, limit]);

  if (!userId) return null;

  const handleClick = (id) => {
    if (onSelectProduct) onSelectProduct(id);
    else navigate(`/products/${id}`);
  };

  return (
    <div style={{
      background: 'white',
      padding: '40px 30px',
      borderRadius: '16px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
      marginTop: '40px'
    }}>
      <Spin spinning={loading}>
        <Row gutter={[24, 32]}>
          {products.map(product => (
            <Col xs={24} sm={12} md={8} lg={6} key={product.id}>
              <Card
                hoverable
                onClick={() => handleClick(product.id)}
                style={{
                  borderRadius: '16px',
                  overflow: 'hidden',
                  border: '1px solid #f0f0f0',
                  boxShadow: '0 2px 12px rgba(0, 0, 0, 0.04)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 12px rgba(0, 0, 0, 0.04)';
                }}
                cover={
                  <div style={{
                    position: 'relative',
                    overflow: 'hidden',
                    paddingTop: '75%'
                  }}>
                    <img
                      src={product.images?.[0]}
                      alt={product.title}
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        transition: 'transform 0.3s ease'
                      }}
                      onMouseEnter={e => { e.target.style.transform = 'scale(1.05)' }}
                      onMouseLeave={e => { e.target.style.transform = 'scale(1)' }}
                    />
                    {product.on_sale && (
                      <div style={{
                        position: 'absolute',
                        top: '12px',
                        right: '12px',
                        background: 'linear-gradient(135deg, #ef0202ff, #ee5a52)',
                        color: "#f8f2f2ff",
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 600,
                        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
                      }}>
                        特價
                      </div>
                    )}
                  </div>
                }
                bodyStyle={{
                  padding: '20px',
                  background: 'white'
                }}
              >
                <div style={{
                  fontWeight: 600,
                  fontSize: '16px',
                  marginBottom: '8px',
                  color: '#2d3748',
                  lineHeight: '1.4',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {product.title}
                </div>
                <div style={{
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  {product.on_sale ? (
                    <>
                      <span style={{
                        color: '#e53e3e',
                        fontWeight: 700,
                        fontSize: '18px'
                      }}>
                        NT${product.sale_price}
                      </span>
                      <span style={{
                        textDecoration: 'line-through',
                        color: '#a0aec0',
                        fontSize: '14px'
                      }}>
                        NT${product.price}
                      </span>
                    </>
                  ) : (
                    <span style={{
                      fontWeight: 600,
                      fontSize: '18px',
                      color: '#2d3748'
                    }}>
                      NT${product.price}
                    </span>
                  )}
                </div>
              </Card>
            </Col>
          ))}
          {products.length === 0 && !loading && (
            <Col span={24}>
              <div style={{
                textAlign: 'center',
                padding: '60px 20px',
                color: '#a0aec0',
                fontSize: '18px'
              }}>
                <div style={{
                  fontSize: '48px',
                  marginBottom: '16px',
                  opacity: 0.5
                }}>
                  🔍
                </div>
                暫無推薦商品
              </div>
            </Col>
          )}
        </Row>
      </Spin>
    </div>
  );
}

export default RecommendList;
