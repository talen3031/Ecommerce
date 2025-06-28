from models import db, Cart, CartItem, Product,Order,OrderItem
from datetime import datetime
from exceptions import NotFoundError
from service.audit_service import AuditService

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
            product = item.product
            #計算折扣後價格
            final_price = product.get_final_price() if product else 0
            items.append({
                "product_id": item.product_id,
                "title": item.product.title if item.product else None,
                "price":final_price,
                "orginal_price": float(item.product.price) if product and product.price else 0.0,
                "quantity": item.quantity
            })
        res = cart.to_dict() 
        res["items"] = items
        return res
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        # 1. 取得該用戶最新（active）購物車，沒有則新建
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            cart = Cart(user_id=user_id, created_at=datetime.now(), status='active')
            db.session.add(cart)
            db.session.commit()

        # 2. 檢查商品是否存在
        product = Product.get_by_product_id(product_id)
        if not product:
            raise NotFoundError("Product not found")

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
            raise NotFoundError("No active cart found")
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
            raise NotFoundError("No active cart found")
        # 2. 找到該商品在購物車的 cart_item
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            raise ValueError("Product not in cart")
        old_qty = cart_item.quantity
        if old_qty==quantity:
            raise ValueError(f"quantity is already {quantity}")
        cart_item.quantity = quantity
        db.session.commit()
        return cart_item,old_qty

    @staticmethod
    def checkout_cart(user_id, items_to_checkout):
        if not items_to_checkout or not isinstance(items_to_checkout, list):
            raise ValueError("Must provide items to checkout")
        # validate user cart == 'active'
        cart = CartService._get_active_cart(user_id)
        # validate cart_item compare to the items_to_checkout
        CartService._validate_cart_items(cart, items_to_checkout)

        order = CartService._create_order(user_id)
        total = 0

        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            product = db.session.get(Product, product_id)
            
            price = product.get_final_price() if product else 0
            total += price * quantity
            
            #add  order item
            CartService._add_order_item(order.id, product_id, quantity, price)
            # handle rest of cart_item
            CartService._handle_cart_item_on_checkout(user_id, cart, product_id, quantity)

        order.total = total
        #if cart become empty set cart status = check_out
        message = CartService._update_cart_status_if_empty(user_id, cart)

        db.session.commit()

        return {
            "message": message,
            "order_id": order.id,
            "total": float(total)
        }
    
    @staticmethod
    def _get_active_cart(user_id):
        cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
        if not cart:
            raise ValueError("No active cart to checkout")
        return cart

    @staticmethod
    def _validate_cart_items(cart, items_to_checkout):
        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
            if not cart_item or quantity > cart_item.quantity:
                raise ValueError(f"Product {product_id} quantity not enough in cart")

    @staticmethod
    def _create_order(user_id):
        order = Order(user_id=user_id, order_date=datetime.now(), total=0, status='pending')
        db.session.add(order)
        db.session.flush()  # 先獲得 order.id
        return order

    @staticmethod
    def _add_order_item(order_id, product_id, quantity, price):
        order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        db.session.add(order_item)

    @staticmethod
    def _handle_cart_item_on_checkout(user_id, cart, product_id, quantity):
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        old_quantity = cart_item.quantity
        if old_quantity == quantity:
            db.session.delete(cart_item)
            action = "remove_from_cart_on_checkout"
            desc = f"Removed product_id={product_id} from cart_id={cart.id} during checkout (qty={quantity})"
        else:
            cart_item.quantity -= quantity
            action = "update_cart_item_on_checkout"
            desc = f"Decreased product_id={product_id} in cart_id={cart.id} from {old_quantity} to {cart_item.quantity} during checkout"
        
        #write to audit_log
        AuditService.log(
            user_id=user_id,
            action=action,
            target_type="cart_item",
            target_id=cart_item.id,
            description=desc
        )

    @staticmethod
    def _update_cart_status_if_empty(user_id, cart):
        if len(cart.cart_items) == 0:
            cart.status = 'checked_out'
            #write to audit_log
            AuditService.log(
                user_id=user_id,
                action="cart_checked_out",
                target_type="cart",
                target_id=cart.id,
                description=f"Cart {cart.id} status changed to checked_out after checkout"
            )
            return "all checkout success"
        else:
            return "partial checkout success"
