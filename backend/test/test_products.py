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
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    # 手動升級為 admin
    user = User.query.filter_by(username='admin').first()
    user.role = 'admin'
    db.session.commit()
    # 登入拿 token
    res = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    return res.get_json()['access_token']

def test_create_get_update_delete_product(client, admin_token):
    # --- 新增商品 ---
    res = client.post('/products/add', 
                      json={
                          'title': 'iPhone 99',
                          'price': 9999,
                          'description': 'The best phone',
                          'category_id': 1,
                          'image': 'http://image'
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
    res = client.put(f'/products/update/{product_id}',
                     json={
                         'title': 'iPhone 99 Pro',
                         'price': 19999,
                         'description': 'Updated phone',
                         'category_id': 1,
                         'image': 'http://image_new'
                     },
                     headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查詢驗證
    res = client.get(f'/products/{product_id}')
    assert res.get_json()['title'] == 'iPhone 99 Pro'

    # --- 刪除商品 ---
    res = client.delete(f'/products/delete/{product_id}',
                        headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    # 查驗證已刪除
    res = client.get(f'/products/{product_id}')
    assert res.status_code == 404

def test_create_product_permission(client):
    # 沒帶 token 無法新增商品
    res = client.post('/products/add', 
                      json={'title': 'nope', 'price': 1, 'category_id': 1})
    assert res.status_code == 401  # 未授權

def test_update_delete_permission(client, admin_token):
    # 先新增一個商品
    res = client.post('/products/add', 
                      json={'title': 'temp', 'price': 1, 'category_id': 1},
                      headers={'Authorization': f'Bearer {admin_token}'})
    product_id = res.get_json()['product_id']

    # 不帶 token 不能改
    res = client.put(f'/products/update/{product_id}',
                     json={'title': 'hack', 'price': 1, 'category_id': 1})
    assert res.status_code == 401

    # 不帶 token 不能刪
    res = client.delete(f'/products/delete/{product_id}')
    assert res.status_code == 401
