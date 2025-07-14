import React, { useEffect, useState } from "react";
import { Table, Button, Modal, Form, Input, InputNumber, DatePicker, Switch, message, Space, Select } from "antd";
import api from "./api";
import dayjs from "dayjs";

function DiscountCodeAdmin() {
  const [codes, setCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [addVisible, setAddVisible] = useState(false);
  const [products, setProducts] = useState([]);

  const [form] = Form.useForm();

  // 取得商品清單（for 指定商品折扣碼）
  const fetchProducts = async () => {
    try {
      const res = await api.get("/products/admin?per_page=1000");
      setProducts(res.data.products || []);
    } catch (err) {
      setProducts([]);
    }
  };

  // 取得折扣碼清單
  const fetchCodes = async () => {
    setLoading(true);
    try {
      const res = await api.get("/discount_codes/");
      setCodes(res.data || []);
    } catch (err) {
      message.error("取得折扣碼失敗");
    }
    setLoading(false);
  };

  useEffect(() => { 
    fetchCodes(); 
    fetchProducts();
  }, []);

  // 新增折扣碼
  const handleAdd = async (values) => {
    try {
      const data = {
        ...values,
        product_id: values.product_id === "all" ? null : values.product_id,
        valid_from: values.valid_from.format("YYYY-MM-DDTHH:mm:ss"),
        valid_to: values.valid_to.format("YYYY-MM-DDTHH:mm:ss"),
        discount: values.discount || null,
        amount: values.amount || null,
      };
      await api.post("/discount_codes/", data);
      message.success("新增成功！");
      setAddVisible(false);
      form.resetFields();
      fetchCodes();
    } catch (err) {
      message.error("新增失敗：" + (err.response?.data?.error || err.message));
    }
  };

  // 停用折扣碼
  const handleDeactivate = async (id) => {
    try {
      await api.patch(`/discount_codes/${id}/deactivate`);
      message.success("已停用");
      fetchCodes();
    } catch (err) {
      message.error("停用失敗");
    }
  };

  // 輔助：根據 product_id 找名稱
  const getProductName = (product_id) => {
    if (!product_id) return "全站通用";
    const product = products.find(p => p.id === product_id || p.id === Number(product_id));
    return product ? product.title : product_id;
  };

  const columns = [
    { title: "折扣碼", dataIndex: "code" },
    { title: "描述", dataIndex: "description" },
    { title: "指定商品", dataIndex: "product_id", render: v => getProductName(v) },
    { title: "折扣%", dataIndex: "discount", render: v => v ? (v * 100 + "%") : "-" },
    { title: "折抵金額", dataIndex: "amount", render: v => v ? ("NT$" + v) : "-" },
    { title: "滿額", dataIndex: "min_spend", render: v => v ? ("NT$" + v) : "-" },
    { title: "總可用", dataIndex: "usage_limit" },
    { title: "每人限用", dataIndex: "per_user_limit" },
    { title: "開始", dataIndex: "valid_from", render: v => v && v.slice(0, 16).replace("T", " ") },
    { title: "結束", dataIndex: "valid_to", render: v => v && v.slice(0, 16).replace("T", " ") },
    { title: "啟用", dataIndex: "is_active", render: v => v ? "啟用" : "停用" },
    {
      title: "操作",
      render: (_, record) => (
        <Space>
          {record.is_active && (
            <Button danger size="small" onClick={() => handleDeactivate(record.id)}>
              停用
            </Button>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ maxWidth: 1000, margin: "40px auto" }}>
      <h2>折扣碼管理</h2>
      <Button type="primary" style={{ marginBottom: 16 }} onClick={() => setAddVisible(true)}>
        新增折扣碼
      </Button>
      <Table
        columns={columns}
        dataSource={codes}
        rowKey="id"
        loading={loading}
        pagination={false}
      />

      {/* 新增折扣碼 Modal */}
      <Modal
        title="新增折扣碼"
        open={addVisible}
        onCancel={() => setAddVisible(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item name="code" label="折扣碼" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input />
          </Form.Item>
          {/* 這裡改為下拉選單 */}
          <Form.Item name="product_id" label="指定商品">
            <Select
              placeholder="選擇指定商品（預設全站通用）"
              allowClear
              defaultValue="all"
              options={[
                { label: "全站通用", value: "all" },
                ...products
                  .filter(p => p.is_active)
                  .map(p => ({
                    label: `${p.title} (ID:${p.id})`,
                    value: p.id
                  }))
              ]}
            />
          </Form.Item>
          <Form.Item label="折扣%（0.9 = 9折，與折抵金額擇一）" name="discount">
            <InputNumber min={0.01} max={1} step={0.01} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="折抵金額（與折扣%擇一）" name="amount">
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="滿額才能用（選填）" name="min_spend">
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="總可用次數" name="usage_limit">
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="每人限用次數" name="per_user_limit">
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="開始日期" name="valid_from" rules={[{ required: true }]}>
            <DatePicker showTime format="YYYY-MM-DD HH:mm:ss" style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="結束日期" name="valid_to" rules={[{ required: true }]}>
            <DatePicker showTime format="YYYY-MM-DD HH:mm:ss" style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              新增
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default DiscountCodeAdmin;
