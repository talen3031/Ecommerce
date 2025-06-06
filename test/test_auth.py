import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,User,Category

def test_register_and_login(client):
    # 測試註冊
    res = client.post('/register', json={
        'username': 'pytest',
        'email': 'pytest@example.com',
        'password': '123456'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'user_id' in data

    # 測試登入
    res = client.post('/login', json={
        'username': 'pytest',
        'password': '123456'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data
