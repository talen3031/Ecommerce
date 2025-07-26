import pytest
import sys
import os
from datetime import datetime, timedelta

# 最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
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
def shipping_info():
    return {
        "shipping_method": "711",
        "recipient_name": "測試用戶",
        "recipient_phone": "0912345678",
        "recipient_email": "pytest@example.com",  # 這裡一定要和查詢用一致
        "store_name": "7-11 測試店"
    }

@pytest.fixture
def user_token_and_id(client):
    # 註冊並登入
    client.post('/auth/register', json={
        'email': 'cartuser@example.com',
        'password': '123456'
    })
    login_res = client.post('/auth/login', json={'email': 'cartuser@example.com', 'password': '123456'})
    token = login_res.get_json()['access_token']
    user_id = login_res.get_json()['user_id']
    return token, user_id

@pytest.fixture
def guest_order(client, shipping_info):
    guest_id = "pytest_guest_1"
    guest_email = shipping_info["recipient_email"]  # 一定要用 recipient_email

    client.post(f"/carts/guest/{guest_id}", json={"product_id": 1, "quantity": 1})
    resp = client.post(
        f"/carts/guest/{guest_id}/checkout",
        json={
            "items": [{"product_id": 1, "quantity": 1}],
            "shipping_info": shipping_info
        }
    )
    assert resp.status_code == 200
    order_id = resp.json["order_id"]
    return {"guest_id": guest_id, "guest_email": guest_email, "order_id": order_id}

def admin_token(client):
    client.post('/auth/register', json={'email': 'admin@example.com', 'password': 'adminpw', 'role': 'admin'})
    login_res = client.post('/auth/login', json={'email': 'admin@example.com', 'password': 'adminpw'})
    return login_res.get_json()['access_token']

def test_order_flow(client, user_token_and_id,shipping_info):
    token, user_id = user_token_and_id

    # 購物車加商品 & 結帳
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1},
                headers={'Authorization': f'Bearer {token}'})

    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("下單前購物車：", res.status_code, res.get_json())

    res = client.post(
        f'/carts/{user_id}/checkout',
        json={
            'items': [{'product_id': 1, 'quantity': 1}],
            'shipping_info': shipping_info
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200
    order_id = res.get_json()['order_id']

    # 查詢歷史訂單（修正路徑，不要帶 user_id）
    res = client.get(f'/orders', headers={'Authorization': f'Bearer {token}'})
    print("查詢訂單 resp：", res.status_code, res.get_json())
    assert res.status_code == 200
    result = res.get_json()
    orders = result['orders']
    assert len(orders) > 0
    order = orders[0]
    assert order['id'] == order_id

    # 查詢訂單明細（修正為 /orders/<order_id>）
    res = client.get(f'/orders/{order_id}', headers={'Authorization': f'Bearer {token}'})
    print("查詢訂單明細 resp：", res.status_code, res.get_json())
    assert res.status_code == 200
    order_detail = res.get_json()
    assert order_detail['order_id'] == order_id
    assert order_detail['items'][0]['product_id'] == 1

    # 修改訂單狀態
    res = client.patch(f'/orders/{order_id}/status', json={'status': 'shipped'},
                       headers={'Authorization': f'Bearer {token}'})
    print("改訂單狀態 resp：", res.status_code, res.get_json())
    assert res.status_code == 200

    # 取消訂單（已出貨不可取消，會回 400）
    res = client.post(f'/orders/{order_id}/cancel', headers={'Authorization': f'Bearer {token}'})
    print("取消訂單 resp：", res.status_code, res.get_json())
    assert res.status_code == 400

def test_get_all_orders_as_admin(client, user_token_and_id,shipping_info):
    token, user_id = user_token_and_id
    
    # 加入購物車並結帳
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    client.post(
    f'/carts/{user_id}/checkout',
    json={
        'items': [{'product_id': 1, 'quantity': 1}],
        'shipping_info': shipping_info
    },
    headers={'Authorization': f'Bearer {token}'}
    )

    # 用 admin 查詢
    admin_tok = admin_token(client)
    res = client.get('/orders/all', headers={'Authorization': f'Bearer {admin_tok}'})
    print("管理員查詢所有訂單：", res.status_code, res.get_json())
    assert res.status_code == 200
    assert res.get_json()['total'] >= 1

def test_update_order_status_error(client, user_token_and_id,shipping_info):
    token, user_id = user_token_and_id
    # 下訂單
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    res = client.post(
        f'/carts/{user_id}/checkout',
        json={
            'items': [{'product_id': 1, 'quantity': 1}],
            'shipping_info': shipping_info
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    
    order_id = res.get_json()['order_id']
    # 設定錯誤狀態
    res = client.patch(f'/orders/{order_id}/status', json={'status': 'WRONG'}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 400
    # 設定一樣的狀態
    res = client.patch(f'/orders/{order_id}/status', json={'status': 'pending'}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 400

def test_cancel_order_wrong_status(client, user_token_and_id,shipping_info):
    token, user_id = user_token_and_id
    # 下訂單並設已付款
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    res = client.post(
    f'/carts/{user_id}/checkout',
    json={
        'items': [{'product_id': 1, 'quantity': 1}],
        'shipping_info': shipping_info
    },
    headers={'Authorization': f'Bearer {token}'}
)
    order_id = res.get_json()['order_id']
    client.patch(f'/orders/{order_id}/status', json={'status': 'shipped'}, headers={'Authorization': f'Bearer {token}'})
    # 這時再取消
    res = client.post(f'/orders/{order_id}/cancel', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 400

def test_get_order_detail_404(client, user_token_and_id):
    token, _ = user_token_and_id
    # 查一個不存在的 order_id（修正為 /orders/<order_id>）
    res = client.get(f'/orders/9999999999', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 404

def test_cancel_order_404(client, user_token_and_id):
    token, _ = user_token_and_id
    res = client.post(f'/orders/999999/cancel', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 404
#===============================guest order test===============================================
def test_guest_get_order_detail_success(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}?email={guest_order['guest_email']}"
    resp = client.get(url)
    print("查詢 guest 訂單:", resp.status_code, resp.get_json())
    assert resp.status_code == 200
    detail = resp.get_json()
    assert detail["order_id"] == guest_order["order_id"]

def test_guest_get_order_detail_wrong_email(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}?email=wrong@example.com"
    resp = client.get(url)
    assert resp.status_code in (404, 400)

def test_guest_get_order_detail_missing_email(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}"
    resp = client.get(url)
    assert resp.status_code == 400

def test_guest_cancel_order_success(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}/cancel"
    resp = client.post(url, json={"email": guest_order["guest_email"]})
    print("取消 guest 訂單:", resp.status_code, resp.get_json())
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Order cancelled"

def test_guest_cancel_order_wrong_email(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}/cancel"
    resp = client.post(url, json={"email": "wrong@email.com"})
    assert resp.status_code in (404, 400)

def test_guest_cancel_order_missing_email(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}/cancel"
    resp = client.post(url, json={})
    assert resp.status_code == 400

def test_guest_cancel_order_twice(client, guest_order):
    url = f"/orders/guest/{guest_order['guest_id']}/{guest_order['order_id']}/cancel"
    # 第一次取消
    resp1 = client.post(url, json={"email": guest_order["guest_email"]})
    assert resp1.status_code == 200
    # 第二次應該不能再取消
    resp2 = client.post(url, json={"email": guest_order["guest_email"]})
    assert resp2.status_code in (400, 404)