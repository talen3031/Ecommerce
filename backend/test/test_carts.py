import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,Category,Product


@pytest.fixture(autouse=True)
def setup_products(app):
    # 建立預設分類和商品，確保有 id=1
    if not Category.query.filter_by(id=1).first():
        db.session.add(Category(id=1, name='cat1', description='for test'))
    if not Product.query.filter_by(id=1).first():
        db.session.add(Product(id=1, title='Test Product', price=100, description='desc', category_id=1, image='img'))
    db.session.commit()

@pytest.fixture
def user_token_and_id(client):
    # 註冊並登入
    client.post('/auth/register', json={
        'username': 'cartuser',
        'email': 'cartuser@example.com',
        'password': '123456'
    })
    login_res = client.post('/auth/login', json={'username': 'cartuser', 'password': '123456'})
    token = login_res.get_json()['access_token']
    user_id = login_res.get_json()['user_id']
    return token, user_id

def test_cart_crud_flow(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 查詢空購物車
    res = client.get(f'/cart/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert res.get_json()['items'] == []

    # 加商品到購物車
    res = client.post(f'/cart/{user_id}/add', json={'product_id': 1, 'quantity': 2},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    cart_id = res.get_json()['cart_id']

    # 查詢購物車內容
    res = client.get(f'/cart/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    items = res.get_json()['items']
    assert len(items) == 1 and items[0]['product_id'] == 1 and items[0]['quantity'] == 2

    # 調整購物車商品數量
    res = client.put(f'/cart/{user_id}/update', json={'product_id': 1, 'quantity': 5},
                     headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    res = client.get(f'/cart/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.get_json()['items'][0]['quantity'] == 5

    # 刪除購物車商品
    res = client.delete(f'/cart/{user_id}/remove', json={'product_id': 1},
                        headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    res = client.get(f'/cart/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.get_json()['items'] == []

def test_cart_checkout(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 先加商品
    client.post(f'/cart/{user_id}/add', json={'product_id': 1, 'quantity': 2},
                headers={'Authorization': f'Bearer {token}'})

    # 正常結帳
    res = client.post(f'/cart/{user_id}/checkout',
                      json={'items': [{'product_id': 1, 'quantity': 2}]},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert 'order_id' in res.get_json()

    # 再查購物車，應該已空（或 checked_out 狀態）
    res = client.get(f'/cart/{user_id}', headers={'Authorization': f'Bearer {token}'})
    # checked_out後 items應該是空的
    assert res.get_json()['items'] == []
