from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.order_service import OrderService
from service.audit_service import AuditService

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# 查詢我的歷史訂單
@orders_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_orders(user_id):
   

    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403
    
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    orders_page = OrderService.get_user_orders(user_id, page=page, per_page=per_page)

    result = [order.to_dict() for order in orders_page.items]
    return jsonify({
        "orders": result,
        "total": orders_page.total,
        "page": orders_page.page,
        "per_page": orders_page.per_page,
        "pages": orders_page.pages
    })

# 查詢訂單明細
@orders_bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):


    detail = OrderService.get_order_detail(order_id)

    return jsonify(detail)
#取消訂單
@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    order = OrderService.cancel_order(order_id)
    user_id = get_jwt_identity()
   
    AuditService.log(
        user_id=user_id,
        action='cancel',
        target_type='order',
        target_id=order.id,
        description=f"cancel order: {order.to_dict()}"
    )
    return jsonify({"message": "Order cancelled"})

#修改訂單狀態
@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    data = request.json
    status = data.get("status")
    order = OrderService.update_order_status(order_id, status)
    
    #寫入日誌
    user_id = get_jwt_identity()
    AuditService.log(
        user_id=user_id,
        action='update',
        target_type='order',
        target_id=order.id,
        description=f"update order: {order.to_dict()}"
    )

    return jsonify({"message": f"Order status updated to {status}"})

