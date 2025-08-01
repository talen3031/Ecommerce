import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import { Layout, List, Input, Button, Avatar, Spin, message as antdMsg, Popconfirm } from "antd";
import { SendOutlined, UserOutlined, DeleteOutlined } from "@ant-design/icons";
import { REACT_APP_SOCKET_URL } from "../../config";

const { Sider, Content } = Layout;

function AdminReply() {
  const socketRef = useRef(null);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const msgEndRef = useRef();

  // 最新選中 user 用於 socket 推播判斷
  const selectedUserRef = useRef(selectedUser);
  useEffect(() => {
    selectedUserRef.current = selectedUser;
  }, [selectedUser]);

  // 1. 只初始化一次 socket，監聽 receive_message
  useEffect(() => {
    fetchUsers();
    const sock = io(REACT_APP_SOCKET_URL, {
      query: { token: localStorage.getItem("token"), role: "admin" }
    });
    socketRef.current = sock;

    sock.on("system", msg => {
      console.log("[system]", msg);
    });

    sock.on("receive_message", data => {
      // 只 append 當前聊天室
      if (selectedUserRef.current && data.user_id === selectedUserRef.current.id) {
        setChatHistory(prev => Array.isArray(prev) ? [...prev, data] : [data]);
      }
    });

    return () => {
      sock.disconnect();
    };
    // eslint-disable-next-line
  }, []);

  // 2. 拉用戶清單
  function fetchUsers() {
    fetch(`${REACT_APP_SOCKET_URL}/chat/users`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    })
      .then(res => res.json())
      .then(data => setUsers(Array.isArray(data) ? data : []));
  }

  // 3. 點用戶時只拉聊天紀錄
  useEffect(() => {
    if (!selectedUser) return;
    setLoading(true);
    fetch(`${REACT_APP_SOCKET_URL}/chat/history/${selectedUser.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    })
      .then(res => res.json())
      .then(data => setChatHistory(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false));
  }, [selectedUser]);

  // 4. 滾到最底
  useEffect(() => {
    if (msgEndRef.current) msgEndRef.current.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // 5. 發送回覆
  const sendReply = () => {
    if (!msg.trim() || !selectedUser || !socketRef.current) return;
    socketRef.current.emit("admin_reply", {
      user_id: selectedUser.id,
      msg,
    });
    setMsg("");
  };

  // 6. 刪除聊天室
  const handleDeleteChat = async (userId) => {
    try {
      const resp = await fetch(`${REACT_APP_SOCKET_URL}/chat/history/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      if (!resp.ok) throw new Error("刪除失敗");
      antdMsg.success("刪除成功");
      fetchUsers();
      setSelectedUser(null);
      setChatHistory([]);
    } catch {
      antdMsg.error("刪除失敗");
    }
  };

  return (
    <Layout style={{ minHeight: 500, border: "1px solid #eee", borderRadius: 10 }}>
      <Sider width={260} style={{ background: "#f8f8f8", padding: 12, borderRight: "1px solid #eee" }}>
        <div style={{ fontWeight: 600, marginBottom: 10 }}>聊天室用戶</div>
        <List
          itemLayout="horizontal"
          dataSource={users}
          renderItem={user => (
            <List.Item
              style={{
                cursor: "pointer",
                background: selectedUser?.id === user.id ? "#e6f7ff" : ""
              }}
              onClick={() => setSelectedUser(user)}
              actions={[
                <Popconfirm
                  title="確定刪除此用戶所有訊息？"
                  okText="刪除"
                  cancelText="取消"
                  onConfirm={e => {
                    e.stopPropagation();
                    handleDeleteChat(user.id);
                  }}
                  onCancel={e => e.stopPropagation()}
                  onClick={e => e.stopPropagation()}
                  key="del"
                >
                  <Button
                    type="text"
                    icon={<DeleteOutlined />}
                    shape="circle"
                    danger
                    size="small"
                    style={{
                      background: "#fff",
                      border: "1.5px solid #f5222d",
                      color: "#f5222d",
                      width: 24,
                      height: 24,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "none",
                      transition: "all .18s"
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = "#fff1f0"; }}
                    onMouseLeave={e => { e.currentTarget.style.background = "#fff"; }}
                    onClick={e => e.stopPropagation()}
                  />
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                avatar={<Avatar icon={<UserOutlined />} />}
                title={<span style={{ fontWeight: 500 }}>{user.full_name || user.email || user.id}</span>}
                description={user.email}
              />
            </List.Item>
          )}
        />
      </Sider>
      <Content style={{ padding: 20 }}>
        <div style={{ minHeight: 340, maxHeight: 500, overflowY: "auto", background: "#fff", borderRadius: 6, padding: 10 }}>
          <Spin spinning={loading}>
            <List
              dataSource={chatHistory}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar style={{ background: item.from === "客服" ? "#52c41a" : "#1890ff" }}>
                        {item.from === "客服" ? "客服" : "用戶"}
                      </Avatar>
                    }
                    title={item.from}
                    description={item.msg}
                  />
                </List.Item>
              )}
            />
            <div ref={msgEndRef}></div>
          </Spin>
        </div>
        <div style={{ display: "flex", marginTop: 14 }}>
          <Input
            value={msg}
            onChange={e => setMsg(e.target.value)}
            onPressEnter={sendReply}
            placeholder="輸入回覆內容"
            disabled={!selectedUser}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={sendReply}
            disabled={!msg.trim() || !selectedUser}
            style={{ marginLeft: 8 }}
          >
            回覆
          </Button>
        </div>
      </Content>
    </Layout>
  );
}

export default AdminReply;
