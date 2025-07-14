import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db, User, Category, Order, OrderItem

@pytest.fixture(autouse=True)
def setup_category(client):
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

@pytest.fixture
def new_user(client):
    def _create_user(email, password="pw"):
        res = client.post('/auth/register', json={
            'email': email,
            'password': password
        })
        user_id = res.get_json()['user_id']
        res = client.post('/auth/login', json={'email': email, 'password': password})
        token = res.get_json()['access_token']
        return {"user_id": user_id, "token": token, "email": email}
    return _create_user

def test_get_user(client, new_user):
    user = new_user("pytest@example.com", "123456")
    res = client.get(f'/users/{user["user_id"]}', headers={'Authorization': f'Bearer {user["token"]}'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['email'] == 'pytest@example.com'

def test_update_user_info(client, new_user):
    user = new_user("patchtest@example.com")
    res = client.patch(f'/users/{user["user_id"]}',
                       json={
                           'full_name': 'Patch User',
                           'address': 'Taipei',
                           'phone': '0912345678'
                       },
                       headers={'Authorization': f'Bearer {user["token"]}'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['full_name'] == 'Patch User'
    assert data['address'] == 'Taipei'
    assert data['phone'] == '0912345678'

def test_get_all_users_admin(client, admin_token):
    # 查全部用戶
    res = client.get('/users/all', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data.get("users", []), list)
    assert any(u['email'] == 'admin@example.com' for u in data.get("users", []))

def test_recommend_for_user(client, new_user, admin_token):
    user = new_user("recomuser@example.com")
    # 管理員新增三個商品
    id_list = []
    for title in ['A', 'B', 'C']:
        r = client.post('/products',
            json={'title': title, 'price': 100, 'category_id': 1},
            headers={'Authorization': f'Bearer {admin_token}'})
        id_list.append(r.get_json()['product_id'])
        
    # 用戶下單購買 A, B
    order = Order(user_id=user["user_id"])
    db.session.add(order)
    db.session.commit()
    db.session.add_all([
        OrderItem(order_id=order.id, product_id=id_list[0], quantity=1, price=100),
        OrderItem(order_id=order.id, product_id=id_list[1], quantity=1, price=100),
    ])
    db.session.commit()

    # 呼叫推薦 API
    res = client.get(f'/users/{user["user_id"]}/recommend', headers={'Authorization': f'Bearer {user["token"]}'})
    assert res.status_code == 200
    data = res.get_json()
    assert any(item['title'] == 'C' for item in data)

def test_user_permission(client, new_user):
    user1 = new_user("user1@example.com")
    user2 = new_user("user2@example.com")
    # user2 查詢 user1 資料
    res = client.get(f'/users/{user1["user_id"]}', headers={'Authorization': f'Bearer {user2["token"]}'})
    assert res.status_code == 403
    # user2 修改 user1
    res = client.patch(f'/users/{user1["user_id"]}', json={'full_name': 'Hack'}, headers={'Authorization': f'Bearer {user2["token"]}'})
    assert res.status_code == 403

def test_user_unauthorized_access(client, new_user):
    user = new_user("unauth@example.com")
    # 沒帶 token 查詢
    res = client.get(f'/users/{user["user_id"]}')
    assert res.status_code == 401
    # 沒帶 token 修改
    res = client.patch(f'/users/{user["user_id"]}', json={'full_name': 'Nope'})
    assert res.status_code == 401

def test_get_all_users_permission(client, new_user):
    user = new_user("notadmin@example.com")
    res = client.get('/users/all', headers={'Authorization': f'Bearer {user["token"]}'})
    assert res.status_code in (401, 403)

def test_get_update_user_notfound(client, admin_token):
    # 查不存在用戶
    res = client.get('/users/999999', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 404
    # 改不存在用戶
    res = client.patch('/users/999999', json={'full_name': 'none'}, headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 404

def test_patch_user_empty_payload(client, new_user):
    user = new_user("patchblank@example.com")
    res = client.patch(f'/users/{user["user_id"]}', json={}, headers={'Authorization': f'Bearer {user["token"]}'})
    assert res.status_code in (400, 422)

def test_recommend_permission(client, new_user):
    user1 = new_user("rr1@example.com")
    user2 = new_user("rr2@example.com")
    # user2 嘗試獲得 user1 的推薦
    res = client.get(f'/users/{user1["user_id"]}/recommend', headers={'Authorization': f'Bearer {user2["token"]}'})
    assert res.status_code == 403
    # 未登入
    res = client.get(f'/users/{user1["user_id"]}/recommend')
    assert res.status_code == 401
