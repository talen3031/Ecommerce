import React, { useEffect, useState } from "react";
import { Table, Pagination, Spin, Input, Button, Space, InputNumber, Select, Row, Col, message,Image } from "antd";
import api from "./api";
import RecommendList from "./RecommendList";
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
  const [pageInfo, setPageInfo] = useState({ page: 1, pages: 1, total: 0, per_page: 10 });
  const [loading, setLoading] = useState(false);

  const [searchValue, setSearchValue] = useState("");
  const [minPrice, setMinPrice] = useState();
  const [maxPrice, setMaxPrice] = useState();
  const [category, setCategory] = useState("");
  const [sortField, setSortField] = useState("");
  const [sortOrder, setSortOrder] = useState("");
  const [cartLoading, setCartLoading] = useState({});
  const [cartQuantity, setCartQuantity] = useState({});

  // 查詢 API
  const fetchProducts = (page = 1, pageSize = 10) => {
    setLoading(true);
    let url = `/products?page=${page}&per_page=${pageSize}`;
    if (searchValue) url += `&keyword=${encodeURIComponent(searchValue)}`;
    if (minPrice !== undefined && minPrice !== null && minPrice !== "") url += `&min_price=${minPrice}`;
    if (maxPrice !== undefined && maxPrice !== null && maxPrice !== "") url += `&max_price=${maxPrice}`;
    if (category) url += `&category_id=${category}`;
    if (sortField) url += `&sort_by=${sortField}&order=${sortOrder || "asc"}`;
    api.get(url)
      .then(res => { //API 請求成功時進入這個區塊，res.data 就是回傳的資料
        setProducts(res.data.products || []);
        setPageInfo({
          page: res.data.page, //page 當前頁，pages 總頁數，total 總商品數，per_page 每頁幾
          pages: res.data.pages,
          total: res.data.total,
          per_page: res.data.per_page || 10,
        });
      })
      .finally(() => setLoading(false)); //API 完成（不管成功失敗）後，設定 loading 為 false，畫面轉圈 loading 動畫關掉
  };

  useEffect(() => {
    fetchProducts(pageInfo.page, pageInfo.per_page);
    // eslint-disable-next-line
  }, [searchValue, minPrice, maxPrice, category, sortField, sortOrder]);

  const handlePageChange = (page, pageSize) => {
    setPageInfo(prev => ({ ...prev, page }));  //把 pageInfo 狀態裡的 page 更新成新頁碼
    fetchProducts(page, pageSize);//呼叫 API 取得指定分頁的商品列表
  };

  const handleTableChange = (pagination, filters, sorter) => {
    if (sorter.order) {
      setSortField(sorter.field);
      setSortOrder(sorter.order === "ascend" ? "asc" : "desc");
    } else {
      setSortField("");
      setSortOrder("");
    }
  };

  const handleSearch = () => {
    setPageInfo(prev => ({ ...prev, page: 1 }));
  };

  const handleClear = () => {
    setSearchValue("");
    setMinPrice();
    setMaxPrice();
    setCategory("");
    setSortField("");
    setSortOrder("");
    setPageInfo(prev => ({ ...prev, page: 1 }));
  };

  // 加入購物車
  const handleAddToCart = async (productId) => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      message.error("請先登入");
      return;
    }
    const quantity = cartQuantity[productId] || 1;
    setCartLoading(loading => ({ ...loading, [productId]: true }));
    try {
      await api.post(`/cart/${userId}/add`, {
        product_id: productId,
        quantity,
      });
      message.success("已加入購物車！");
    } catch (err) {
      message.error("加入購物車失敗：" + (err.response?.data?.error || err.message));
    }
    setCartLoading(loading => ({ ...loading, [productId]: false }));
  };

  const columns = [
    {
    title: "圖片",
    dataIndex: "image",
    render: (value) =>
      value ? (
        <Image
          src={value}
          width={50}
          height={50}
          style={{ objectFit: "cover", borderRadius: 8 }}
          alt="商品圖"
          fallback="https://via.placeholder.com/60x60?text=No+Image"
        />
      ) : (
        <span style={{ color: "#bbb" }}>無圖</span>
      ),
    },
    { title: '名稱', dataIndex: 'title', sorter: true },
     // 原價：特價時顯示刪除線
    {
      title: "原價",
      dataIndex: "price",
      render: (value, record) =>
        record.on_sale
          ? <span style={{ textDecoration: "line-through", color: "#888" }}>NT${value}</span>
          : <span>NT${value}</span>
    },
    // 折扣後價格：只有特價時顯示
    {
      title: "特價",
      dataIndex: "sale_price",
      render: (value, record) =>
        record.on_sale
          ? <span style={{ color: "#fa541c", fontWeight: "bold" }}>NT${value}</span>
          : <span style={{ color: "#aaa" }}>—</span>
    },
    {
    title: "分類",
    dataIndex: "category_id",
    render: (value) => categoryMap[value] || "未知"
    },
    {
    title: "分類id",
    dataIndex: "category_id"
    },
    {
      title: '加入購物車',
      render: (_, record) => (
        <Space>
          <InputNumber
            min={1}
            max={99}
            defaultValue={1}
            style={{ width: 60 }}
            value={cartQuantity[record.id] || 1}
            onChange={val => setCartQuantity(q => ({ ...q, [record.id]: val }))}
          />
          <Button
            loading={cartLoading[record.id]}
            onClick={() => handleAddToCart(record.id)}
            type="primary"
          >
            加入
          </Button>
        </Space>
      ),
    }
  ];

  return (
    <div style={{ maxWidth: 900, margin: "40px auto" }}>
      <h2>商品列表</h2>
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
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={products}
          rowKey="id"
          pagination={false}
          onChange={handleTableChange}
        />
      </Spin>
      <div style={{ textAlign: "center", margin: "24px 0" }}>
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
      <RecommendList userId={localStorage.getItem("user_id")} mode="user" limit={6} />

    </div>
  );
}

export default ProductList;
