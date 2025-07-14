import pytest
import sys
import os
from datetime import datetime, timedelta

# 最優先去指定的資料(專案根目錄下) 來 import 程式檔案 app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db, User, PasswordResetToken

def test_register_and_login(client):
    # 註冊只用 email
    res = client.post('/auth/register', json={
        'email': 'testuser@example.com',
        'password': '123456'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'user_id' in data

    # 測試登入
    res = client.post('/auth/login', json={
        'email': 'testuser@example.com',
        'password': '123456'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data

def test_forgot_password_send_link(client):
    # 先創一個用戶
    user = User(email='reset@example.com', password='hashedpw')
    db.session.add(user)
    db.session.commit()

    # 呼叫 API
    res = client.post('/auth/forgot_password', json={'email': 'reset@example.com'})
    assert res.status_code == 200
    # 不論存在與否都應同樣訊息
    assert 'reset link' in res.get_json()['message']
    
    # 在 PasswordResetToken 資料庫有新 token
    token = PasswordResetToken.get_user_newest_token(user_id=user.id)
    assert token is not None
    assert token.used is False

def test_forgot_password_nonexist_email(client):
    res = client.post('/auth/forgot_password', json={'email': 'notexist@example.com'})
    assert res.status_code == 200
    # 應該不會暴露資訊
    assert 'reset link' in res.get_json()['message']

def test_reset_password_success(client):
    # 建立用戶+token
    user = User(email='reset2@example.com', password='hashedpw2')
    db.session.add(user)
    db.session.commit()
    
    # 建立有效 token
    token = PasswordResetToken(
        user_id=user.id,
        token='X7sWa1oIczo3UMRGODmTULD19KZZojZYCQuVJLRfBrQ',
        expire_at=datetime.now() + timedelta(hours=1),
        used=False
    )
    db.session.add(token)
    db.session.commit()

    # 呼叫 API 重設
    res = client.post('/auth/reset_password', json={
        'token': 'X7sWa1oIczo3UMRGODmTULD19KZZojZYCQuVJLRfBrQ',
        'new_password': 'newpw123'
    })
    assert res.status_code == 200
    assert 'has been reset' in res.get_json()['message']

    # 驗證 token 已失效
    db.session.refresh(token)
    assert token.used is True
    
    # 測試用 reset password 登入
    res = client.post('/auth/login', json={
        'email': 'reset2@example.com',
        'password': 'newpw123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data

def test_reset_password_invalid_token(client):
    # 測不存在或過期 token
    res = client.post('/auth/reset_password', json={
        'token': 'badtoken',
        'new_password': 'anypw'
    })
    assert res.status_code == 400
    assert 'invalid or expired' in res.get_json()['error']
def test_register_duplicate_email(client):
    # 首次註冊
    res = client.post('/auth/register', json={'email': 'dup@example.com', 'password': 'pw123'})
    assert res.status_code == 201
    # 重複註冊
    res = client.post('/auth/register', json={'email': 'dup@example.com', 'password': 'pw123'})
    assert res.status_code == 409

def test_login_fail(client):
    # 未註冊帳號
    res = client.post('/auth/login', json={'email': 'notexist@example.com', 'password': 'pw'})
    assert res.status_code == 401
    # 密碼錯誤
    client.post('/auth/register', json={'email': 'wrongpw@example.com', 'password': 'pw'})
    res = client.post('/auth/login', json={'email': 'wrongpw@example.com', 'password': 'wrong'})
    assert res.status_code == 401

def test_register_invalid_payload(client):
    # 缺欄位
    res = client.post('/auth/register', json={'email': 'no_pw@example.com'})
    assert res.status_code == 400
    res = client.post('/auth/register', json={'password': 'noemail'})
    assert res.status_code == 400

def test_forgot_password_invalid_email_format(client):
    res = client.post('/auth/forgot_password', json={'email': 'not-an-email'})
    assert res.status_code == 200  # 通常系統為安全設計還是會回 200

def test_reset_password_missing_fields(client):
    # 缺新密碼
    res = client.post('/auth/reset_password', json={'token': 'tokenonly'})
    assert res.status_code == 400
    # 缺 token
    res = client.post('/auth/reset_password', json={'new_password': 'xxx'})
    assert res.status_code == 400

def test_reset_password_expired_token(client):
    from models import User, PasswordResetToken
    from datetime import datetime, timedelta
    
    user = User(email='expire@example.com', password='pw')
    db.session.add(user)
    db.session.commit()
    token = PasswordResetToken(
        user_id=user.id,
        token='expiredtoken',
        expire_at=datetime.now() - timedelta(hours=1),# 建立過期 token
        used=False
    )
    db.session.add(token)
    db.session.commit()
    res = client.post('/auth/reset_password', json={'token': 'expiredtoken', 'new_password': 'newpw'})
    assert res.status_code == 400
    assert 'invalid or expired' in res.get_json()['error']
