from app import create_app
from models import db, Product
import json

app = create_app()
app.app_context().push()

# 只查詢 id 25~34 的商品
products = Product.query.filter(Product.id >= 25, Product.id <= 34).all()
data = [p.to_dict() for p in products]

with open("products.json", "w", encoding="utf8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已匯出 id 25-34 之間的商品到 products.json")
