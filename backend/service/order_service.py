from models import db, Order,Product,User
from exceptions import NotFoundError
from utils.notify_util import send_email_notify_user_order_status,send_line_notify_user_order_status
class OrderService:
    @staticmethod
    def create(user_id, order_date, total=0, status='pending'):
        """新增某用戶的訂單"""
        if not user_id :
            raise ValueError('missing user_id')
        
        order = Order(
            user_id=user_id,
            order_date=order_date,
            total=total,
            status=status
        )
        db.session.add(order)
        db.session.commit()
        return order
    
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
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            raise NotFoundError("Order not found")
    
        # 組合 items 清單
        items = []
        for item in order.order_items:
            product = db.session.get(Product, item.product_id)
            items.append({
                "product_id": product.id,
                "title": product.title,
                "price": float(product.get_final_price()),
                "quantity": item.quantity
            })
        result = {
            "order_id": order.id,
            "user_id": order.user_id,
            "order_date": str(order.order_date),
            "total": float(order.total),
            "status": order.status,
            "items": items
        }
        return result

    @staticmethod
    def cancel_order(order_id):
        """取消訂單"""
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            raise NotFoundError("Order not found")
        if order.status != 'pending':
            raise ValueError("Only pending orders can be cancelled")
        order.status = 'cancelled'
        db.session.commit()
                #email 寄信通知
        send_email_notify_user_order_status(order)
        #line 新增推播通知
        user = User.get_by_user_id(order.user_id)
        send_line_notify_user_order_status(user, order)
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