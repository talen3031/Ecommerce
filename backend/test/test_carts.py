import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import Product, db, Order, OrderItem,Category,User
from datetime import datetime

@pytest.fixture(autouse=True)
def setup_products(app):
    # 建立預設分類和商品，確保有 id=1
    if not Category.query.filter_by(id=1).first():
        db.session.add(Category(id=1, name='cat1', description='for test'))
    db.session.add(Product(title='Test Product', price=100, description='desc', category_id=1, images=['img1','img2']))
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

@pytest.fixture
def discount_code():
    from models import DiscountCode
    code = "TESTCODE"
    dc = DiscountCode(
        code=code,
        discount=0.8,        # 8折
        amount=None,         # 固定金額折抵測試時可改成100
        product_id=None,     # 全品項可用
        min_spend=100,       # 滿百可用
        valid_from=datetime(2000, 1, 1),
        valid_to=datetime(2099, 12, 31),
        usage_limit=10,
        per_user_limit=2,
        description="測試折扣碼",
        is_active=True
    )
    db.session.add(dc)
    db.session.commit()
    return dc

def test_cart_crud_flow(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 查詢空購物車
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    assert res.get_json()['items'] == []

    # 加商品到購物車
    res = client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 2},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    cart_id = res.get_json()['cart_id']

    # 查詢購物車內容
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    items = res.get_json()['items']
    assert len(items) == 1 and items[0]['product_id'] == 1 and items[0]['quantity'] == 2

    # 調整購物車商品數量
    res = client.put(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 5},
                     headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.get_json()['items'][0]['quantity'] == 5

    # 刪除購物車商品
    res = client.delete(f'/carts/{user_id}', json={'product_id': 1},
                        headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.get_json()['items'] == []

def test_cart_checkout(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 先加商品
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 2},
                headers={'Authorization': f'Bearer {token}'})

    # 結帳前 印出購物車內容
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("Checkout 前購物車：", res.status_code, res.get_json())

    # 正常結帳
    res = client.post(f'/carts/{user_id}/checkout',
                      json={'items': [{'product_id': 1, 'quantity': 2}]},
                      headers={'Authorization': f'Bearer {token}'})
    print("Checkout resp：", res.status_code, res.get_json())
    assert res.status_code == 200
    assert 'order_id' in res.get_json()

    # 再查購物車，應該已空
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("Checkout 後購物車：", res.status_code, res.get_json())
    assert res.get_json()['items'] == []

def test_cart_content_recommend(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 建立新商品同分類，並假設 p2 熱賣（有訂單數紀錄）
    hot_title = f'Hot Product for user {user_id}'
    p2 = Product(title=hot_title, price = 200, description='Hot', category_id=1, images=['img2-1','img2-2'])
    db.session.add(p2)
    db.session.commit()
    
    # 先創建一個假用戶
    user_1 = User(username=f'fakeuser_{user_id}', email=f'fake{user_id}@example.com', password='pw')
    db.session.add(user_1)
    db.session.commit()

    # 幫別的用戶下訂單，模擬熱賣
    order = Order(user_id = user_1.id) 
    db.session.add(order)
    db.session.commit()
    db.session.add(OrderItem(order_id=order.id, product_id=p2.id, quantity=5, price=200))
    db.session.commit()

    # cartuser 加入原有商品到購物車
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1},
                headers={'Authorization': f'Bearer {token}'})

    # 呼叫推薦（應該推薦 p2，因為是同分類又熱賣）
    res = client.get(f'/carts/{user_id}/recommend', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.get_json()
    # 應該包含 hot_title
    assert any(p['title'] == hot_title for p in data)

def test_cart_collaborative_recommend(client, user_token_and_id):
    token, user_id = user_token_and_id

    # 建立唯一名稱商品
    collab_title = f'Collab_Product for user {user_id}'
    p3 = Product(title=collab_title, price=300, description='collab', category_id=1, images=['img3-1','img3-2'])
    db.session.add(p3)
    db.session.commit()

    # 新增一個用戶 user2 並讓他買過 cartuser 的商品與 p3
    user2 = User(username=f'collabuser_{user_id}', email=f'collab{user_id}@example.com', password='pw')
    db.session.add(user2)
    db.session.commit()


    order2 = Order(user_id=user2.id)
    db.session.add(order2)
    db.session.commit()
    db.session.add_all([
        OrderItem(order_id=order2.id, product_id=1, quantity=1, price=100),   # 與 cartuser 購物車重複
        OrderItem(order_id=order2.id, product_id=p3.id, quantity=2, price=300)  # collab product
    ])
    db.session.commit()

    # cartuser 加入原有商品到購物車
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1},
                headers={'Authorization': f'Bearer {token}'})

    # 呼叫協同過濾推薦（應該推薦 p3，因為有共同買過商品）
    res = client.get(f'/carts/{user_id}/recommend/collaborative', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert any(p['title'] == collab_title for p in data)
def test_discount_code_checkout_flow(client, user_token_and_id, discount_code):
    token, user_id = user_token_and_id

    # 1. 先加商品到購物車
    res = client.post(
        f'/carts/{user_id}', 
        json={'product_id': 1, 'quantity': 2},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert res.status_code == 200

    # 2. 前端在購物車頁輸入折扣碼查詢折扣後金額
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("折扣碼流程前購物車：", res.status_code, res.get_json())

    res = client.post(
        f'/carts/{user_id}/apply_discount', 
        json={'code': discount_code.code},
        headers={'Authorization': f'Bearer {token}'}
    )
    print("套用折扣碼 resp:", res.status_code, res.get_json())
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["discounted_total"] == 160
    assert data["discount_amount"] == 40

    # 3. 直接用折扣碼結帳
    res = client.post(
        f'/carts/{user_id}/checkout',
        json={
            'items': [{'product_id': 1, 'quantity': 2}],
            'discount_code': discount_code.code
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    print("折扣碼 checkout resp:", res.status_code, res.get_json())
    assert res.status_code == 200
    result = res.get_json()
    assert result["discount_code"] == discount_code.code
    assert result["total"] == 160
    assert result["discount_amount"] == 40
    assert "order_id" in result

    # 4. 再查一次購物車，應為空
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("折扣碼 checkout 後購物車：", res.status_code, res.get_json())
    assert res.get_json()['items'] == []
