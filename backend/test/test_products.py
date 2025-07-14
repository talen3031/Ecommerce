import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,User,Category


@pytest.fixture(autouse=True)
def setup_category(app):
    # 若已存在 category_id=1 就不需重複插入
    if not Category.query.filter_by(id=1).first():
        db.session.add(Category(id=1, name='default', description='for test'))
        db.session.commit()

@pytest.fixture
def admin_token(client):
    # 註冊管理員帳號
    res = client.post('/auth/register', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    # 手動升級為 admin
    user = User.query.filter_by(email='admin@example.com').first()
    user.role = 'admin'
    db.session.commit()
    # 登入拿 token
    res = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    return res.get_json()['access_token']

def test_create_get_update_delete_product(client, admin_token):
    # --- 新增商品 ---
    res = client.post('/products', 
                      json={
                          'title': 'iPhone 99',
                          'price': 9999,
                          'description': 'The best phone',
                          'category_id': 1,
                          'images': ['http://image1','http://image2']
                      },
                      headers={'Authorization': f'Bearer {admin_token}'})
    
    
    assert res.status_code == 200
    product_id = res.get_json()['product_id']

    # --- 查單一商品 ---
    res = client.get(f'/products/{product_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['title'] == 'iPhone 99'
    assert data['price'] == 9999

    # --- 查詢全部商品 ---
    res = client.get('/products')
    assert res.status_code == 200
    res = res.get_json()
    products = res['products']
    for p in products:
        assert p['id'] == product_id

    # --- 修改商品 ---
    res = client.put(f'/products/{product_id}',
                     json={
                         'title': 'iPhone 99 Pro',
                         'price': 19999,
                         'description': 'Updated phone',
                         'category_id': 1,
                         'images': ['http://image_new1','http://image_new2']
                     },
                     headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查詢驗證
    res = client.get(f'/products/{product_id}')
    assert res.get_json()['title'] == 'iPhone 99 Pro'

    # --- 刪除商品 ---
    res = client.delete(f'/products/{product_id}',
                        headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查驗證已刪除
    res = client.get(f'/products/{product_id}')
    assert res.status_code == 404

def test_create_product_permission(client):
    # 沒帶 token 無法新增商品
    res = client.post('/products', 
                      json={'title': 'nope', 'price': 1, 'category_id': 1})
    assert res.status_code == 401  # 未授權

def test_update_delete_permission(client, admin_token):
    # 先新增一個商品
    res = client.post('/products', 
                      json={'title': 'temp', 'price': 1, 'category_id': 1},
                      headers={'Authorization': f'Bearer {admin_token}'})
    product_id = res.get_json()['product_id']

    # 不帶 token 不能改
    res = client.put(f'/products/{product_id}',
                     json={'title': 'hack', 'price': 1, 'category_id': 1})
    assert res.status_code == 401

    # 不帶 token 不能刪
    res = client.delete(f'/products/{product_id}')
    assert res.status_code == 401

def test_product_list_filter_and_pagination(client, admin_token):
    # 新增多個商品
    for i in range(5):
        client.post('/products',
            json={'title': f'Prod{i}', 'price': 100+i*10, 'category_id': 1, 'images': []},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
    # 用關鍵字查詢
    res = client.get('/products?keyword=Prod1')
    assert res.status_code == 200
    data = res.get_json()
    assert any('Prod1' in p['title'] for p in data['products'])
    # 用價格範圍查
    res = client.get('/products?min_price=110&max_price=120')
    prods = res.get_json()['products']
    assert all(110 <= p['price'] <= 120 for p in prods)
    # 測分頁
    res = client.get('/products?page=2&per_page=2')
    data = res.get_json()
    assert data['page'] == 2 and data['per_page'] == 2

def test_admin_products_api(client, admin_token):
    res = client.get('/products/admin', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 非 admin 不能查
    res = client.get('/products/admin')
    assert res.status_code == 401 or res.status_code == 403

def test_activate_deactivate_product(client, admin_token):
    # 新增商品
    res = client.post('/products', json={'title':'T1','price':1,'category_id':1,'images':[]}, headers={'Authorization': f'Bearer {admin_token}'})
    pid = res.get_json()['product_id']
    # 下架
    res = client.post(f'/products/{pid}/deactivate', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查詢應該查不到（前台查詢）
    res = client.get('/products')
    assert not any(p['id'] == pid for p in res.get_json()['products'])
    # 上架
    res = client.post(f'/products/{pid}/activate', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查詢應該查得到
    res = client.get('/products')
    assert any(p['id'] == pid for p in res.get_json()['products'])

    #商品上下架權限與狀態驗證
def test_activate_deactivate_product(client, admin_token):
    # 新增商品
    res = client.post('/products', json={'title':'T1','price':1,'category_id':1,'images':[]}, headers={'Authorization': f'Bearer {admin_token}'})
    pid = res.get_json()['product_id']
    # 下架
    res = client.post(f'/products/{pid}/deactivate', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查詢應該查不到（前台查詢只會回 active 商品）
    res = client.get('/products')
    assert not any(p['id'] == pid for p in res.get_json()['products'])
    # 上架
    res = client.post(f'/products/{pid}/activate', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查詢應該查得到
    res = client.get('/products')
    assert any(p['id'] == pid for p in res.get_json()['products'])

def test_deactivate_activate_permission(client, admin_token):
    # 先新增商品
    res = client.post('/products', json={'title':'PTest','price':10,'category_id':1,'images':[]}, headers={'Authorization': f'Bearer {admin_token}'})
    pid = res.get_json()['product_id']
    # 未登入不能上下架
    res = client.post(f'/products/{pid}/deactivate')
    assert res.status_code in (401, 403)
    res = client.post(f'/products/{pid}/activate')
    assert res.status_code in (401, 403)

#新增/修改商品時的異常處理
def test_create_product_missing_fields(client, admin_token):
    # 少 title
    res = client.post('/products', json={'price': 10, 'category_id': 1, 'images': []}, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
    # 少 price
    res = client.post('/products', json={'title': 'x', 'category_id': 1, 'images': []}, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
    # 少 category_id
    res = client.post('/products', json={'title': 'x', 'price': 1, 'images': []}, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 400
def test_get_delete_nonexistent_product(client, admin_token):
    # 查詢不存在
    res = client.get('/products/999999')
    assert res.status_code == 404
    # 刪除不存在
    res = client.delete('/products/999999', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 404
    # 修改不存在商品
    res = client.put('/products/999999', json={'title': 'x', 'price': 1, 'category_id': 1, 'images': []}, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 404

    
#商品特價 API 權限與資料驗證
def test_product_sale_admin_permission(client, admin_token):
    # 新增商品
    res = client.post('/products', json={'title':'TSale','price':100,'category_id':1,'images':[]}, headers={'Authorization': f'Bearer {admin_token}'})
    pid = res.get_json()['product_id']
    # 設定特價
    sale_body = {
        "discount": 0.8,
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59",
        "description": "Summer Sale"
    }
    res = client.post(f'/products/sale/{pid}', json=sale_body, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 非 admin 不可設定特價
    res = client.post(f'/products/sale/{pid}', json=sale_body)
    assert res.status_code in (401, 403)
