from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, Product 

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# 查詢我的歷史訂單
@orders_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_orders(user_id):
    # 只允許本人查自己
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    orders = Order.for_user(user_id=user_id)
    Order.query.filter_by(user_id=user_id)
    result = []
    for order in orders:
        result.append({
            "order_id": order.id,
            "order_date": str(order.order_date),
            "total": float(order.total),
            "status": order.status
        })
    return jsonify(result)


# 查詢訂單明細
@orders_bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    items = []
    for item in order.order_items:
        product = db.session.get(Product, item.product_id)
        items.append({
            "product_id": product.id,
            "title": product.title,
            "price": float(product.price),
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
    return jsonify(result)

# 取消訂單
@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    order =  db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    if order.status != 'pending':
        return jsonify({"error": "Only pending orders can be cancelled"}), 400
    order.status = 'cancelled'
    db.session.commit()
    return jsonify({"message": "Order cancelled"})

# 訂單狀態流轉（PATCH）
@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    data = request.json
    status = data.get("status")
    if not status:
        return jsonify({"error": "Missing status"}), 400
    ORDER_STATUS = [
        'pending',
        'paid',
        'processing',
        'shipped',
        'delivered',
        'cancelled',
        'returned',
        'refunded'
    ]
    if status not in ORDER_STATUS:
        return jsonify({"error": "status in wrong format"}), 400
    order =  db.session.get(Order, order_id)

    
    if order.status==status:
        return jsonify({f"error": "status is {original_status} already"}), 404
    
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order.status = status
    db.session.commit()
    return jsonify({"message": f"Order status updated to {status}"})
