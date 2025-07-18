import React, { useEffect, useState } from "react";
import { Table, Button, Popconfirm, message, Modal, Form, Input, InputNumber, Select, DatePicker, Upload, Spin } from "antd";
import { PlusOutlined } from '@ant-design/icons';
import api from "../../api/api";
import dayjs from "dayjs";
import { useNavigate } from "react-router-dom";
import { ReactSortable } from "react-sortablejs";
import '../../styles/AdminPage.css'

const categoryOptions = [
  { label: "全部", value: "" },
  { label: "褲子", value: 1 },
  { label: "帽子", value: 2 },
  { label: "上衣", value: 3 },
  { label: "外套", value: 4 },
];

// 型別安全判斷商品狀態
const isActive = (val) => val === true || val === 1 || val === "1" || val === "true";

function ProductManager() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);

  const [saleModalOpen, setSaleModalOpen] = useState(false);
  const [saleForm] = Form.useForm();
  const [saleProductId, setSaleProductId] = useState(null);

  const navigate = useNavigate();

  const fetchProducts = () => {
    setLoading(true);
    api.get("/products/admin?per_page=1000")
      .then(res => setProducts(res.data.products || res.data || []))
      .finally(() => setLoading(false));
  };
  useEffect(fetchProducts, []);

  const openEdit = (record) => {
    setEditing(record);
    setModalOpen(true);
    if (record) {
      form.setFieldsValue(record);
      setFileList((record.images || []).map(url => ({ uid: url, url, name: url })));
    } else {
      form.resetFields();
      setFileList([]);
    }
  };

  const handleSave = async () => {
    if (uploading) {
      message.warning("圖片尚在上傳中，請稍候再試");
      return;
    }
    try {
      const values = await form.validateFields();
      const imageUrls = fileList.map(file => file.url || file.response?.url).filter(Boolean);
      const payload = { ...values, images: imageUrls };

      if (editing) {
        await api.put(`/products/${editing.id}`, payload);
        message.success("已更新商品！");
      } else {
        await api.post("/products", payload);
        message.success("已新增商品！");
      }
      setModalOpen(false);
      fetchProducts();
    } catch (err) {
      message.error("操作失敗：" + (err.response?.data?.error || err.message));
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/products/${id}`);
      message.success("已刪除商品！");
      fetchProducts();
    } catch {
      message.error("刪除失敗");
    }
  };

  const openSaleModal = (productId) => {
    setSaleProductId(productId);
    setSaleModalOpen(true);
    saleForm.resetFields();
  };

  const handleSaleSave = async () => {
    try {
      const values = await saleForm.validateFields();
      const { discount, start_date, end_date, description } = values;
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

  // 下架
  const handleDeactivate = async (id) => {
    try {
      await api.post(`/products/${id}/deactivate`);
      message.success("商品已下架！");
      fetchProducts();
    } catch {
      message.error("下架失敗");
    }
  };

  // 上架
  const handleActivate = async (id) => {
    try {
      await api.post(`/products/${id}/activate`);
      message.success("商品已重新上架！");
      fetchProducts();
    } catch {
      message.error("上架失敗");
    }
  };

  const columns = [
    { title: "ID", dataIndex: "id", sorter: (a, b) => a.id - b.id, defaultSortOrder: "ascend" },
    {
      title: "名稱",
      dataIndex: "title",
      render: (value, record) => (
        <Button type="link" onClick={() => navigate(`/products/${record.id}`)}>
          {value}
        </Button>
      )
    },
    {
      title: "原價",
      dataIndex: "price",
      render: (value, record) => record.on_sale
        ? <span style={{ textDecoration: "line-through", color: "#888" }}>NT${value}</span>
        : <span>NT${value}</span>
    },
    {
      title: "特價",
      dataIndex: "sale_price",
      render: (value, record) => record.on_sale
        ? <span style={{ color: "#fa541c", fontWeight: "bold" }}>NT${value}</span>
        : <span style={{ color: "#aaa" }}>—</span>
    },
    { title: "分類", dataIndex: "category_id" },
    {
      title: "圖片",
      dataIndex: "images",
      render: (images) =>
        images && images.length > 0 ? (
          <img
            src={images[0]}
            alt="商品圖"
            style={{
              width: 50,
              height: 50,
              objectFit: "cover",
              borderRadius: 6
            }}
          />
        ) : (
          <span style={{ color: "#bbb" }}>無圖</span>
        )
    },
    {
      title: "狀態",
      dataIndex: "is_active",
      render: (value, record) => {
        return isActive(value)
          ? <span style={{ color: "#52c41a" }}>上架</span>
          : <span style={{ color: "#f5222d" }}>下架</span>;
      }
    },
    {
      title: "操作",
      render: (_, record) => (
        <>
          <Button size="small" onClick={() => openEdit(record)} style={{ marginRight: 8 ,color: "#808481ff"}}>編輯</Button>
          <Popconfirm title="確定刪除？" onConfirm={() => handleDelete(record.id)}>
          <Button danger size="small" style={{ marginRight: 8 }}>刪除</Button>
          </Popconfirm>
          <Button size="small" type="dashed" onClick={() => openSaleModal(record.id)} style={{ marginRight: 8 ,color: "#9509faff"}}>特價</Button>
          {isActive(record.is_active) ? (
            <Popconfirm title="確定要下架這個商品嗎？" onConfirm={() => handleDeactivate(record.id)}>
              <Button size="small" danger>下架</Button>
            </Popconfirm>
          ) : (
            <Popconfirm title="確定要重新上架？" onConfirm={() => handleActivate(record.id)}>
              <Button size="small" type="primary">上架</Button>
            </Popconfirm>
          )}
        </>
      ),
    },
  ];

  return (
    <div className="admin-container">
      <Button type="primary" style={{ marginBottom: 16 }} onClick={() => openEdit(null)}>
        新增商品
      </Button>
      <div className="admin-table-scroll">
        <Table
          columns={columns}
          dataSource={products}
          rowKey="id"
          loading={loading}
          size="small" // <-- 關鍵：密集型管理表格
        />
      </div>
      {/* 新增/編輯商品 modal */}
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

          <Form.Item label="圖片上傳" required>
            <Spin spinning={uploading} tip="圖片上傳中...">
              <Upload
                listType="picture-card"
                fileList={fileList}
                customRequest={async ({ file, onSuccess, onError }) => {
                  const formData = new FormData();
                  formData.append("image", file);
                  setUploading(true);
                  try {
                    const res = await api.postForm("/upload/upload_image", formData);
                    setFileList(prev => [...prev, { uid: file.uid, name: file.name, url: res.data.url }]);
                    onSuccess();
                  } catch (err) {
                    onError(err);
                  } finally {
                    setUploading(false);
                  }
                }}
                onRemove={(file) => {
                  setFileList(prev => prev.filter(f => f.uid !== file.uid));
                }}
                showUploadList={false}
              >
                {fileList.length < 5 && <div><PlusOutlined /><div style={{ marginTop: 8 }}>上傳</div></div>}
              </Upload>
              <ReactSortable
                tag="div"
                animation={180}
                list={fileList}
                setList={setFileList}
                style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}
              >
                {fileList.map(file => (
                  <div
                    key={file.uid}
                    style={{
                      width: 92, height: 92, borderRadius: 8, border: "1.5px solid #ccc",
                      position: "relative", overflow: "hidden", background: "#fafafa", boxShadow: "0 1px 4px #0001"
                    }}
                  >
                    <img
                      src={file.url}
                      alt={file.name}
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      draggable={false}
                    />
                    <Button
                      danger size="small"
                      style={{ position: "absolute", top: 3, right: 3, padding: "0 6px", fontSize: 13, borderRadius: 9, zIndex: 2 }}
                      onClick={() => setFileList(prev => prev.filter(f => f.uid !== file.uid))}
                    >x</Button>
                  </div>
                ))}
              </ReactSortable>
            </Spin>
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
          <Form.Item name="discount" label="折數（例如 0.8 代表 8 折）" rules={[{ required: true, type: "number", min: 0.01, max: 0.99 }]}>
            <InputNumber step={0.01} min={0.01} max={0.99} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="start_date" label="特價開始" rules={[{ required: true }]}>
            <DatePicker showTime format="YYYY-MM-DDTHH:mm:ss" style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="end_date" label="特價結束" rules={[{ required: true }]}>
            <DatePicker showTime format="YYYY-MM-DDTHH:mm:ss" style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="description" label="活動說明">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default ProductManager;
