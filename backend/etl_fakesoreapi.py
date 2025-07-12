import requests
import random
from werkzeug.security import generate_password_hash
from models import db, Category, Product, User, Cart, CartItem, Order, OrderItem
from app import create_app

app = create_app()
app.app_context().push()

if Category.query.first():
    print("🟢 已有資料，跳過 ETL 載入")
    exit(0)

def etl_categories():
    print("下載 categories...")
    resp = requests.get("https://fakestoreapi.com/products/categories")
    categories = resp.json()
    cat_name_id_map = {}
    for cat in categories:
        category = Category.query.filter_by(name=cat).first()
        if not category:
            category = Category(name=cat)
            db.session.add(category)
            db.session.flush()
        cat_name_id_map[cat] = category.id
    db.session.commit()
    return cat_name_id_map

def etl_products(cat_name_id_map):
    print("下載 products...")
    resp = requests.get("https://fakestoreapi.com/products")
    products = resp.json()
    for prod in products:
        # 取得正確的 category_id
        category_id = cat_name_id_map.get(prod["category"])
        if not category_id:
            continue
        if Product.query.filter_by(title=prod["title"], category_id=category_id).first():
            continue
        p = Product(
            title=prod["title"],
            price=prod["price"],
            description=prod.get("description"),
            category_id=category_id,
            images=[prod["image"]]
        )
        db.session.add(p)
    db.session.commit()
    print("✅ 已載入 API products")

def etl_users():
    print("下載 users...")
    resp = requests.get("https://fakestoreapi.com/users")
    users = resp.json()
    for u in users:
        # 檢查 email 唯一
        if User.query.filter_by(email=u['email']).first():
            continue
        full_name = f"{u['name']['firstname']} {u['name']['lastname']}"
        address = f"{u['address']['number']} {u['address']['street']}, {u['address']['city']}"
        user = User(
            email=u['email'],
            password=generate_password_hash(u['password']),
            full_name=full_name,
            address=address,
            phone=u['phone']
        )
        db.session.add(user)
    db.session.commit()
    print("✅ 已載入 API users")

def etl_carts_orders():
    print("下載 carts 與 orders...")
    resp = requests.get("https://fakestoreapi.com/carts")
    carts_api = resp.json()
    cart_ids = [c['id'] for c in carts_api]
    order_ids = set(random.sample(cart_ids, k=len(cart_ids)//2))

    for cart_data in carts_api:
        is_order = cart_data['id'] in order_ids
        user_id = cart_data['userId']
        date = cart_data['date']
        items = cart_data['products']
        # 插入 order
        if is_order:
            # 用 user_id、order_date 判斷是否重複（可依你邏輯調整唯一條件）
            unique_order = Order.query.filter_by(user_id=user_id, order_date=date).first()
            if unique_order:
                continue
            order = Order(user_id=user_id, order_date=date, total=0, status='paid')
            db.session.add(order)
            db.session.flush()
            total = 0
            # 插入 order_item
            for item in items:
                unique_oi = OrderItem.query.filter_by(order_id=order.id, product_id=item['productId']).first()
                if unique_oi:
                    continue
                product = Product.query.filter_by(id=item['productId']).first()
                if not product:
                    continue
                subtotal = float(product.price) * item['quantity']
                total += subtotal
                db.session.add(OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item['quantity'],
                    price=product.price
                ))
            order.total = total
        # 插入 cart
        else:
            unique_cart = Cart.query.filter_by(user_id=user_id, created_at=date).first()
            if unique_cart:
                continue
            cart = Cart(user_id=user_id, created_at=date, status='active')
            db.session.add(cart)
            db.session.flush()
            for item in items:
                unique_ci = CartItem.query.filter_by(cart_id=cart.id, product_id=item['productId']).first()
                if unique_ci:
                    continue
                db.session.add(CartItem(
                    cart_id=cart.id,
                    product_id=item['productId'],
                    quantity=item['quantity']
                ))
    db.session.commit()
    print("✅ 已載入 API carts/orders")

def main():
    cat_name_id_map = etl_categories()
    etl_products(cat_name_id_map)
    etl_users()
    # etl_carts_orders()   # 需有正確 user_id 和 product_id 對應時再開啟
    print("✅ 所有資料已從 fakestoreapi.com 下載並載入資料庫")

if __name__ == "__main__":
    main()
