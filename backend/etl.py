import os
import json
from werkzeug.security import generate_password_hash
from models import db, Category, Product, User
from app import create_app

app = create_app()
app.app_context().push()

# 1. 載入 categories
def etl_categories():
    print("載入 categories.json ...")
    if not os.path.exists("categories.json"):
        print("❌ 找不到 categories.json")
        return {}
    with open("categories.json", "r", encoding="utf-8") as f:
        categories = json.load(f)
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

# 2. 載入本地產品
def etl_local_products(json_path="products.json"):
    if not os.path.exists(json_path):
        print("❌ 找不到 products.json")
        return
    with open(json_path, "r", encoding="utf-8") as f:
        products = json.load(f)
    for prod in products:
        if Product.query.filter_by(title=prod["title"], category_id=prod["category_id"]).first():
            continue
        p = Product(
            title=prod["title"],
            price=prod["price"],
            description=prod.get("description"),
            category_id=prod["category_id"],
            images=prod.get("images", [])
        )
        db.session.add(p)
    db.session.commit()
    print("✅ 已載入本地 products.json 資料")

# 3. 新增一個 admin 用戶（必要時可自行擴充）
def etl_users():
    print("新增 admin 用戶...")
    if not User.query.filter_by(username='talen3031').first():
        user = User(
            username='talen3031',
            email="talen3031@gmail.com",
            password=generate_password_hash("talen168168"),
            full_name='蔡b',
            address='台南市東區',
            phone='0923956156',
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        print("✅ 已新增 admin user")
    else:
        print("admin user 已存在")

def main():
    etl_categories()
    etl_local_products()
    etl_users()
    print("✅ 全部資料已載入完成")

if __name__ == "__main__":
    main()
