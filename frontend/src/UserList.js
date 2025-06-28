import React, { useEffect, useState } from "react";
import { Table, Input, Button, Spin, Space, message } from "antd";
import api from "./api";

function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchVal, setSearchVal] = useState("");
  const [pageInfo, setPageInfo] = useState({ page: 1, total: 0, pageSize: 10 });

  // 取得會員清單
  const fetchUsers = (page = 1, keyword = "") => {
    setLoading(true);
    let url = `/users/all?page=${page}&per_page=${pageInfo.pageSize}`;
    if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
    api.get(url)
      .then(res => {
        // 你 API 若是 {users: [...], page:1, total:99}，就要這樣寫
        setUsers(res.data.users || []);
        setPageInfo({
          page: res.data.page || 1,
          total: res.data.total || 0,
          pageSize: res.data.per_page || 10
        });
      })
      .catch(() => message.error("查詢會員失敗"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchUsers(1, searchVal);
    // eslint-disable-next-line
  }, []);

  // 搜尋
  const handleSearch = () => fetchUsers(1, searchVal);

  // 分頁切換
  const handlePageChange = (page) => fetchUsers(page, searchVal);

  const columns = [
    { title: "會員ID", dataIndex: "id", sorter: true },
    { title: "使用者名稱", dataIndex: "username" },
    { title: "Email", dataIndex: "email" },
    { title: "建立時間", dataIndex: "created_at" },
    // 你可再加更多欄位...
  ];

  return (
    <div style={{ maxWidth: 900, margin: "40px auto" }}>
      <h2>會員資訊清單</h2>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜尋使用者名稱/Email"
          value={searchVal}
          onChange={e => setSearchVal(e.target.value)}
          onPressEnter={handleSearch}
          style={{ width: 200 }}
        />
        <Button onClick={handleSearch} type="primary">搜尋</Button>
      </Space>
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          pagination={{
            current: pageInfo.page,
            pageSize: pageInfo.pageSize,
            total: pageInfo.total,
            onChange: handlePageChange
          }}
        />
      </Spin>
    </div>
  );
}

export default UserList;
