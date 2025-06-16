from models import db, Cart, CartItem, Product,Order,OrderItem
from datetime import datetime

class CartService:
    @staticmethod
    def get_cart(user_id):
        """
        回傳該用戶目前 active 狀態的購物車（含所有商品明細）
        """
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            return None  # 或視需求回傳 {"cart": None, "items": []}

        items = []
        for item in cart.cart_items:
            items.append({
                "product_id": item.product_id,
                "title": item.product.title if item.product else None,
                "price": float(item.product.price) if item.product and item.product.price else 0.0,
                "quantity": item.quantity
            })

        return {
            "cart_id": cart.id,
            "user_id": cart.user_id,
            "created_at": cart.created_at.isoformat() if cart.created_at else None,
            "status": cart.status,
            "items": items
        }
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        # 1. 取得該用戶最新（active）購物車，沒有則新建
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            cart = Cart(user_id=user_id, created_at=datetime.now(), status='active')
            db.session.add(cart)
            db.session.commit()

        # 2. 檢查商品是否存在
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")

        # 3. 查詢該商品是否已在購物車
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
        return cart_item

    @staticmethod
    def remove_from_cart(user_id, product_id):
        # 1. 找到該用戶 active 購物車
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            raise ValueError("No active cart found")
        # 2. 找到該商品在購物車的 cart_item
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            raise ValueError("Product not in cart")
        db.session.delete(cart_item)
        db.session.commit()
        return cart_item

    @staticmethod
    def update_cart_item(user_id, product_id, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        # 1. 找到該用戶 active 購物車
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            raise ValueError("No active cart found")
        # 2. 找到該商品在購物車的 cart_item
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            raise ValueError("Product not in cart")
        cart_item.quantity = quantity
        db.session.commit()
        return cart_item
    @staticmethod
    def checkout_cart(user_id, items_to_checkout):  
        """
        將購物車商品結帳為訂單，items_to_checkout: [{"product_id": x, "quantity": y}, ...]
        """
        if not items_to_checkout or not isinstance(items_to_checkout, list):
            raise ValueError("Must provide items to checkout")

        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            raise ValueError("No active cart to checkout")

        # 驗證每個商品與數量
        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            if not cart_item or quantity > cart_item.quantity:
                raise ValueError(f"Product {product_id} quantity not enough in cart")

        # 建立訂單
        order = Order(user_id=user_id, order_date=datetime.now(), total=0, status='pending')
        db.session.add(order)
        db.session.flush()  # 先獲得 order.id

        total = 0
        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            product = db.session.get(Product, product_id)
            price = float(product.price) if product else 0
            total += price * quantity
            order_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity, price=price)
            db.session.add(order_item)
            # 從購物車扣除數量
            cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            if cart_item.quantity == quantity:
                db.session.delete(cart_item)
            else:
                cart_item.quantity -= quantity

        order.total = total
        # 如果購物車已經沒有商品，就將狀態設為 checked_out
        if len(cart.cart_items) == 0:
            cart.status = 'checked_out'

        db.session.commit()
        return {
            "message": "Partial checkout success",
            "order_id": order.id,
            "total": float(total)
        }