import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import { Button, Input, List, Avatar, Spin } from "antd";
import { CustomerServiceOutlined, SendOutlined } from "@ant-design/icons";
import { REACT_APP_SOCKET_URL } from "../../config";


function CustomerChat() {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(true);
  const msgEndRef = useRef();

  useEffect(() => {
    // 拉歷史紀錄
    const token = localStorage.getItem("token");
    fetch(`${REACT_APP_SOCKET_URL}/chat/history`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setMessages(data || []))
      .finally(() => setLoading(false));

    // 建立 socket.io 連線
    const sock = io(REACT_APP_SOCKET_URL, { query: { token } });
    setSocket(sock);

    // 收新訊息（統一格式: {from, msg, created_at, user_id}）
    sock.on("receive_message", data => {
      setMessages(prev => [...prev, data]);
    });

    return () => {
      sock.disconnect();
    };
  }, []);

  // 自動滾動到底
  useEffect(() => {
    if (msgEndRef.current) msgEndRef.current.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 發送訊息
  const sendMsg = () => {
    if (msg.trim() && socket) {
      socket.emit("send_message", { token: localStorage.getItem("token"), msg });
      setMsg("");
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: "40px auto", background: "#fff", borderRadius: 10, border: "1px solid #eee", padding: 18 }}>
      <h2>
        <CustomerServiceOutlined /> 客服聊天室
      </h2>
      <Spin spinning={loading}>
        <List
          dataSource={messages}
          renderItem={item => (
            <List.Item style={{ padding: "2px 0" }}>
              <List.Item.Meta
                avatar={
                  <Avatar style={{ background: item.from === "客服" ? "#52c41a" : "#1890ff" }}>
                    {item.from === "客服" ? "客服" : "我"}
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
      <div style={{ display: "flex", marginTop: 10 }}>
        <Input
          value={msg}
          onChange={e => setMsg(e.target.value)}
          onPressEnter={sendMsg}
          placeholder="請輸入訊息"
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={sendMsg}
          disabled={!msg.trim()}
          style={{ marginLeft: 8 }}
        />
      </div>
    </div>
  );
}

export default CustomerChat;
