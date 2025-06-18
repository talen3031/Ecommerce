import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,User,Category

def test_get_user(client):
    # 先註冊
    res = client.post('/auth/register', json={
        'username': 'pytest',
        'email': 'pytest@example.com',
        'password': '123456'
    })
    user_id = res.get_json()['user_id']
    # 登入拿 token
    res = client.post('/auth/login', json={
        'username': 'pytest',
        'password': '123456'
    })
    token = res.get_json()['access_token']
    # 查詢個人資訊
    res = client.get(f'/users/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    data = res.get_json()
    assert data['username'] == 'pytest'
