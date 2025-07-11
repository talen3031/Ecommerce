import React, { useEffect, useState } from "react";
import { Card, Row, Col, Spin, Input, Button, InputNumber, Select, Pagination, Drawer } from "antd";
import RecommendList from "./RecommendList";
import api from "./api";
import { useNavigate } from "react-router-dom";

const categoryOptions = [
  { label: "全部", value: "" },
  { label: "3C", value: 1 },
  { label: "飾品", value: 2 },
  { label: "男生衣服", value: 3 },
  { label: "女生衣服", value: 4 },
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

  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();

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

  const handleSearch = () => {
    setPageInfo(prev => ({ ...prev, page: 1 }));
    fetchProducts(1, pageInfo.per_page);
  };

  const handleClear = () => {
    setSearchValue("");
    setMinPrice();
    setMaxPrice();
    setCategory("");
    setPageInfo(prev => ({ ...prev, page: 1 }));
    fetchProducts(1, pageInfo.per_page);
  };

  const handleGoDetail = (id) => navigate(`/products/${id}`);

  return (
    <>
      {/*  Banner 無按鈕 */}
      <div
        style={{
          width: "100vw",
          height: 80,
          background: "#eee",
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <span className="typing-banner">Nerd.com</span>
        {/* 這段只需在 App 載入一次即可 */}
        <style>
          {`
            .typing-banner {
              color: #000;
              font-weight: 900;
              font-size: 32px;
              letter-spacing: 2px;
              font-family: Oswald, 'Noto Sans TC', Arial, sans-serif;
              user-select: none;
              border-right: 4px solid #000;
              white-space: nowrap;
              overflow: hidden;
              display: inline-block;
              animation: typing 2.2s steps(9, end), blink-caret 0.9s step-end infinite;
              width: 9ch;
            }
            @keyframes typing {
              from { width: 0 }
              to { width: 8ch }
            }
            @keyframes blink-caret {
              50% { border-color: transparent }
            }
          `}
        </style>
      </div>



      {/* 假設你有 Drawer (側邊選單) 就維持原本寫法（不會被 Banner 蓋住） */}

      {/* 主內容 */}
      <div style={{ marginTop: 90, maxWidth: 980, marginLeft: "auto", marginRight: "auto", fontFamily: "'Inter', 'Roboto', 'sans-serif'" }}>
        {/* 搜尋/篩選 */}
        <Row gutter={8} style={{ marginBottom: 18 }}>
          <Col>
            <Input
              placeholder="關鍵字"
              value={searchValue}
              onChange={e => setSearchValue(e.target.value)}
              style={{ width: 150 }}
              onPressEnter={handleSearch}
              allowClear
            />
          </Col>
          <Col>
            <InputNumber
              placeholder="最低價"
              min={0}
              value={minPrice}
              onChange={setMinPrice}
              style={{ width: 100 }}
            />
          </Col>
          <Col>
            <InputNumber
              placeholder="最高價"
              min={0}
              value={maxPrice}
              onChange={setMaxPrice}
              style={{ width: 100 }}
            />
          </Col>
          <Col>
            <Select
              placeholder="分類"
              value={category}
              options={categoryOptions}
              onChange={val => setCategory(val)}
              style={{ width: 100 }}
              allowClear
            />
          </Col>
          <Col>
            <Button type="default" onClick={handleSearch} style={{ borderColor: "#222", color: "#222" }}>搜尋</Button>
          </Col>
          <Col>
            <Button onClick={handleClear} style={{ background: "#f4f4f4", color: "#888", border: "none" }}>清除</Button>
          </Col>
        </Row>

        {/* 商品卡片2欄排列 */}
        <Spin spinning={loading}>
          <Row gutter={[32, 32]}>
            {products.map(product => (
              <Col xs={24} sm={12} md={12} lg={12} key={product.id}>
                <Card
                  hoverable
                  onClick={() => handleGoDetail(product.id)}
                  cover={
                    <img
                      src={product.images?.[0]}
                      alt={product.title}
                      style={{
                        height: 240, objectFit: "cover", borderRadius: 12,
                        border: "1px solid #ebebeb", background: "#fff"
                      }}
                    />
                  }
                  style={{
                    borderRadius: 12,
                    border: "1px solid #ddd",
                    cursor: "pointer",
                    minHeight: 350,
                    background: "#fafbfc",
                    transition: "all 0.18s cubic-bezier(.22,1,.36,1)",
                  }}
                  bodyStyle={{ padding: 18 }}
                  className="minimal-card"
                >
                  <div style={{
                    fontWeight: 600, fontSize: 19, marginBottom: 6, color: "#1a1a1a"
                  }}>
                    {product.title}
                  </div>
                  <div style={{ marginBottom: 4 }}>
                    {product.on_sale ? (
                      <>
                        <span style={{ color: "#1a1a1a", fontWeight: "bold", fontSize: 19 }}>NT${product.sale_price}</span>
                        <span style={{ textDecoration: "line-through", color: "#b2b2b2", marginLeft: 10, fontSize: 15 }}>NT${product.price}</span>
                      </>
                    ) : (
                      <span style={{ fontWeight: 500, fontSize: 18, color: "#1a1a1a" }}>NT${product.price}</span>
                    )}
                  </div>
                  <div style={{ color: "#6e6e6e", fontSize: 15 }}>
                    {categoryMap[product.category_id] || "－"}
                  </div>
                </Card>
              </Col>
            ))}
            {products.length === 0 && !loading && (
              <div style={{ color: "#aaa", margin: "40px auto" }}>找不到商品</div>
            )}
          </Row>
        </Spin>

        <div style={{ textAlign: "center", margin: "32px 0" }}>
          <Pagination
            current={pageInfo.page}
            pageSize={pageInfo.per_page}
            total={pageInfo.total}
            showSizeChanger={false}
            onChange={handlePageChange}
          />
        </div>
        <div style={{ textAlign: "right", color: "#aaa", fontSize: 14 }}>
          共 {pageInfo.total} 筆資料
        </div>
        <RecommendList
          userId={localStorage.getItem("user_id")}
          mode="user"
          limit={6}
          onSelectProduct={handleGoDetail}
        />

        {/* 卡片 hover 動畫 */}
        <style>
          {`
          .minimal-card:hover {
            transform: translateY(-4px) scale(1.018);
            border: 1.5px solid #333;
            background: #f2f2f2;
          }
          `}
        </style>
      </div>
    </>
  );
}

export default ProductList;
