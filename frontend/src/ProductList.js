import React, { useEffect, useState } from "react";
import { Card, Row, Col, Spin, Input, Button, InputNumber, Select, Pagination, message, Tag } from "antd";
import RecommendList from "./RecommendList";
import api from "./api";

const categoryOptions = [
  { label: "全部", value: "" },
  { label: "3C", value: 1 },
  { label: "飾品", value: 2 },
  { label: "男生衣服", value: 3 },
  { label: "女生衣服", value: 4 },
];
const categoryMap = Object.fromEntries(categoryOptions.map(opt => [opt.value, opt.label]));

function ProductList({ onSelectProduct }) {
  const [products, setProducts] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, pages: 1, total: 0, per_page: 12 });
  const [loading, setLoading] = useState(false);

  const [searchValue, setSearchValue] = useState("");
  const [minPrice, setMinPrice] = useState();
  const [maxPrice, setMaxPrice] = useState();
  const [category, setCategory] = useState("");

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

  return (
    <div style={{ maxWidth: 900, margin: "40px auto" }}>
      <h2>商品瀏覽</h2>
      {/* 搜尋/篩選 */}
      <Row gutter={8} style={{ marginBottom: 16 }}>
        <Col>
          <Input
            placeholder="關鍵字"
            value={searchValue}
            onChange={e => setSearchValue(e.target.value)}
            style={{ width: 150 }}
            onPressEnter={handleSearch}
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
          <Button type="primary" onClick={handleSearch}>搜尋</Button>
        </Col>
        <Col>
          <Button onClick={handleClear}>清除</Button>
        </Col>
      </Row>

      {/* 商品卡片2欄排列 */}
      <Spin spinning={loading}>
        <Row gutter={[24, 24]}>
          {products.map(product => (
            <Col xs={24} sm={12} md={12} lg={12} key={product.id}>
              <Card
                hoverable
                onClick={() => onSelectProduct(product.id)}
                cover={
                  <img
                    src={product.images?.[0]}
                    alt={product.title}
                    style={{ height: 240, objectFit: "cover", borderRadius: 8 }}
                  />
                }
                style={{
                  borderRadius: 12,
                  boxShadow: "0 2px 16px #eee",
                  cursor: "pointer",
                  minHeight: 370
                }}
                bodyStyle={{ padding: 16 }}
              >
                <div style={{ fontWeight: 600, fontSize: 18, marginBottom: 4 }}>{product.title}</div>
                <div>
                  {product.on_sale ? (
                    <>
                      <span style={{ color: "#fa541c", fontWeight: "bold", fontSize: 18 }}>NT${product.sale_price}</span>
                      <span style={{ textDecoration: "line-through", color: "#888", marginLeft: 8 }}>NT${product.price}</span>
                      <Tag color="red" style={{ marginLeft: 8, verticalAlign: "middle" }}>特價</Tag>
                    </>
                  ) : (
                    <span style={{ fontWeight: "bold", fontSize: 18 }}>NT${product.price}</span>
                  )}
                </div>
                <div style={{ color: "#999", fontSize: 14, margin: "6px 0" }}>
                  {categoryMap[product.category_id] || "未知"}
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
      <div style={{ textAlign: "right", color: "#888" }}>
        共 {pageInfo.total} 筆資料
      </div>
      <RecommendList
        userId={localStorage.getItem("user_id")}
        mode="user"
        limit={6}
        onSelectProduct={onSelectProduct}
      />
    </div>
  );
}

export default ProductList;
