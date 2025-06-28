import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db,User,Category,Order,OrderItem

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

@pytest.fixture
def new_user(client):
    def _create_user(username, email, password="pw"):
        res = client.post('/auth/register', json={
            'username': username,
            'email': email,
            'password': password
        })
        user_id = res.get_json()['user_id']
        res = client.post('/auth/login', json={'username': username, 'password': password})
        token = res.get_json()['access_token']
        return {"user_id": user_id, "token": token, "username": username, "email": email}
    return _create_user

def test_get_user(client, new_user):
    user = new_user("pytest", "pytest@example.com", "123456")
    res = client.get(f'/users/{user["user_id"]}', headers={'Authorization': f'Bearer {user["token"]}'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['username'] == 'pytest'

def test_update_user_info(client, new_user):
    user = new_user("patchtest", "patchtest@example.com")
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


def test_get_all_users_admin(client,admin_token):

    # 查全部用戶
    res = client.get('/users/all', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(u['username'] == 'admin' for u in data)

def test_recommend_for_user(client, new_user,admin_token):
    user = new_user("recomuser", "recomuser@example.com")
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
