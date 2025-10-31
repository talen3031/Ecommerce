import pytest
from ext_socketio import socketio

# ===== Fixture：註冊 & 登入會員/管理員 =====

@pytest.fixture
def user_token_and_id(client):
    # 註冊用戶
    client.post('/auth/register', json={
        'email': 'user1@Raw type',
        'password': '123456'
    })
    login_res = client.post('/auth/login', json={'email': 'user1@Raw type', 'password': '123456'})
    token = login_res.get_json()['access_token']
    user_id = login_res.get_json()['user_id']
    return token, user_id

@pytest.fixture
def admin_token_and_id(client):
    # 註冊管理員
    client.post('/auth/register', json={
        'email': 'admin@Raw type',
        'password': '123456',
        'role': 'admin'
    })
    login_res = client.post('/auth/login', json={'email': 'admin@Raw type', 'password': '123456'})
    token = login_res.get_json()['access_token']
    user_id = login_res.get_json()['user_id']
    return token, user_id

@pytest.fixture
def socketio_client(app):
    def _client(token):
        return socketio.test_client(app, flask_test_client=app.test_client(), query_string=f"token={token}")
    return _client

# ===== 測試 WebSocket 互動 =====

def test_user_send_and_auto_reply(app, user_token_and_id, socketio_client):
    token, user_id = user_token_and_id
    sio = socketio_client(token)

    # 用戶發送訊息
    sio.emit("send_message", {"token": token, "msg": "哈囉，客服在嗎？"})
    received = sio.get_received()

    # 用戶應收到自己的訊息和自動回覆
    msgs = [msg["args"][0] for msg in received if msg["name"] == "receive_message"]
    assert any("哈囉" in m["msg"] for m in msgs)
    assert any("請稍等" in m["msg"] for m in msgs)

def test_admin_reply(app, user_token_and_id, admin_token_and_id, socketio_client):
    token, user_id = user_token_and_id

    # 1. 用戶 client 先在線（連線 + 送一句話 join 房間）
    sio_user = socketio_client(token)
    sio_user.emit("send_message", {"token": token, "msg": "哈囉"})
    sio_user.get_received()  # 清掉自動回覆等訊息

    # 2. 管理員建立連線並推播
    admin_token, admin_id = admin_token_and_id
    sio_admin = socketio_client(admin_token)
    sio_admin.emit("admin_reply", {"user_id": user_id, "msg": "你好，我是客服"})
    sio_admin.get_received()

    # 3. 用戶 client 這時還是同一個，直接 get_received()
    received = sio_user.get_received()
    print("user received:", received)
    assert any("你好，我是客服" in msg['args'][0]['msg']
               for msg in received if msg['name'] == "receive_message")

# ===== 測試 REST API =====
@pytest.fixture
def chat_user_ready(client, user_token_and_id, socketio_client):
    token, user_id = user_token_and_id
    sio = socketio_client(token)
    sio.emit("send_message", {"token": token, "msg": "哈囉"})
    sio.get_received()
    return token, user_id

def test_user_chat_history(client, chat_user_ready):
    token, user_id = chat_user_ready
    resp = client.get("/chat/history", headers={"Authorization": f"Bearer {token}"})
    data = resp.get_json()
    assert isinstance(data, list)
    print(data)
    assert any("請稍等" in m["msg"] for m in data)


def test_get_chat_users(client, chat_user_ready, admin_token_and_id):
    admin_token, _ = admin_token_and_id
    resp = client.get("/chat/users", headers={"Authorization": f"Bearer {admin_token}"})
    data = resp.get_json()
    assert any(u["email"] == "user1@Raw type" for u in data)

def test_delete_user_chat_history(client, chat_user_ready, admin_token_and_id):
    admin_token, _ = admin_token_and_id
    _, user_id = chat_user_ready
    resp = client.delete(f"/chat/history/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] > 0

def test_non_admin_cannot_access_admin_api(client, user_token_and_id):
    token, user_id = user_token_and_id
    # 用戶不能查所有聊天室用戶
    resp = client.get("/chat/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403 or "error" in resp.get_json()
    # 用戶不能刪除聊天室
    resp = client.delete(f"/chat/history/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403 or "error" in resp.get_json()

