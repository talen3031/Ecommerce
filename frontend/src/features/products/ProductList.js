import React, { useEffect, useState } from "react";
import { Card, Row, Col, Spin, Input, Button, InputNumber, Select, Pagination } from "antd";
import RecommendList from "../../components/RecommendList";
import api from "../../api/api";
import { useNavigate } from "react-router-dom";
import '../../styles/ProductList.css'
import { Skeleton } from "antd";
import '@fontsource/luckiest-guy';
import '@fontsource/bangers'; 
const categoryOptions = [
  { label: "全部", value: "" },
  { label: "褲子", value: 1 },
  { label: "帽子", value: 2 },
  { label: "上衣", value: 3 },
  { label: "外套", value: 4 },
];
  
const categoryMap = Object.fromEntries(categoryOptions.map(opt => [opt.value, opt.label]));

function ProductList() {
  const [products, setProducts] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, pages: 1, total: 0, per_page: 12 });
  const [loading, setLoading] = useState(false);

  const [searchValue, setSearchValue] = useState("");
  const [minPrice, setMinPrice] = useState();
  const [maxPrice, setMaxPrice] = useState();
  const [category, setCategory] = useState("");

  const navigate = useNavigate();
   // 這段是新增的 ↓
  const isLoggedIn = !!localStorage.getItem("user_id") && localStorage.getItem("role") === "user";
  const userId = localStorage.getItem("user_id");
  let guestId = localStorage.getItem("guest_id");
  
  const fetchProducts = (page = 1, pageSize = 12) => {
    setLoading(true);
    let url = `/products?page=${page}&per_page=${pageSize}`;
    if (searchValue) url += `&keyword=${encodeURIComponent(searchValue)}`;
    if (minPrice !== undefined && minPrice !== null && minPrice !== "") url += `&min_price=${minPrice}`;
    if (maxPrice !== undefined && maxPrice !== null && maxPrice !== "") url += `&max_price=${maxPrice}`;
    if (category) url += `&category_id=${category}`;
    api.get(url)
      .then(res => {
        setProducts(res.data.products || []);
        setPageInfo({
          page: res.data.page,
          pages: res.data.pages,
          total: res.data.total,
          per_page: res.data.per_page || 12,
        });
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProducts(pageInfo.page, pageInfo.per_page);
    // eslint-disable-next-line
  }, [searchValue, minPrice, maxPrice, category]);

  const handlePageChange = (page) => {
    setPageInfo(prev => ({ ...prev, page }));
    fetchProducts(page, pageInfo.per_page);
  };


  const handleGoDetail = (id) => navigate(`/products/${id}`);

  return (
    <div style={{ 
      background: 'linear-gradient(to bottom, #f8f9fa, #ffffff)',
      minHeight: '100vh',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Hero Banner */}
   
      {/* 主內容 */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '60px 20px',
        position: 'relative'
      }}>
        {/* 搜尋/篩選區域 */}
        {/* 商品網格 */}
        <Spin spinning={loading}>
          {loading ? (
            <Row gutter={[24, 32]}>
              {Array.from({ length: 8 }).map((_, idx) => (
                <Col xs={24} sm={12} md={8} lg={6} key={idx}>
                  <Card style={{
                    borderRadius: '16px',
                    overflow: 'hidden',
                    border: '1px solid #f0f0f0',
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.04)'
                  }}>
                    <Skeleton.Image style={{ 
                      width: '100%', 
                      height: 240, 
                      borderRadius: '12px',
                      marginBottom: 16 
                    }} active />
                    <Skeleton active paragraph={{ rows: 2 }} title={false} />
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <Row gutter={[24, 32]}>
              {products.map(product => (
                <Col xs={24} sm={12} md={8} lg={6} key={product.id}>
                  <Card
                    hoverable
                    onClick={() => handleGoDetail(product.id)}
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
                    找不到符合條件的商品
                  </div>
                </Col>
              )}
            </Row>
          )}
        </Spin>

        {/* 分頁 */}
        <div style={{ 
          textAlign: 'center',
          margin: '50px 0 30px',
          padding: '20px',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
        }}>
          <Pagination
            current={pageInfo.page}
            pageSize={pageInfo.per_page}
            total={pageInfo.total}
            showSizeChanger={false}
            onChange={handlePageChange}
            style={{
              '& .ant-pagination-item-active': {
                background:  'linear-gradient(135deg, #090909ff 0%, #764ba2 100%)',
                borderColor: '#667eea'
              }
            }}
          />
          <div style={{
            marginTop: '12px',
            color: '#718096',
            fontSize: '14px'
          }}>
            共 {pageInfo.total} 筆商品
          </div>
        </div>

        {/* 推薦商品 
        <div style={{
          background: 'white',
          padding: '40px 30px',
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          marginTop: '40px'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#2d3748',
            marginBottom: '30px',
            textAlign: 'center'
          }}>
            為你推薦
          </h2>
          <RecommendList
              userId={isLoggedIn ? userId : guestId}
              mode={isLoggedIn ? "user" : "guest"}
              limit={3}
              onSelectProduct={handleGoDetail}
            />
        </div>           */}
              

      </div>
    </div>
  );
}

export default ProductList;