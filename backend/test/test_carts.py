import pytest
import sys
import os
#最優先去指定的資料(專案根目錄下) 來imprt程式檔案app.py。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import Product, db, Order, OrderItem,Category,User
from datetime import datetime
import uuid
import pytest


@pytest.fixture(autouse=True)
def setup_products(app):
    # 建立預設分類和商品，確保有 id=1
    if not Category.query.filter_by(id=1).first():
        db.session.add(Category(id=1, name='cat1', description='for test'))
    db.session.add(Product(title='Test Product', price=100, description='desc', category_id=1, images=['img1','img2']))
    db.session.commit()

@pytest.fixture
def guest_id():
    # 模擬一組訪客 id (uuid 字串)
    return str(uuid.uuid4())
@pytest.fixture
def shipping_info():
    return {
        "shipping_method": "711",
        "recipient_name": "測試用戶",
        "recipient_phone": "0912345678",
        "recipient_email": "user1@mail.com",
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

def test_cart_checkout(client, user_token_and_id,shipping_info):
    token, user_id = user_token_and_id

    # 先加商品
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 2},
                headers={'Authorization': f'Bearer {token}'})

    # 結帳前 印出購物車內容
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("Checkout 前購物車：", res.status_code, res.get_json())

    # 正常結帳
    res = client.post(f'/carts/{user_id}/checkout',
                       json={
                            'items': [{'product_id': 1, 'quantity': 2}],
                            'shipping_info':shipping_info
                        },headers={'Authorization': f'Bearer {token}'})
    print("Checkout resp：", res.status_code, res.get_json())
    assert res.status_code == 200
    assert 'order_id' in res.get_json()

    # 再查購物車，應該已空
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    print("Checkout 後購物車：", res.status_code, res.get_json())
    assert res.get_json()['items'] == []

def test_cart_content_recommend(client, user_token_and_id):
    token, user_id = user_token_and_id
    hot_title = f'Hot Product for user {user_id}'
    p2 = Product(title=hot_title, price=200, description='Hot', category_id=1, images=['img2-1', 'img2-2'])
    db.session.add(p2)
    db.session.commit()
    
    # 改：假用戶不再有 username
    user_1 = User(email=f'fake{user_id}@example.com', password='pw')
    db.session.add(user_1)
    db.session.commit()

    order = Order(user_id=user_1.id)
    db.session.add(order)
    db.session.commit()
    db.session.add(OrderItem(order_id=order.id, product_id=p2.id, quantity=5, price=200))
    db.session.commit()

    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1},
                headers={'Authorization': f'Bearer {token}'})
    res = client.get(f'/carts/{user_id}/recommend', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert any(p['title'] == hot_title for p in data)

def test_cart_collaborative_recommend(client, user_token_and_id):
    token, user_id = user_token_and_id
    collab_title = f'Collab_Product for user {user_id}'
    p3 = Product(title=collab_title, price=300, description='collab', category_id=1, images=['img3-1', 'img3-2'])
    db.session.add(p3)
    db.session.commit()

    # 改：新增 user2 只用 email
    user2 = User(email=f'collab{user_id}@example.com', password='pw')
    db.session.add(user2)
    db.session.commit()

    order2 = Order(user_id=user2.id)
    db.session.add(order2)
    db.session.commit()
    db.session.add_all([
        OrderItem(order_id=order2.id, product_id=1, quantity=1, price=100),
        OrderItem(order_id=order2.id, product_id=p3.id, quantity=2, price=300)
    ])
    db.session.commit()

    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1},
                headers={'Authorization': f'Bearer {token}'})
    res = client.get(f'/carts/{user_id}/recommend/collaborative', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.get_json()
    assert any(p['title'] == collab_title for p in data)

def test_discount_code_checkout_flow(client, user_token_and_id, discount_code,shipping_info):
    token, user_id = user_token_and_id

    # 1. 先加商品到購物車
    res = client.post(f'/carts/{user_id}',
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
        'discount_code': discount_code.code,
        'shipping_info': shipping_info         
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
    
def test_product_specific_discount_code_and_sale(client, user_token_and_id,shipping_info):
    """
    商品專屬折扣碼 + 商品有特價，應只擇一（取最優惠），不能疊加
    例：原價$100，特價$80，折扣碼9折=$90，最終$80*2=160
    """
    from models import Product, db, ProductOnSale, DiscountCode
    from datetime import datetime

    token, user_id = user_token_and_id

    # 1. 新增商品
    product = Product(title='專屬測試商品', price=100, description='desc', category_id=1, images=['img1'])
    db.session.add(product)
    db.session.commit()

    # 2. 設定商品特價 8折
    sale = ProductOnSale(
        product_id=product.id, discount=0.8,
        start_date=datetime(2000, 1, 1), end_date=datetime(2099, 1, 1), description='特價8折'
    )
    db.session.add(sale)
    db.session.commit()

    # 3. 設定商品專屬9折折扣碼（不能疊加）
    code = "SPECIFICSALE"
    dc = DiscountCode(
        code=code, discount=0.9, amount=None,
        product_id=product.id, min_spend=0,
        valid_from=datetime(2000, 1, 1), valid_to=datetime(2099, 1, 1),
        usage_limit=10, per_user_limit=2, description="專屬折扣", is_active=True
    )
    db.session.add(dc)
    db.session.commit()

    # 4. 放商品進購物車
    res = client.post(f'/carts/{user_id}', json={'product_id': product.id, 'quantity': 2},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    # 5. 套用商品專屬折扣碼（只擇一優惠：$80*2）
    res = client.post(f'/carts/{user_id}/apply_discount', json={'code': code},
                      headers={'Authorization': f'Bearer {token}'})
    data = res.get_json()
    assert data["success"] is True
    assert data["discounted_total"] == 160  # $80*2
    assert data["discount_amount"] == 40    # $100*2 - $80*2

    # 6. 結帳驗證
    res = client.post(f'/carts/{user_id}/checkout',
                      json={'items': [{'product_id': product.id, 'quantity': 2}], 
                        'shipping_info':shipping_info, 
                        'discount_code': code},
                        headers={'Authorization': f'Bearer {token}'})
    result = res.get_json()
    print("Checkout 回傳：", result)
    assert result["total"] == 160
    assert result["discount_amount"] == 40

def test_sitewide_discount_code_with_sale(client, user_token_and_id,shipping_info):
    """
    全站折扣碼 + 特價商品，可疊加（先特價再全單折扣）
    例：原價$100，特價$80，再9折=72，最終$72*2=144
    """
    from models import Product, db, ProductOnSale, DiscountCode
    from datetime import datetime

    token, user_id = user_token_and_id

    # 1. 新增商品
    product = Product(title='全站折扣測試', price=100, description='desc', category_id=1, images=['img2'])
    db.session.add(product)
    db.session.commit()

    # 2. 設定商品特價 8折
    sale = ProductOnSale(
        product_id=product.id, discount=0.8,
        start_date=datetime(2000, 1, 1), end_date=datetime(2099, 1, 1), description='特價8折'
    )
    db.session.add(sale)
    db.session.commit()

    # 3. 全站9折折扣碼（可疊加）
    code = "SITEWIDE"
    dc = DiscountCode(
        code=code, discount=0.9, amount=None,
        product_id=None, min_spend=0,
        valid_from=datetime(2000, 1, 1), valid_to=datetime(2099, 1, 1),
        usage_limit=10, per_user_limit=2, description="全站折扣", is_active=True
    )
    db.session.add(dc)
    db.session.commit()

    # 4. 放商品進購物車
    res = client.post(f'/carts/{user_id}', json={'product_id': product.id, 'quantity': 2},
                      headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    # 5. 套用全站折扣碼（特價再折扣 $80*0.9=$72；$72*2=144）
    res = client.post(f'/carts/{user_id}/apply_discount', json={'code': code},
                      headers={'Authorization': f'Bearer {token}'})
    data = res.get_json()
    assert data["success"] is True
    assert data["discounted_total"] == 144
    assert data["discount_amount"] == 16  # $80*2 - $72*2

    # 6. 結帳驗證
    res = client.post(f'/carts/{user_id}/checkout',
                      json={'items': [{'product_id': product.id, 'quantity': 2}],
                             'shipping_info':shipping_info, 
                            'discount_code': code},
                            headers={'Authorization': f'Bearer {token}'})
    result = res.get_json()
    print("Checkout 回傳：", result)
    assert result["total"] == 144
    assert result["discount_amount"] == 16

def test_cart_permission(client, user_token_and_id,shipping_info):
    token1, user1 = user_token_and_id
    # 新增 user2
    client.post('/auth/register', json={'email': 'user2@example.com', 'password': 'pw'})
    login_res = client.post('/auth/login', json={'email': 'user2@example.com', 'password': 'pw'})
    token2 = login_res.get_json()['access_token']
    user2 = login_res.get_json()['user_id']
    # 用 user2 查詢 user1 購物車
    res = client.get(f'/carts/{user1}', headers={'Authorization': f'Bearer {token2}'})
    assert res.status_code == 403
    # 用 user2 結帳 user1
    res = client.post(f'/carts/{user1}/checkout', json={'items': [{'product_id': 1, 'quantity': 1}],
                                                        'shipping_info': shipping_info
                                                        }
                      , headers={'Authorization': f'Bearer {token2}'})
    assert res.status_code == 403

def test_cart_unauthorized(client, user_token_and_id,shipping_info):
    _, user_id = user_token_and_id
    # 沒 token 查購物車
    res = client.get(f'/carts/{user_id}')
    assert res.status_code == 401
    # 沒 token 結帳
    res = client.post(f'/carts/{user_id}/checkout', json={'items': [{'product_id': 1, 'quantity': 1}],
                                                        'shipping_info': shipping_info
                                                        })
    assert res.status_code == 401

def test_cart_add_nonexistent_product(client, user_token_and_id):
    token, user_id = user_token_and_id
    res = client.post(f'/carts/{user_id}', json={'product_id': 99999, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code in (400, 404)

def test_cart_update_invalid_quantity(client, user_token_and_id):
    token, user_id = user_token_and_id
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    res = client.put(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 0}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 400

def test_cart_checkout_empty(client, user_token_and_id,shipping_info):
    token, user_id = user_token_and_id
    # 空購物車結帳
    res = client.post(f'/carts/{user_id}/checkout', json={'items': [],'shipping_info': shipping_info}, headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 400

def test_cart_discount_code_usage_limit(client, user_token_and_id, discount_code,shipping_info):
    token, user_id = user_token_and_id
    # 超過可用次數
    discount_code.per_user_limit = 1
    db.session.commit()
    from models import UserDiscountCode
    udc = UserDiscountCode.query.filter_by(user_id=user_id, discount_code_id=discount_code.id).first()
    print("used_count before checkout:", udc.used_count if udc else "None")
    # 先用一次
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    client.post(f'/carts/{user_id}/checkout',
                json={'items': [{'product_id': 1, 'quantity': 1}],
                        'shipping_info': shipping_info,
                        'discount_code': discount_code.code}, 
                headers={'Authorization': f'Bearer {token}'})
    udc = UserDiscountCode.query.filter_by(user_id=user_id, discount_code_id=discount_code.id).first()
    print("used_count after checkout:", udc.used_count if udc else "None")
    
    db.session.remove()  # 斷開所有連線（更激進地清除 cache）
    db.session.commit()  # 確保 commit 完後才 apply
    # 再用一次
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    res = client.post(f'/carts/{user_id}/apply_discount', json={'code': discount_code.code}, headers={'Authorization': f'Bearer {token}'})
    print("API Response (should fail):", res.get_json())
    
    assert not res.get_json()['success']
    assert "可用次數上限" in res.get_json()['message']
    
def test_cart_discount_code_usage_limit(client, user_token_and_id, discount_code,shipping_info):
    token, user_id = user_token_and_id

    # 保證測試乾淨：刪掉使用紀錄
    #from models import UserDiscountCode
    #UserDiscountCode.query.filter_by(user_id=user_id, discount_code_id=discount_code.id).delete()
    discount_code.used_count = 0
    discount_code.per_user_limit = 1
    db.session.commit()

    # 1. 先加商品
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 2}, headers={'Authorization': f'Bearer {token}'})
    # 2. 第一次 apply 折扣碼，確認可用
    res1 = client.post(f'/carts/{user_id}/apply_discount', json={'code': discount_code.code}, headers={'Authorization': f'Bearer {token}'})
    print("API Response (first apply):", res1.get_json())
    assert res1.status_code == 200
    assert res1.get_json()['success'] is True

    # 3. 結帳
    res2 = client.post(f'/carts/{user_id}/checkout', json={'items': [{'product_id': 1, 'quantity': 2}],
                                                           'shipping_info': shipping_info, 
                                                           'discount_code': discount_code.code}, 
                                                    headers={'Authorization': f'Bearer {token}'})
    assert res2.status_code == 200

    # 4. 第二次再用應該失敗
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 2}, headers={'Authorization': f'Bearer {token}'})
    res3 = client.post(f'/carts/{user_id}/apply_discount', json={'code': discount_code.code}, headers={'Authorization': f'Bearer {token}'})
    print("API Response (should fail):", res3.get_json())
    assert res3.get_json()['success'] is False
    assert "可用次數上限" in res3.get_json()['message']


def test_cart_add_same_product_multiple_times(client, user_token_and_id):
    token, user_id = user_token_and_id
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 1}, headers={'Authorization': f'Bearer {token}'})
    client.post(f'/carts/{user_id}', json={'product_id': 1, 'quantity': 2}, headers={'Authorization': f'Bearer {token}'})
    res = client.get(f'/carts/{user_id}', headers={'Authorization': f'Bearer {token}'})
    assert res.get_json()['items'][0]['quantity'] == 3

#訪客CRUD流程
def test_guest_cart_crud_flow(client, guest_id):
    # 查詢空購物車
    res = client.get(f'/carts/guest/{guest_id}')
    assert res.status_code == 200
    assert res.get_json()['items'] == []

    # 加商品到購物車
    res = client.post(f'/carts/guest/{guest_id}', json={'product_id': 1, 'quantity': 2})
    assert res.status_code == 200
    cart_id = res.get_json()['cart_id']

    # 查詢購物車內容
    res = client.get(f'/carts/guest/{guest_id}')
    assert res.status_code == 200
    items = res.get_json()['items']
    assert len(items) == 1 and items[0]['product_id'] == 1 and items[0]['quantity'] == 2

    # 調整商品數量
    res = client.put(f'/carts/guest/{guest_id}', json={'product_id': 1, 'quantity': 5})
    assert res.status_code == 200
    res = client.get(f'/carts/guest/{guest_id}')
    assert res.get_json()['items'][0]['quantity'] == 5

    # 刪除商品
    res = client.delete(f'/carts/guest/{guest_id}', json={'product_id': 1})
    assert res.status_code == 200
    res = client.get(f'/carts/guest/{guest_id}')
    assert res.get_json()['items'] == []
# 訪客結帳流程測試
def test_guest_cart_checkout(client, guest_id):
    # 先加商品
    client.post(f'/carts/guest/{guest_id}', json={'product_id': 1, 'quantity': 2})

    # 檢查購物車
    res = client.get(f'/carts/guest/{guest_id}')
    assert res.status_code == 200

    # 訪客結帳
    shipping_info = {
        "shipping_method": "711",
        "recipient_name": "訪客甲",
        "recipient_phone": "0912345678",
        "recipient_email": "guest1@mail.com",
        "store_name": "7-11 測試店"
    }
    res = client.post(
        f'/carts/guest/{guest_id}/checkout',
        json={
            'items': [{'product_id': 1, 'quantity': 2}],
            'shipping_info': shipping_info
        }
    )
    assert res.status_code == 200
    assert 'order_id' in res.get_json()

    # 結帳後購物車應為空
    res = client.get(f'/carts/guest/{guest_id}')
    assert res.get_json()['items'] == []
#訪客錯誤防呆測試
def test_guest_cart_add_nonexistent_product(client, guest_id):
    res = client.post(f'/carts/guest/{guest_id}', json={'product_id': 99999, 'quantity': 1})
    assert res.status_code in (400, 404)

def test_guest_cart_update_invalid_quantity(client, guest_id):
    client.post(f'/carts/guest/{guest_id}', json={'product_id': 1, 'quantity': 1})
    res = client.put(f'/carts/guest/{guest_id}', json={'product_id': 1, 'quantity': 0})
    assert res.status_code == 400

def test_guest_cart_checkout_empty(client, guest_id):
    res = client.post(f'/carts/guest/{guest_id}/checkout', json={'items': []})
    assert res.status_code == 400
