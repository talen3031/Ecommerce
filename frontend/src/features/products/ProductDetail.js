import React, { useEffect, useState } from "react";
import { Card, Spin, message, Button, InputNumber, Row, Modal,Col } from "antd";
import api from "../../api/api";
import { useNavigate, useParams } from "react-router-dom";
import '../../styles/ProductDetail.css'
const categoryMap = {
  1: "褲子",
  2: "帽子",
  3: "上衣",
  4: "外套"
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
      background: 'linear-gradient(to bottom, #080808ff, #1d1b1bff)',
      minHeight: '100vh',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <Spin spinning={loading}>
          {product && (
            <Row gutter={[48, 48]} align="middle">
              {/* 左側圖片區域 */}
              <Col xs={24} md={12}>
                <div style={{
                  background: 'white',
                  borderRadius: '20px',
                  padding: '30px',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  {/* 主圖 */}
                  <div style={{
                    position: 'relative',
                    marginBottom: '20px',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                    aspectRatio: '1/1'
                  }}>
                    <img
                      src={product.images?.[currentImage]}
                      alt="商品圖"
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        cursor: 'zoom-in',
                        transition: 'transform 0.3s ease'
                      }}
                      title="點擊放大"
                      onClick={() => setModalOpen(true)}
                      onMouseEnter={(e) => {
                        e.target.style.transform = 'scale(1.05)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.transform = 'scale(1)';
                      }}
                    />
                    {product.on_sale && (
                      <div style={{
                        position: 'absolute',
                        top: '20px',
                        right: '20px',
                        background: 'linear-gradient(135deg, #ef0202ff, #ee5a52)',
                        color: 'white',
                        padding: '8px 16px',
                        borderRadius: '20px',
                        fontSize: '14px',
                        fontWeight: 600,
                        boxShadow: '0 4px 12px rgba(255, 107, 107, 0.3)'
                      }}>
                        特價中
                      </div>
                    )}
                  </div>
                  
                  {/* 縮圖列 */}
                  {product.images && product.images.length > 1 && (
                    <div style={{
                      display: 'flex',
                      gap: '12px',
                      justifyContent: 'center',
                      flexWrap: 'wrap'
                    }}>
                      {product.images.map((img, idx) => (
                        <img
                          key={img + idx}
                          src={img}
                          alt={`縮圖${idx + 1}`}
                          style={{
                            width: '60px',
                            height: '60px',
                            objectFit: 'cover',
                            borderRadius: '8px',
                            border: idx === currentImage ? '3px solid #667eea' : '2px solid #e2e8f0',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            opacity: idx === currentImage ? 1 : 0.7
                          }}
                          onClick={() => setCurrentImage(idx)}
                          onMouseEnter={(e) => {
                            e.target.style.opacity = '1';
                            e.target.style.transform = 'scale(1.1)';
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.opacity = idx === currentImage ? '1' : '0.7';
                            e.target.style.transform = 'scale(1)';
                          }}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </Col>

              {/* 右側商品資訊 */}
              <Col xs={24} md={12}>
                <div style={{
                  background: 'white',
                  borderRadius: '20px',
                  padding: '40px',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  height: '100%'
                }}>
                  {/* 分類標籤 */}
                  <div style={{
                    display: 'inline-block',
                    background: 'linear-gradient(135deg, #050505ff 0%, #646462ff 100%)',
                    color: '#fdfdfdff',
                    padding: '6px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    fontWeight: 500,
                    marginBottom: '20px'
                  }}>
                    {categoryMap[product.category_id] || product.category_id}
                  </div>

                  {/* 商品名稱 */}
                  <h1 style={{
                    fontSize: 'clamp(1.8rem, 4vw, 2.5rem)',
                    fontWeight: 700,
                    color: '#2d3748',
                    margin: '0 0 16px 0',
                    lineHeight: '1.2',
                    letterSpacing: '-0.02em'
                  }}>
                    {product.title}
                  </h1>

                  {/* 價格 */}
                  <div style={{
                    marginBottom: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px'
                  }}>
                    {product.on_sale ? (
                      <>
                        <span style={{
                          color: '#e53e3e',
                          fontWeight: 700,
                          fontSize: '2rem'
                        }}>
                          NT${product.sale_price}
                        </span>
                        <span style={{
                          color: '#a0aec0',
                          textDecoration: 'line-through',
                          fontSize: '1.2rem'
                        }}>
                          NT${product.price}
                        </span>
                      </>
                    ) : (
                      <span style={{
                        fontWeight: 700,
                        fontSize: '2rem',
                        color: '#2d3748'
                      }}>
                        NT${product.price}
                      </span>
                    )}
                  </div>

                  {/* 商品描述 */}
                  <div style={{
                    background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                    borderRadius: '12px',
                    padding: '20px',
                    margin: '24px 0',
                    border: '1px solid #e2e8f0'
                  }}>
                    <h3 style={{
                      fontSize: '16px',
                      fontWeight: 600,
                      color: '#4a5568',
                      margin: '0 0 12px 0'
                    }}>
                      商品描述
                    </h3>
                    <div style={{
                      color: '#718096',
                      fontSize: '15px',
                      lineHeight: '1.6',
                      whiteSpace: 'pre-line',
                      maxHeight: '120px',
                      overflowY: 'auto'
                    }}>
                      {product.description}
                    </div>
                  </div>

                  {/* 購買區域 */}
                  <div style={{
                    background: 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)',
                    borderRadius: '16px',
                    padding: '24px',
                    border: '1px solid #e2e8f0',
                    marginTop: '30px'
                  }}>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: 600,
                      color: '#4a5568',
                      marginBottom: '16px'
                    }}>
                      選擇數量
                    </div>
                    <Row gutter={16} align="middle">
                      <Col>
                        <InputNumber
                          min={1}
                          max={99}
                          value={quantity}
                          onChange={val => setQuantity(val)}
                          style={{
                            width: '80px',
                            borderRadius: '8px',
                            border: '1px solid #e2e8f0',
                            height: '34px'
                          }}
                        />
                      </Col>
                      <Col flex={1}>
                        <Button
                          type="primary"
                          size="large"
                          loading={cartLoading}
                          onClick={handleAddToCart}
                          className="addtocart-btn"
                        >
                          {cartLoading ? '加入中...' : '加入購物車'}
                        </Button>
                      </Col>
                    </Row>
                  </div>
                </div>
              </Col>
            </Row>
          )}
        </Spin>

        {/* 大圖預覽 Modal */}
        <Modal
          open={modalOpen}
          onCancel={() => setModalOpen(false)}
          footer={null}
          centered
          width="90vw"
          style={{
            maxWidth: '800px'
          }}
          bodyStyle={{
            padding: '20px',
            background: 'white',
            borderRadius: '16px'
          }}
        >
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            borderRadius: '12px',
            padding: '20px'
          }}>
            <img
              src={product?.images?.[currentImage]}
              alt="大圖預覽"
              style={{
                maxHeight: '70vh',
                maxWidth: '100%',
                objectFit: 'contain',
                borderRadius: '8px'
              }}
            />
          </div>
        </Modal>
      </div>
    </div>
  );
}

export default ProductDetail;