import pytest
from models import User, db

def test_google_login_success(client):
    """正常情況 - Google 驗證成功 & 新用戶創建"""
    resp = client.post("/auth/google", json={"credential": "fake-token"})
    data = resp.get_json()

    assert resp.status_code == 200
    assert "access_token" in data
    assert "user_id" in data
    assert data["role"] == "user"

    # 驗證 DB 有新增用戶
    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None

    assert user.email == "test@example.com"          # 來自 Google payload
    assert user.google_sub == "mock-google-sub-id"   # 來自 Google payload
    assert user.oauth_provider == "google"



    
def test_google_login_existing_user(client):
    """已存在的使用者，應該直接登入而不是重複新增"""
    # 先創建一個使用者
    user = User(email="test@example.com", password="hashed", role="user", google_sub="mock-google-sub-id")
    db.session.add(user)
    db.session.commit()

    resp = client.post("/auth/google", json={"credential": "fake-token"})
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["user_id"] == user.id

    # 驗證 DB 只有一筆
    assert User.query.filter_by(email="test@example.com").count() == 1

def test_google_login_email_not_verified(client, monkeypatch):
    """Google 驗證返回 email_verified=False，應該回 401"""
    monkeypatch.setattr(
        'service.user_service.google_id_token.verify_oauth2_token',
        lambda *a, **k: {
            "sub": "mock-google-sub-id",
            "email": "test@example.com",
            "email_verified": False,
            "name": "Test User"
        }
    )
    resp = client.post("/auth/google", json={"credential": "fake-token"})
    data = resp.get_json()

    assert resp.status_code == 401
    assert "error" in data

def test_google_login_missing_credential(client):
    """缺少 credential 應該回 400"""
    resp = client.post("/auth/google", json={})
    data = resp.get_json()

    assert resp.status_code == 400
    assert "error" in data
