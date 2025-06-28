import requests
import random
from werkzeug.security import generate_password_hash
from models import db, Category, Product, User, Cart, CartItem, Order, OrderItem
from app import create_app
from flask import Flask

app = create_app()
app.app_context().push()

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
        exists = db.session.get(Product, prod['id'])
        if exists:
            continue
        p = Product(
            id=prod['id'],
            title=prod['title'],
            price=prod['price'],
            description=prod['description'],
            category_id=cat_name_id_map[prod['category']],
            image=prod['image']
        )
        db.session.add(p)
    db.session.commit()

def etl_users():
    print("下載 users...")
    resp = requests.get("https://fakestoreapi.com/users")
    users = resp.json()
    for u in users:
        if db.session.get(User, u['id']):
            continue
        full_name = f"{u['name']['firstname']} {u['name']['lastname']}"
        address = f"{u['address']['number']} {u['address']['street']}, {u['address']['city']}"
        user = User(
            id=u['id'],
            username=u['username'],
            email=u['email'],
            password=generate_password_hash(u['password']),
            full_name=full_name,
            address=address,
            phone=u['phone']
        )
        db.session.add(user)
    db.session.commit()

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
        #插入order
        if is_order:
            if db.session.get(Order, cart_data['id']):
                continue
            order = Order(id=cart_data['id'], user_id=user_id, order_date=date, total=0, status='completed')
            db.session.add(order)
            db.session.flush()
            total = 0
            #插入order_item
            for item in items:
                product = db.session.get(Product, item['productId'])
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
        #插入 carts
        else:
            if db.session.get(Cart, cart_data['id']):
                continue
            cart = Cart(id=cart_data['id'], user_id=user_id, created_at=date, status='active')
            db.session.add(cart)
            db.session.flush()
            #插入carts_item
            for item in items:
                db.session.add(CartItem(
                    cart_id=cart.id,
                    product_id=item['productId'],
                    quantity=item['quantity']
                ))
    db.session.commit()

def main():
    cat_name_id_map = etl_categories()
    etl_products(cat_name_id_map)
    etl_users()
    etl_carts_orders()
    print("✅ ORM 資料載入完成")

if __name__ == "__main__":
    main()
