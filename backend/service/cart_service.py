from models import db, Cart, CartItem, Product,Order,OrderItem,User
from datetime import datetime
from exceptions import NotFoundError
from service.audit_service import AuditService
from service.discount_service import DiscountService
from utils.notify_util import send_email_notify_order_created,send_line_notify_order_created
from utils.google_sheets_util import append_order_to_sheet

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
            if not product or not product.is_active:
                continue  # 跳過下架商品
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
        product = Product.get_active_by_product_id(product_id)
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
    def checkout_cart(user_id, items_to_checkout, discount_code=None):
        if not items_to_checkout or not isinstance(items_to_checkout, list):
            raise ValueError("Must provide items to checkout")

        cart = CartService._get_active_cart(user_id)

        #驗證 cart_item 跟 items_to_checkout(例如 items_to_checkout 的quantity 不能大於 cart 中的 quantity) 
        CartService._validate_cart_items(cart, items_to_checkout)

        # 1. 計算原價總金額（不新增 order_item，只用來驗證金額）
        total = CartService._caculate_items_to_checkout(items_to_checkout, order=None, user_id=user_id, cart=cart)

        discount_amount = 0
        discount_obj = None

        # 2. 折扣碼驗證（失敗時直接 raise，不建立訂單）
        if discount_code:
            ok, msg, dc, discounted_total, discount_amount = DiscountService.apply_discount_code(
                user_id, cart, discount_code, items_to_checkout
            )
            if not ok:
                raise ValueError(f"折扣碼不可用: {msg}")
            total = discounted_total
            discount_obj = dc
        
        # 3. 通過所有驗證，開始正式建立訂單
        order = CartService._create_order(user_id)

        # 4. 寫入訂單商品（這時才寫入 DB）
        CartService._caculate_items_to_checkout(items_to_checkout, order, user_id, cart)
     

        # 5. 寫入訂單金額與折扣碼資訊
        order.total = total
        order.discount_code_id = discount_obj.id if discount_obj else None
        order.discount_amount = float(discount_amount) if discount_obj else None


        #日誌寫入（包含所有商品資料）
        order_items_str = ", ".join([f"{item['product_id']} x {item['quantity']}" for item in items_to_checkout])
        AuditService.log(
            user_id=user_id,
            action='add_order_items',
            target_type='order',
            target_id=order.id,
            description=f"Order {order.id} add items: {order_items_str}"
        )

        # 6. consume 折扣碼（正式寫入使用紀錄）
        if discount_code:
            DiscountService.consume_discount_code(user_id, discount_code)
            # 日誌寫入
            AuditService.log(
                user_id=user_id,
                action='use',  
                target_type='discount_code',
                target_id = discount_obj.id,
                description = f"user {user_id} use discount_code {discount_obj.id}"
            )
        message = CartService._update_cart_status_if_empty(user_id, cart)

        db.session.commit()
        import traceback
        try:
            send_email_notify_order_created(order)
            send_line_notify_order_created(user, order, order_items)
            append_order_to_sheet(order, order_items)
        except Exception as e:
            print("==== Checkout 外部服務錯誤 traceback ====")
            print(traceback.format_exc())
            raise
        # # ==== 寄信給user ========
        # send_email_notify_order_created(order)
        
        # # ==== line_bot 傳送訊息 給以綁定line的user ========
        # user = User.get_by_user_id(user_id)
        # order_items = OrderItem.query.filter_by(order_id=order.id).all()
        # send_line_notify_order_created(user, order, order_items)
        
        # # ==== 同步 Google Sheet ====
        # order_items = OrderItem.query.filter_by(order_id=order.id).all()
        # append_order_to_sheet(order, order_items)

        return {
            "message": message,
            "order_id": order.id,
            "total": float(total),
            "discount_amount": float(discount_amount) if discount_code else 0,
            "discount_code": discount_code if discount_code else None
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
    # 
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
    @staticmethod
    def _caculate_items_to_checkout(items_to_checkout,order,user_id,cart):
        total = 0 
        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            product = db.session.get(Product, product_id)
            
            price = product.get_final_price() if product else 0
            total += price * quantity
            if order:
                #add  order item
                CartService._add_order_item(order.id, product_id, quantity, price)
                # handle rest of cart_item
                CartService._handle_cart_item_on_checkout(user_id, cart, product_id, quantity)
        print("_caculate_items_to_checkout .....total=",total)
        return total
        