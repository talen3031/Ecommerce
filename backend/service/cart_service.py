from models import db, Cart, CartItem, Product, Order, OrderItem, User
from datetime import datetime
from exceptions import NotFoundError
from service.audit_service import AuditService
from service.discount_service import DiscountService
from service.order_service import OrderService
from utils.notify_util import send_email_notify_order_created, send_line_notify_order_created
from sqlalchemy.orm import joinedload

class CartService:

    @staticmethod
    def get_cart(user_id=None, guest_id=None):
        """
        回傳該用戶/訪客目前 active 狀態的購物車（含所有商品明細）
        """
        if (not user_id) and (not guest_id):
            raise  ValueError("user_id 或 guest_id 必須至少有一個")
        if user_id and  guest_id:
            raise  ValueError("user_id 或 guest_id 只能傳入一個")
        filter_args = {"status": "active"}
        if user_id:
            filter_args["user_id"] = user_id
        else: 
            filter_args["guest_id"] = guest_id
       

        cart = (
            Cart.query
            .options(joinedload(Cart.cart_items).joinedload(CartItem.product))
            .filter_by(**filter_args)
            .order_by(Cart.created_at.desc())
            .first()
        )
        if not cart:
            return None
        # 寫入購物車商品明細
        items = []
        for item in cart.cart_items:
            product = item.product
            if not product or not product.is_active:
                continue
            final_price = product.get_final_price() if product else 0
            items.append({
                "product_id": item.product_id,
                "title": product.title if product else None,
                "price": final_price,
                "orginal_price": float(product.price) if product and product.price else 0.0,
                "quantity": item.quantity,
                "images": product.images
            })
        res = cart.to_dict()
        res["items"] = items
        return res
    
    @staticmethod
    def add_to_cart(user_id=None, guest_id=None, product_id=None, quantity=1):
        """
        加入商品到購物車（支援會員或訪客）
        """
        if not product_id:
            raise ValueError("Missing product_id")

        if (not user_id) and (not guest_id):
            raise  ValueError("user_id 或 guest_id 必須至少有一個")
        if user_id and  guest_id:
            raise  ValueError("user_id 或 guest_id 只能傳入一個")
        filter_args = {"status": "active"}
        if user_id:
            filter_args["user_id"] = user_id
        else: 
            filter_args["guest_id"] = guest_id
       

        # 取得現有購物車或新建
        cart = Cart.query.filter_by(**filter_args).order_by(Cart.created_at.desc()).first()
        if not cart:
            cart = Cart(user_id=user_id, guest_id=guest_id, created_at=datetime.now(), status='active')
            db.session.add(cart)
            db.session.commit()

        # 商品驗證
        product = Product.get_active_by_product_id(product_id)
        if not product:
            raise NotFoundError("Product not found")

        # 查詢商品是否已在購物車
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
        AuditService.log(
            user_id=user_id,
            guest_id=guest_id,
            action='add',
            target_type='cart_item',
            target_id=cart_item.cart_id,
            description=f"add prodcut{product_id} quantity: {quantity} to cart{cart_item.cart_id}"
        )
        return cart_item

    @staticmethod
    def remove_from_cart(user_id=None, guest_id=None, product_id=None):
        filter_args = {"status": "active"}
        if (not user_id) and (not guest_id):
            raise  ValueError("user_id 或 guest_id 必須至少有一個")
        if user_id and  guest_id:
            raise  ValueError("user_id 或 guest_id 只能傳入一個")
        filter_args = {"status": "active"}
        if user_id:
            filter_args["user_id"] = user_id
        else: 
            filter_args["guest_id"] = guest_id
       
        cart = Cart.query.filter_by(**filter_args).order_by(Cart.created_at.desc()).first()
        if not cart:
            raise NotFoundError("No active cart found")
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            raise ValueError("Product not in cart")
        db.session.delete(cart_item)
        db.session.commit()
        AuditService.log(
            user_id=user_id,
            guest_id=guest_id,
            action='delete',
            target_type='cart_item',
            target_id=cart_item.id,
            description=f"Delete product_id={product_id} from cart_id={cart_item.cart_id}"
        )
        return cart_item

    @staticmethod
    def update_cart_item(user_id=None, guest_id=None, product_id=None, quantity=None):
        if quantity is None or quantity < 1:
            raise ValueError("Quantity must be at least 1")
        if (not user_id) and (not guest_id):
            raise  ValueError("user_id 或 guest_id 必須至少有一個")
        if user_id and  guest_id:
            raise  ValueError("user_id 或 guest_id 只能傳入一個")
        filter_args = {"status": "active"}
        if user_id:
            filter_args["user_id"] = user_id
        else: 
            filter_args["guest_id"] = guest_id
       
        
        cart = Cart.query.filter_by(**filter_args).order_by(Cart.created_at.desc()).first()
        if not cart:
            raise NotFoundError("No active cart found")
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            raise ValueError("Product not in cart")
        old_qty = cart_item.quantity
        if old_qty == quantity:
            raise ValueError(f"quantity is already {quantity}")
        cart_item.quantity = quantity
        db.session.commit()
        AuditService.log(
            user_id=user_id,
            guest_id=guest_id,
            action='update',
            target_type='cart_item',
            target_id=cart_item.id,
            description=f"product_id={product_id}, cart_id={cart_item.cart_id}, qty {old_qty} -> {quantity}"
        )
        return cart_item, old_qty


    @staticmethod
    def checkout_cart(items_to_checkout, user_id=None, guest_id=None, discount_code=None, shipping_info=None):
        if not items_to_checkout or not isinstance(items_to_checkout, list):
            raise ValueError("Must provide items to checkout")
        if (not user_id) and (not guest_id):
            raise  ValueError("user_id 或 guest_id 必須至少有一個")
        if user_id and  guest_id:
            raise  ValueError("user_id 或 guest_id 只能傳入一個")
        
        
        # 1. 查購物車（支援 user_id 或 guest_id）
        cart = CartService._get_active_cart(user_id=user_id, guest_id=guest_id)
        # 2. 驗證商品數量
        CartService._validate_cart_items(cart, items_to_checkout)

        # 3. 計算金額
        total = CartService._caculate_items_to_checkout(items_to_checkout)

        discount_amount = 0
        discount_obj = None

        # 4. 折扣碼驗證
        if discount_code:
            ok, msg, dc, discounted_total, discount_amount, rule_msg, used_coupon  = DiscountService.apply_discount_code(
                user_id =user_id ,
                guest_id=guest_id, 
                cart=cart, 
                code=discount_code, 
                items_to_checkout=items_to_checkout
            )
            if not ok:
                raise ValueError(f"折扣碼不可用: {msg}")
            total = discounted_total
            discount_obj = dc
        else:
            used_coupon = False  # 無折扣碼

        # 5. 建立訂單（支援會員/訪客）
        order = OrderService._create_order(
            user_id =user_id,
            guest_id=guest_id,            # 訪客才寫入(guestemail = recipient_email !)
            guest_email=shipping_info.get("recipient_email") if (shipping_info and guest_id) else None,
        )
        # 6. 寫入訂單商品 
        CartService._add_items_to_checkout_to_order_items(items_to_checkout, order, user_id, guest_id, cart)
        # 7. 寫入訂單金額與折扣碼資訊
        order.total = total 
        order.discount_code_id = discount_obj.id if discount_obj else None
        order.discount_amount = float(discount_amount) if discount_obj else None

        # 8. 寫入 shipping info
        if shipping_info:
            OrderService.set_shipping_info(
                order.id,
                shipping_info.get("shipping_method"),
                shipping_info.get("recipient_name"),
                shipping_info.get("recipient_phone"),
                shipping_info.get("store_name"),
                user_id or guest_id
            )

        # 9. 記錄日誌
        order_items_str = ", ".join([f"{item['product_id']} x {item['quantity']}" for item in items_to_checkout])
        AuditService.log(
            user_id=user_id,
            guest_id=guest_id,
            action='add_order_items',
            target_type='order',
            target_id=order.id,
            description=f"Order {order.id} add items: {order_items_str}"
        )

        # 10. consume 折扣碼
        if discount_code and used_coupon:
            DiscountService.consume_discount_code(user_id=user_id , guest_id=guest_id, code=discount_code)
            AuditService.log(
                user_id=user_id,
                guest_id=guest_id,
                action='use',
                target_type='discount_code',
                target_id=discount_obj.id,
                description=f"user {user_id or guest_id} use discount_code {discount_obj.id}"
            )

        message = CartService._update_cart_status_if_empty(user_id=user_id, guest_id=guest_id, cart=cart)

        db.session.commit()

        # 日誌寫入
        AuditService.log(
            user_id=user_id,
            guest_id=guest_id,
            action='checkout',  # 建議用 'checkout'
            target_type='order',
            target_id = order.id,
            description = f"Checkout order_id={order.id}, total={total}, items={items_to_checkout}"
        )

        order_items = OrderItem.get_by_order_id(order_id=order.id)
        # 會員/訪客查收件人
        user = User.get_by_user_id(user_id) if user_id else None

        # ===== email訪客用戶通知  ======
        send_email_notify_order_created(order)
        # ===== 用戶line 訊息通知  ======
        if user_id:
            send_line_notify_order_created(user, order, order_items)
        
        return {
            "message": message,
            "order_id": order.id,
            "total": float(total),
            "discount_amount": float(discount_amount) if discount_code else 0,
            "discount_code": discount_code if discount_code else None
        }

    @staticmethod
    def _get_active_cart(user_id=None, guest_id=None):
        filter_args = {"status": "active"}
        if user_id:
            filter_args["user_id"] = user_id
        elif guest_id:
            filter_args["guest_id"] = guest_id
        else:
            raise ValueError("user_id 或 guest_id 必須至少有一個")
        cart = (Cart.query.options(
                    joinedload(Cart.cart_items).joinedload(CartItem.product)
                ).filter_by(**filter_args)
                .order_by(Cart.created_at.desc())
                .first()
                )
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
    # 處理購物車內的結帳商品
    @staticmethod
    def _handle_cart_item_on_checkout(user_id, guest_id, cart, product_id, quantity):
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
        AuditService.log(
            user_id=user_id,
            guest_id=guest_id,
            action=action,
            target_type="cart_item",
            target_id=cart_item.id,
            description=desc
        )

    @staticmethod
    def _update_cart_status_if_empty(user_id=None, guest_id=None, cart=None):
        if len(cart.cart_items) == 0:
            cart.status = 'checked_out'
            AuditService.log(
                user_id=user_id,
                guest_id=guest_id,
                action="cart_checked_out",
                target_type="cart",
                target_id=cart.id,
                description=f"Cart {cart.id} status changed to checked_out after checkout"
            )
            return "all checkout success"
        else:
            return "partial checkout success"

    @staticmethod
    def _caculate_items_to_checkout(items_to_checkout):
        total = 0
        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            product = Product.get_by_product_id(product_id)
            price = product.get_final_price() if product else 0
            total += price * quantity
        return total
    
    @staticmethod
    def _add_items_to_checkout_to_order_items(items_to_checkout,order,user_id, guest_id,cart):
        if not order :
            raise ValueError("order is required when _add_items_to_checkout_to_order_items")
        for item in items_to_checkout:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            product = Product.get_by_product_id(product_id)
            price = product.get_final_price() if product else 0
            OrderService._add_order_item(order.id, product_id, quantity, price)
            CartService._handle_cart_item_on_checkout(user_id, guest_id, cart, product_id, quantity)
        