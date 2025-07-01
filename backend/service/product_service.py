from models import db, Product,ProductOnSale,OrderItem,Order,Cart,CartItem
from exceptions import NotFoundError
from datetime import datetime
from utils import notify_util
class ProductService:
    @staticmethod
    def search(category_id=None, keyword=None, min_price=None, max_price=None, page=1, per_page=10):
        query = Product.query
        if category_id is not None:
            query = query.filter_by(category_id=category_id)
        if keyword:
            query = query.filter(Product.title.ilike(f"%{keyword}%"))
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def create_product(title, price, category_id, description=None, image=None):
            
        if not title or price is None or not category_id:
            raise ValueError('title, price, category_id are required')

        product = Product(
            title=title,
            price=price,
            description=description,
            category_id=category_id,
            image=image
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(product_id, title, price, category_id, description, image):
        product = Product.get_by_product_id(product_id)
        if not product:
            raise NotFoundError("product not found")
        if title:
            product.title = title
        if price:
            product.price = price
        if description:
            product.description = description
        if category_id:
            product.category_id = category_id
        if image:
            product.image = image
        db.session.commit()
        return product

    @staticmethod
    def delete_product(product_id):
        product = Product.get_by_product_id(product_id)
        if not product:
            raise NotFoundError("product not found")
        db.session.delete(product)
        db.session.commit()
        return product

    @staticmethod
    def add_product_onsale(product_id,discount,start_date,end_date,description):
        if not (0 < discount < 1):
            raise ValueError("discount must between 0 to 1")
         # 檢查 start_date 格式
        if start_date is None:
            start_date = datetime.now()
        elif isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError("start_date format error, must be YYYY-MM-DDTHH:MM:SS")

        # 檢查 end_date 格式
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError("end_date format error, must be YYYY-MM-DDTHH:MM:SS")

        # 檢查 end_date 必須晚於 start_date
        if end_date < start_date:
            raise ValueError("end_date must be after start_date")

        sale = ProductOnSale(
        product_id=product_id,
        discount=discount,
        start_date=start_date,
        end_date=end_date,
        description=description
        )
        db.session.add(sale)
        db.session.commit()
        
        # 呼叫通知 function
        notify_util.notify_users_cart_product_on_sale(product_id, discount, start_date, end_date, description)
        
        return sale

    @staticmethod
    def recommend_for_user(user_id, limit=5):
        # 1. 直接查詢該用戶所有買過的商品id
        bought_product_ids = db.session.query(OrderItem.product_id)\
            .join(Order, Order.id == OrderItem.order_id)\
            .filter(Order.user_id == user_id)\
            .distinct().all()
        bought_product_ids = [pid[0] for pid in bought_product_ids]
        if not bought_product_ids:
            return []
        
        # 2. 查詢這些商品的分類
        category_ids = db.session.query(Product.category_id)\
            .filter(Product.id.in_(bought_product_ids))\
            .distinct().all()
        category_ids = [cid[0] for cid in category_ids]
        if not category_ids:
            return []

        # 3. 找這些分類下，未買過的熱賣商品
        subq = (
            db.session.query(
                OrderItem.product_id,
                db.func.count(OrderItem.id).label('order_count')
            )
            .group_by(OrderItem.product_id)
            .subquery()
        )
        products = (
            db.session.query(Product)
            .outerjoin(subq, Product.id == subq.c.product_id)
            .filter(Product.category_id.in_(category_ids))
            .filter(~Product.id.in_(bought_product_ids))
            .order_by(subq.c.order_count.desc().nullslast(), Product.id.desc())
            .limit(limit)
            .all()
        )
        return products
    
    #根據購物車
    @staticmethod
    def recommend_for_cart(user_id, limit=5):
        # 找出該用戶目前 active 購物車商品 id
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart or not cart.cart_items:
            return []  # 沒有購物車或沒商品就不推薦
        
        cart_product_ids = [item.product_id for item in cart.cart_items]
        
        # 取這些商品的分類
        category_ids = (
            db.session.query(Product.category_id)
            .filter(Product.id.in_(cart_product_ids))
            .distinct()
            .all()
        )
        category_ids = [cid[0] for cid in category_ids]
        if not category_ids:
            return []
        
        # 找這些分類下、尚未在購物車的熱賣商品
        subq = (
            db.session.query(
                OrderItem.product_id,
                db.func.count(OrderItem.id).label('order_count')
            )
            .group_by(OrderItem.product_id)
            .subquery()
        )
        products = (
            db.session.query(Product)
            .outerjoin(subq, Product.id == subq.c.product_id)
            .filter(Product.category_id.in_(category_ids))
            .filter(~Product.id.in_(cart_product_ids))
            .order_by(subq.c.order_count.desc().nullslast(), Product.id.desc())
            .limit(limit)
            .all()
        )
        return products
    
    #協同過濾(有買過你購物車內商品的人，還常常一起買哪些商品)
    @staticmethod
    def recommend_for_cart_collaborative(user_id, limit=5):
        # 1. 取得購物車內商品 id
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart or not cart.cart_items:
            return []
        cart_product_ids = [item.product_id for item in cart.cart_items]
        
        # 2. 有買過這些商品的用戶 id（不含自己）
        users = db.session.query(Order.user_id)\
            .join(OrderItem, Order.id == OrderItem.order_id)\
            .filter(OrderItem.product_id.in_(cart_product_ids))\
            .filter(Order.user_id != user_id)\
            .distinct().all()
        user_ids = [uid[0] for uid in users]
        if not user_ids:
            return []

        # 3. 這些用戶還買過什麼商品，排除購物車已存在商品
        bought_items = db.session.query(
                OrderItem.product_id,
                db.func.count(OrderItem.id).label('cnt')
            )\
            .join(Order, Order.id == OrderItem.order_id)\
            .filter(Order.user_id.in_(user_ids))\
            .filter(~OrderItem.product_id.in_(cart_product_ids))\
            .group_by(OrderItem.product_id)\
            .order_by(db.desc('cnt'))\
            .limit(limit)\
            .all()
        
        product_ids = [item[0] for item in bought_items]
        if not product_ids:
            return []

        # 4. 撈出商品資料
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        
        # 最終結果排序依照出現次數
        id_to_product_map = {p.id: p for p in products}
        
        result = []
        for pid in product_ids:
            if pid in id_to_product_map:
                result.append(id_to_product_map[pid])
        
        return result