import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def admin_token(client):
    # 註冊管理員
    client.post('/auth/register', json={
        'email': 'admin@example.com',
        'password': '123456',
        'role': 'admin'
    })
    res = client.post('/auth/login', json={'email': 'admin@example.com', 'password': '123456'})
    token = res.get_json()['access_token']
    return token

def test_post_discount_codes(client, admin_token):
    url = '/discount_codes/'

    # 基本成功案例
    body = {
        "code": "NEWCODE",
        "discount": 0.9,
        "amount": None,
        "product_id": None,
        "min_spend": 100,
        "valid_from": "2024-01-01T00:00:00",
        "valid_to": "2099-12-31T23:59:59",
        "usage_limit": 5,
        "per_user_limit": 1,
        "description": "測試新增"
    }
    res = client.post(url, json=body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 201
    data = res.get_json()
    assert data['code'] == "NEWCODE"
    assert data['discount'] == 0.9

    # 重複折扣碼
    res = client.post(url, json=body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
    assert '已存在' in res.get_json()['error']

    # discount 與 amount 同時給，應該錯誤
    body2 = body.copy()
    body2['code'] = "NEWCODE2"
    body2['amount'] = 100
    res = client.post(url, json=body2, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
    assert '二擇一' in res.get_json()['error']

    # 少必填欄位
    res = client.post(url, json={"code": "NOFIELD"}, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
    assert '缺少必填欄位' in res.get_json()['error']
def test_admin_can_query_discount_codes(client, admin_token):
    # 先新增一個折扣碼
    post_body = {
        "code": "QUERYCODE",
        "discount": 0.9,
        "amount": None,
        "product_id": None,
        "min_spend": 100,
        "valid_from": "2024-01-01T00:00:00",
        "valid_to": "2099-12-31T23:59:59",
        "usage_limit": 5,
        "per_user_limit": 1,
        "description": "查詢測試"
    }
    res = client.post('/discount_codes/', json=post_body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 201
    code_id = res.get_json()['id']

    # 查詢所有折扣碼
    res = client.get('/discount_codes/', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert any(dc['code'] == "QUERYCODE" for dc in data)
def test_admin_can_deactivate_discount_code(client, admin_token):
    # 新增一個折扣碼
    post_body = {
        "code": "DEACTIVECODE",
        "discount": 0.8,
        "amount": None,
        "product_id": None,
        "min_spend": 50,
        "valid_from": "2024-01-01T00:00:00",
        "valid_to": "2099-12-31T23:59:59",
        "usage_limit": 5,
        "per_user_limit": 1,
        "description": "停用測試"
    }
    res = client.post('/discount_codes/', json=post_body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 201
    code_id = res.get_json()['id']

    # 停用該折扣碼
    res = client.patch(f'/discount_codes/{code_id}/deactivate', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    result = res.get_json()
    assert result['is_active'] is False

    # 再查詢該折扣碼，確認 is_active=False
    res = client.get('/discount_codes/', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    dc_list = res.get_json()
    dc = next((d for d in dc_list if d['id'] == code_id), None)
    assert dc is not None
    assert dc['is_active'] is False

def test_non_admin_cannot_manage_discount_codes(client):
    # 沒有 token 新增
    res = client.post('/discount_codes/', json={"code": "XXX", "discount": 0.9, "amount": None, "product_id": None,
                                                "min_spend": 0, "valid_from": "2024-01-01T00:00:00",
                                                "valid_to": "2099-12-31T23:59:59", "usage_limit": 1, "per_user_limit": 1, "description": ""})
    assert res.status_code in (401, 403)
    # 非 admin
    client.post('/auth/register', json={'email': 'user@example.com', 'password': 'pw'})
    login_res = client.post('/auth/login', json={'email': 'user@example.com', 'password': 'pw'})
    token = login_res.get_json()['access_token']
    res = client.post('/discount_codes/', json={"code": "YYY", "discount": 0.9, "amount": None, "product_id": None,
                                                "min_spend": 0, "valid_from": "2024-01-01T00:00:00",
                                                "valid_to": "2099-12-31T23:59:59", "usage_limit": 1, "per_user_limit": 1, "description": ""},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code in (401, 403)
    # 查詢也應拒絕
    res = client.get('/discount_codes/', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code in (401, 403)

def test_deactivate_nonexistent_discount_code(client, admin_token):
    res = client.patch('/discount_codes/999999/deactivate', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 404

def test_post_discount_code_invalid_data(client, admin_token):
    # 折扣寫成文字
    body = {
        "code": "BADTYPE",
        "discount": "not_a_number",
        "amount": None,
        "product_id": None,
        "min_spend": 100,
        "valid_from": "2024-01-01T00:00:00",
        "valid_to": "2099-12-31T23:59:59",
        "usage_limit": 5,
        "per_user_limit": 1,
        "description": ""
    }
    res = client.post('/discount_codes/', json=body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
    # 日期格式錯誤
    body["discount"] = 0.8
    body["valid_from"] = "bad-date"
    res = client.post('/discount_codes/', json=body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
