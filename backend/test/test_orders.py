import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db, Category, Product

@pytest.fixture(autouse=True)
def setup_products(app):
    if not Category.query.filter_by(id=1).first():
        db.session.add(Category(id=1, name='cat1', description='for test'))
    if not Product.query.filter_by(id=1).first():
        db.session.add(Product(id=1, title='Test Product', price=100, description='desc', category_id=1, images=['img1','img2'] ))
    db.session.commit()

@pytest.fixture
def user_token_and_id(client):
    # 註冊並登入
    client.post('/auth/register', json={
        'username': 'orderuser',
        'email': 'orderuser@example.com',
        'password': '123456'
    })
    login_res = client.post('/auth/login', json={'username': 'orderuser', 'password': '123456'})
    token = login_res.get_json()['access_token']
    user_id = login_res.get_json()['user_id']
    return token, user_id

def test_order_flow(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 購物車加商品 & 結帳
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1},
                headers={'Authorization': f'Bearer {token}'})

    res = client.post(f'/carts/{user_id}/checkout',
                      json={'items': [{'product_id': 1, 'quantity': 1}]},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    order_id = res.get_json()['order_id']

    # 查詢歷史訂單
    res = client.get(f'/orders/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    result = res.get_json()
    orders = result['orders']
    assert len(orders) > 0
    order = orders[0]
    assert order['id'] == order_id


    # 查詢訂單明細
    res = client.get(f'/orders/order/{order_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    order = res.get_json()
    assert order['order_id'] == order_id
    assert order['items'][0]['product_id'] == 1

    # 修改訂單狀態
    res = client.patch(f'/orders/{order_id}/status', json={'status': 'paid'},
                       headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    # 取消訂單（應該只允許 pending 狀態時成功，這裡測試已 paid 應失敗）
    res = client.post(f'/orders/{order_id}/cancel', headers={'Authorization': f'Bearer {token}'})
    # 若已 paid 應該回 400
    assert res.status_code == 400
