import React, { useEffect, useState } from "react";
import { Card, Spin, message, Button, InputNumber, Row, Modal, Col } from "antd";
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
      padding: 'clamp(20px, 4vw, 40px) clamp(16px, 3vw, 20px)'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <Spin spinning={loading}>
          {product && (
            <Row gutter={[
              { xs: 24, sm: 32, md: 48 }, // 響應式間距
              { xs: 32, sm: 40, md: 48 }
            ]} align="middle">
              {/* 左側圖片區域 */}
              <Col xs={24} sm={24} md={12} lg={12}>
                <div style={{
                  background: 'white',
                  borderRadius: 'clamp(16px, 2vw, 20px)',
                  padding: 'clamp(20px, 3vw, 30px)',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  marginBottom: window.innerWidth <= 768 ? '20px' : '0'
                }}>
                  {/* 主圖 */}
                  <div style={{
                    position: 'relative',
                    marginBottom: 'clamp(16px, 2vw, 20px)',
                    borderRadius: 'clamp(12px, 1.5vw, 16px)',
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
                        if (window.innerWidth > 768) {
                          e.target.style.transform = 'scale(1.05)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.transform = 'scale(1)';
                      }}
                    />
                    {product.on_sale && (
                      <div style={{
                        position: 'absolute',
                        top: 'clamp(12px, 2vw, 20px)',
                        right: 'clamp(12px, 2vw, 20px)',
                        background: 'linear-gradient(135deg, #ef0202ff, #ee5a52)',
                        color: 'white',
                        padding: 'clamp(6px, 1vw, 8px) clamp(12px, 2vw, 16px)',
                        borderRadius: 'clamp(16px, 2vw, 20px)',
                        fontSize: 'clamp(12px, 1.2vw, 14px)',
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
                      gap: 'clamp(8px, 1.5vw, 12px)',
                      justifyContent: 'center',
                      flexWrap: 'wrap',
                      overflowX: 'auto',
                      paddingBottom: '8px'
                    }}>
                      {product.images.map((img, idx) => (
                        <img
                          key={img + idx}
                          src={img}
                          alt={`縮圖${idx + 1}`}
                          style={{
                            width: 'clamp(50px, 8vw, 60px)',
                            height: 'clamp(50px, 8vw, 60px)',
                            objectFit: 'cover',
                            borderRadius: 'clamp(6px, 1vw, 8px)',
                            border: idx === currentImage ? '3px solid #667eea' : '2px solid #e2e8f0',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            opacity: idx === currentImage ? 1 : 0.7,
                            flexShrink: 0
                          }}
                          onClick={() => setCurrentImage(idx)}
                          onMouseEnter={(e) => {
                            if (window.innerWidth > 768) {
                              e.target.style.opacity = '1';
                              e.target.style.transform = 'scale(1.1)';
                            }
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
              <Col xs={24} sm={24} md={12} lg={12}>
                <div style={{
                  background: 'white',
                  borderRadius: 'clamp(16px, 2vw, 20px)',
                  padding: 'clamp(24px, 4vw, 40px)',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  height: window.innerWidth <= 768 ? 'auto' : '100%'
                }}>
                  {/* 分類標籤 */}
                  <div style={{
                    display: 'inline-block',
                    background: 'linear-gradient(135deg, #050505ff 0%, #646462ff 100%)',
                    color: '#fdfdfdff',
                    padding: 'clamp(4px, 1vw, 6px) clamp(12px, 2vw, 16px)',
                    borderRadius: 'clamp(16px, 2vw, 20px)',
                    fontSize: 'clamp(12px, 1.2vw, 14px)',
                    fontWeight: 500,
                    marginBottom: 'clamp(16px, 2vw, 20px)'
                  }}>
                    {categoryMap[product.category_id] || product.category_id}
                  </div>

                  {/* 商品名稱 */}
                  <h1 style={{
                    fontSize: 'clamp(1.5rem, 5vw, 2.5rem)',
                    fontWeight: 700,
                    color: '#2d3748',
                    margin: '0 0 clamp(12px, 2vw, 16px) 0',
                    lineHeight: '1.2',
                    letterSpacing: '-0.02em',
                    wordBreak: 'break-word'
                  }}>
                    {product.title}
                  </h1>

                  {/* 價格 */}
                  <div style={{
                    marginBottom: 'clamp(20px, 3vw, 24px)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'clamp(12px, 2vw, 16px)',
                    flexWrap: 'wrap'
                  }}>
                    {product.on_sale ? (
                      <>
                        <span style={{
                          color: '#e53e3e',
                          fontWeight: 700,
                          fontSize: 'clamp(1.5rem, 4vw, 2rem)'
                        }}>
                          NT${product.sale_price}
                        </span>
                        <span style={{
                          color: '#a0aec0',
                          textDecoration: 'line-through',
                          fontSize: 'clamp(1rem, 2.5vw, 1.2rem)'
                        }}>
                          NT${product.price}
                        </span>
                      </>
                    ) : (
                      <span style={{
                        fontWeight: 700,
                        fontSize: 'clamp(1.5rem, 4vw, 2rem)',
                        color: '#2d3748'
                      }}>
                        NT${product.price}
                      </span>
                    )}
                  </div>

                  {/* 商品描述 */}
                  <div style={{
                    background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                    borderRadius: 'clamp(10px, 1.5vw, 12px)',
                    padding: 'clamp(16px, 2.5vw, 20px)',
                    margin: 'clamp(20px, 3vw, 24px) 0',
                    border: '1px solid #e2e8f0'
                  }}>
                    <h3 style={{
                      fontSize: 'clamp(14px, 1.8vw, 16px)',
                      fontWeight: 600,
                      color: '#4a5568',
                      margin: '0 0 clamp(10px, 1.5vw, 12px) 0'
                    }}>
                      商品描述
                    </h3>
                    <div style={{
                      color: '#718096',
                      fontSize: 'clamp(13px, 1.5vw, 15px)',
                      lineHeight: '1.6',
                      whiteSpace: 'pre-line',
                      maxHeight: window.innerWidth <= 768 ? '100px' : '120px',
                      overflowY: 'auto'
                    }}>
                      {product.description}
                    </div>
                  </div>

                  {/* 購買區域 */}
                  <div style={{
                    background: 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)',
                    borderRadius: 'clamp(12px, 2vw, 16px)',
                    padding: 'clamp(20px, 3vw, 24px)',
                    border: '1px solid #e2e8f0',
                    marginTop: 'clamp(24px, 4vw, 30px)'
                  }}>
                    <div style={{
                      fontSize: 'clamp(14px, 1.8vw, 16px)',
                      fontWeight: 600,
                      color: '#4a5568',
                      marginBottom: 'clamp(12px, 2vw, 16px)'
                    }}>
                      選擇數量
                    </div>
                    <Row gutter={[16, 12]} align="middle">
                      <Col xs={24} sm={6} md={8}>
                        <InputNumber
                          min={1}
                          max={99}
                          value={quantity}
                          onChange={val => setQuantity(val)}
                          style={{
                            width: '100%',
                            borderRadius: '8px',
                            border: '1px solid #e2e8f0',
                            height: 'clamp(40px, 5vw, 48px)',
                            fontSize: 'clamp(14px, 1.5vw, 16px)'
                          }}
                        />
                      </Col>
                      <Col xs={24} sm={18} md={16}>
                        <Button
                          type="primary"
                          size="large"
                          loading={cartLoading}
                          onClick={handleAddToCart}
                          className="addtocart-btn"
                          style={{
                            height: 'clamp(40px, 5vw, 48px)',
                            fontSize: 'clamp(14px, 1.5vw, 16px)',
                            width: '100%'
                          }}
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
          width={window.innerWidth <= 768 ? '95vw' : '90vw'}
          style={{
            maxWidth: window.innerWidth <= 768 ? '400px' : '800px'
          }}
          bodyStyle={{
            padding: 'clamp(16px, 3vw, 20px)',
            background: 'white',
            borderRadius: 'clamp(12px, 2vw, 16px)'
          }}
        >
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            borderRadius: 'clamp(10px, 1.5vw, 12px)',
            padding: 'clamp(16px, 3vw, 20px)'
          }}>
            <img
              src={product?.images?.[currentImage]}
              alt="大圖預覽"
              style={{
                maxHeight: window.innerWidth <= 768 ? '60vh' : '70vh',
                maxWidth: '100%',
                objectFit: 'contain',
                borderRadius: 'clamp(6px, 1vw, 8px)'
              }}
            />
          </div>
        </Modal>
      </div>
    </div>
  );
}

export default ProductDetail;