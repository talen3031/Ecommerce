import React, { useEffect, useState } from "react";
import { Table, Button, Popconfirm, message, Modal, Form, Input, InputNumber, Select, DatePicker } from "antd";
import api from "./api";
import dayjs from "dayjs";

const categoryOptions = [
  { label: "全部", value: "" },
  { label: "3C", value: 1 },
  { label: "飾品", value: 2 },
  { label: "男生衣服", value: 3 },
  { label: "女生衣服", value: 4 },
];

function ProductManager() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null); // null=新增，否則編輯
  const [form] = Form.useForm();

  // 特價 modal 狀態
  const [saleModalOpen, setSaleModalOpen] = useState(false);
  const [saleForm] = Form.useForm();
  const [saleProductId, setSaleProductId] = useState(null);

  // 取得所有商品
  const fetchProducts = () => {
    setLoading(true);
    api.get("/products?per_page=1000")
      .then(res => setProducts(res.data.products || res.data || []))
      .finally(() => setLoading(false));
  };
  useEffect(fetchProducts, []);

  // 開啟編輯/新增表單
  const openEdit = (record) => {
    setEditing(record);
    setModalOpen(true);
    if (record) {
      form.setFieldsValue(record);
    } else {
      form.resetFields();
    }
  };

  // 送出新增/編輯
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editing) {
        await api.put(`/products/${editing.id}`, values);
        message.success("已更新商品！");
      } else {
        await api.post("/products/add", values);
        message.success("已新增商品！");
      }
      setModalOpen(false);
      fetchProducts();
    } catch (err) {
      message.error("操作失敗：" + (err.response?.data?.error || err.message));
    }
  };

  // 刪除商品
  const handleDelete = async (id) => {
    try {
      await api.delete(`/products/${id}`);
      message.success("已刪除商品！");
      fetchProducts();
    } catch {
      message.error("刪除失敗");
    }
  };

  // 新增特價
  const openSaleModal = (productId) => {
    setSaleProductId(productId);
    setSaleModalOpen(true);
    saleForm.resetFields();
  };

  const handleSaleSave = async () => {
    try {
      const values = await saleForm.validateFields();
      const { discount, start_date, end_date, description } = values;

      // 格式轉換，API 要字串
      const start_date_str = dayjs(start_date).format("YYYY-MM-DDTHH:mm:ss");
      const end_date_str = dayjs(end_date).format("YYYY-MM-DDTHH:mm:ss");

      await api.post(`/products/sale/${saleProductId}`, {
        discount,
        start_date: start_date_str,
        end_date: end_date_str,
        description,
      });
      message.success("已新增特價！");
      setSaleModalOpen(false);
      fetchProducts();
    } catch (err) {
      message.error("新增特價失敗：" + (err.response?.data?.error || err.message));
    }
  };

  const columns = [
    { title: "ID", dataIndex: "id" ,sorter: (a, b) => a.id - b.id,defaultSortOrder: "ascend", },
    { title: "名稱", dataIndex: "title" },
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
    { title: "分類", dataIndex: "category_id" },
    { title: "圖片", dataIndex: "image", render: (v) => v && <img src={v} alt="商品圖" width={50} /> },
    {
      title: "操作",
      render: (_, record) => (
        <>
          <Button size="small" onClick={() => openEdit(record)} style={{ marginRight: 8 }}>
            編輯
          </Button>
          <Popconfirm title="確定刪除？" onConfirm={() => handleDelete(record.id)}>
            <Button danger size="small" style={{ marginRight: 8 }}>刪除</Button>
          </Popconfirm>
          <Button size="small" type="dashed" onClick={() => openSaleModal(record.id)}>
            新增特價
          </Button>
        </>
      ),
    },
  ];

  return (
    <div>
      <Button type="primary" style={{ marginBottom: 16 }} onClick={() => openEdit(null)}>
        新增商品
      </Button>
      <Table
        columns={columns}
        dataSource={products}
        rowKey="id"
        loading={loading}
      />

      {/* 商品新增/編輯 modal */}
      <Modal
        title={editing ? "編輯商品" : "新增商品"}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="商品名稱" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="price" label="價格" rules={[{ required: true, type: "number", min: 1 }]}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="category_id" label="分類" rules={[{ required: true }]}>
            <Select options={categoryOptions} />
          </Form.Item>
          <Form.Item name="image" label="圖片網址">
            <Input />
          </Form.Item>
          <Form.Item name="description" label="description">
            <Input />
          </Form.Item>
        </Form>
      </Modal>

      {/* 新增特價 modal */}
      <Modal
        title="新增特價"
        open={saleModalOpen}
        onOk={handleSaleSave}
        onCancel={() => setSaleModalOpen(false)}
        destroyOnClose
      >
        <Form form={saleForm} layout="vertical">
          <Form.Item
            name="discount"
            label="折數（例如 0.8 代表 8 折）"
            rules={[
              { required: true, message: "請輸入折數" },
              { type: "number", min: 0.01, max: 0.99, message: "折數必須介於 0~1 之間" },
            ]}
          >
            <InputNumber step={0.01} min={0.01} max={0.99} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="start_date"
            label="特價開始"
            rules={[{ required: true, message: "請選擇開始日期" }]}
          >
            <DatePicker showTime format="YYYY-MM-DDTHH:mm:ss" style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="end_date"
            label="特價結束"
            rules={[{ required: true, message: "請選擇結束日期" }]}
          >
            <DatePicker showTime format="YYYY-MM-DDTHH:mm:ss" style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="description"
            label="活動說明"
            rules={[]}
          >
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default ProductManager;
