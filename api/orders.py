from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, Product 
from service.order_service import OrderService

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# 查詢我的歷史訂單
@orders_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_orders(user_id):
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403
    orders = OrderService.get_user_orders(user_id)
    result = [
        {
            "order_id": order.id,
            "order_date": str(order.order_date),
            "total": float(order.total),
            "status": order.status
        } for order in orders
    ]
    return jsonify(result)
@orders_bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    detail = OrderService.get_order_detail(order_id)
    if not detail:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(detail)

@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    try:
        OrderService.cancel_order(order_id)
        return jsonify({"message": "Order cancelled"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    data = request.json
    status = data.get("status")
    try:
        OrderService.update_order_status(order_id, status)
        return jsonify({"message": f"Order status updated to {status}"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
