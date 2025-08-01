from models import db, Order,Product,User,OrderShipping,OrderItem
from exceptions import NotFoundError,ForbiddenError,DuplicateError
from service.audit_service import AuditService
from utils.notify_util import send_email_notify_user_order_status,send_line_notify_user_order_status
from datetime import datetime
from sqlalchemy.orm import joinedload

class OrderService:
    
    @staticmethod
    def _create_order(user_id=None, guest_id=None, guest_email=None):
        order = Order(
            user_id=user_id,
            guest_id=guest_id,
            guest_email=guest_email,
            order_date=datetime.now(),
            total=0,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # 先獲得 order.id
        return order

    @staticmethod
    def _add_order_item(order_id, product_id, quantity, price):
        order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, price=price)
        db.session.add(order_item)

    @staticmethod
    def get_all_orders(page=1, per_page=10):
        """查詢全部訂單，依日期排序（分頁）"""
        return Order.query.order_by(Order.order_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    @staticmethod
    def get_user_orders(user_id):
        return Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
    
    @staticmethod
    def get_user_orders(user_id, page=1, per_page=10):
        """查詢某用戶的全部訂單，依日期排序"""
        return Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_order_detail(order_id):
        """查詢單一訂單的詳細資料，含所有明細商品"""
        order = (
            Order.query
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.product),# 預載入 order_items product
                joinedload(Order.shipping),   # 預載入 shipping
            )
            .filter_by(id=order_id)
            .first()
        )
        if not order:
            raise NotFoundError("Order not found")

        # 這時候每個 item.product 已經在記憶體，不會再查 DB
        items = []
        for item in order.order_items:
            product = item.product
            items.append({
                "product_id": product.id,
                "title": product.title,
                "price": float(product.get_final_price()),
                "quantity": item.quantity,
                "images": product.images
            })

        shipping_info = order.shipping.to_dict() if order.shipping else None

        result = {
            "order_id": order.id,
            "user_id": order.user_id,
            "order_date": str(order.order_date),
            "total": float(order.total),
            "status": order.status,
            "discount_code_id": order.discount_code_id,
            "discount_amount": order.discount_amount,
            "items": items,
            "shipping_info": shipping_info
        }
        return result
    
    @staticmethod
    def get_order_detail_guest(order_id, guest_id, guest_email):
        """
        訪客查詢自己的單筆訂單的詳細資料
        """
        order = (
            Order.query
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.product),
                joinedload(Order.shipping),
            )
            .filter_by(id=order_id, guest_id=guest_id, guest_email=guest_email)
            .first()
        )
        if not order:
            raise NotFoundError("Order not found")

        items = []
        for item in order.order_items:
            product = item.product
            items.append({
                "product_id": product.id,
                "title": product.title,
                "price": float(product.get_final_price()),
                "quantity": item.quantity,
                "images": product.images
            })

        shipping_info = order.shipping.to_dict() if order.shipping else None

        result = {
            "order_id": order.id,
            "user_id": order.user_id,
            "order_date": str(order.order_date),
            "total": float(order.total),
            "status": order.status,
            "discount_code_id": order.discount_code_id,
            "discount_amount": order.discount_amount,
            "guest_email": order.guest_email,
            "items": items,
            "shipping_info": shipping_info
        }
        return result

    @staticmethod
    def cancel_order(order_id):
        """取消訂單"""
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            raise NotFoundError("Order not found")
        if order.status not in ["pending", "paid"]:
            raise ValueError("Only pending or paid orders can be cancelled")
        order.status = 'cancelled'
        db.session.commit()
        
                #email 寄信通知
        send_email_notify_user_order_status(order)
        #line 新增推播通知
        user = User.get_by_user_id(order.user_id)
        send_line_notify_user_order_status(user, order)
        return order
    
    
    @staticmethod
    def cancel_order_guest(order_id, guest_id, guest_email):
        """
        訪客訂單取消邏輯：同時驗證 guest_id 與 email
        """
        order = Order.query.filter_by(id=order_id, guest_id=guest_id, guest_email=guest_email).first()
        if not order:
            raise NotFoundError("Order not found or permission denied")
        # 執行取消（直接複用原本 cancel_order，但要注意可能權限不同）
        if order.status not in ["pending", "paid"]:
            raise ValueError("Only pending or paid orders can be cancelled")
        order.status = 'cancelled'
        db.session.commit()
        # email 通知
        send_email_notify_user_order_status(order)
        AuditService.log(
        guest_id=guest_id,
        action='guest_cancel',
        target_type='order',
        target_id=order.id,
        description=f"[{guest_id}] cancel order: {order.to_dict()}"
        )
        return order
    
    @staticmethod
    def update_order_status(order_id, status):
        """更新訂單狀態"""
        ORDER_STATUS = [
            'pending', 'paid', 'processing', 'shipped',
            'delivered', 'cancelled', 'returned', 'refunded'
        ]
        order = db.session.get(Order, order_id)
        if not order:
            raise NotFoundError("Order not found")
        if status not in ORDER_STATUS:
            raise ValueError("Status in wrong format")
        if order.status == status:
            raise ValueError(f"Order is already in status '{status}'")
        order.status = status
        db.session.commit()
        #email 寄信通知
        #send_email_notify_user_order_status(order)
        #line 新增推播通知
        user = User.get_by_user_id(order.user_id)
        send_line_notify_user_order_status(user, order)
        return order
    
    @staticmethod
    def set_shipping_info(order_id, shipping_method,recipient_name,recipient_phone,store_name, operator_user_id):

        ORDER_STATUS_REJECT = [
            'shipped',
            'delivered',
            'cancelled',
            'returned',
            'refunded'
        ]
        #做檢查
        missing = []
        if not shipping_method:
            missing.append("shipping_method")
        if not recipient_name:
            missing.append("recipient_name")
        if not recipient_phone:
            missing.append("recipient_phone")
        if not store_name:
            missing.append("store_name")
        if missing:
            raise ValueError({"error": f"缺少欄位: {', '.join(missing)}"})
        
        order = Order.get_by_order_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        if order.status in ORDER_STATUS_REJECT:
            raise ForbiddenError(f"訂單狀態為 {order.status}，不可修改寄送資訊")

        # 查有沒有寄送資料，沒有就新增，有就reject
        shipping = OrderShipping.query.filter_by(order_id=order_id).first()
        if shipping:
            raise DuplicateError("Order shipping info  exists")
        else:
            shipping = OrderShipping(
                order_id=order_id,
                shipping_method=shipping_method,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                store_name=store_name
            )
            db.session.add(shipping)
        # 日誌
        AuditService.log(
            user_id = operator_user_id if operator_user_id is not None and isinstance(operator_user_id, int) else None, 
            guest_id = operator_user_id if operator_user_id is not None and isinstance(operator_user_id, str) else None,
            action='set',
            target_type='order_shipping',
            target_id=shipping.id,
            description=f"set order_shipping: {shipping.to_dict()}"
        )
        db.session.commit()
        return shipping
    
    #admin only
    @staticmethod
    def update_shipping_info(order_id, data, operator_user_id=None):
        ORDER_STATUS_REJECT = [
            'shipped',
            'delivered',
            'cancelled',
            'returned',
            'refunded'
        ]
        order = Order.get_by_order_id(order_id)
        if not order:
            raise NotFoundError("Order not found")
        if order.status in ORDER_STATUS_REJECT:
            raise ForbiddenError(f"訂單狀態為 {order.status}，不可修改寄送資訊")

        shipping = OrderShipping.query.filter_by(order_id=order_id).first()
        if not shipping:
            raise NotFoundError("Order shipping info not found")

        # 只更新有給的欄位
        for field in ['shipping_method', 'recipient_name', 'recipient_phone', 'store_name']:
            if field in data and data[field]:
                setattr(shipping, field, data[field])

        db.session.commit()

        # 日誌
        AuditService.log(
            user_id=operator_user_id or "admin",
            action='update',
            target_type='order_shipping',
            target_id=shipping.id,
            description=f"update order_shipping: {shipping.to_dict()}"
        )
        return shipping
