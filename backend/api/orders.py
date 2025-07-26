from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from service.order_service import OrderService
from service.audit_service import AuditService
from api.decorate import admin_required
from models import Order,User
from flask import Response

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# 查詢自己歷史訂單
@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_my_orders():
    """
    查詢目前登入者自己的歷史訂單（分頁）
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 頁碼
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: 每頁筆數
    responses:
      200:
        description: 訂單列表
        schema:
          type: object
          properties:
            orders:
              type: array
              items:
                type: object
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
            pages:
              type: integer
    """
    current_user_id = int(get_jwt_identity())
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    orders_page = OrderService.get_user_orders(current_user_id, page=page, per_page=per_page)

    result = [order.to_dict() for order in orders_page.items]
    return jsonify({
        "orders": result,
        "total": orders_page.total,
        "page": orders_page.page,
        "per_page": orders_page.per_page,
        "pages": orders_page.pages
    })


# 查詢訂單明細
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_detail(order_id):
    """
    查詢單一訂單明細
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: 訂單ID
    responses:
      200:
        description: 訂單明細
        schema:
          type: object
      404:
        description: 找不到訂單
    """
    detail = OrderService.get_order_detail(order_id)
    return jsonify(detail)

#admin查詢所有訂單
@orders_bp.route('/all', methods=['GET'])
@admin_required
def get_all_orders():
    """
    查詢所有訂單（管理員）
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 頁碼
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: 每頁筆數
    responses:
      200:
        description: 訂單列表
        schema:
          type: object
          properties:
            orders:
              type: array
              items:
                type: object
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
            pages:
              type: integer
      403:
        description: 權限不足
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    orders_page = OrderService.get_all_orders(page=page, per_page=per_page)

    result = [order.to_dict(include_user=True) for order in orders_page.items]
    return jsonify({
        "orders": result,
        "total": orders_page.total,
        "page": orders_page.page,
        "per_page": orders_page.per_page,
        "pages": orders_page.pages
    })

#取消訂單
@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """
    取消訂單
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: 訂單ID
    responses:
      200:
        description: 訂單已取消
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: 無法取消訂單
    """
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
    """
    修改訂單狀態（admin 或 該訂單用戶可操作）
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: 訂單ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              description: 新的訂單狀態
    responses:
      200:
        description: 狀態更新成功
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: 狀態更新失敗
      403:
        description: 權限不足
    """

    data = request.json
    status = data.get("status")

    # 取得目前登入者資訊
    current_user_id = int(get_jwt_identity())
    
    user = User.get_by_user_id(current_user_id)
    current_user_role = user.role

    # 查詢訂單
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # 權限檢查
    if current_user_role != "admin" and order.user_id != current_user_id:
        return jsonify({"error": "Permission denied"}), 403


    # 修改訂單狀態
    order = OrderService.update_order_status(order_id, status)

    # 日誌
    AuditService.log(
        user_id=current_user_id,
        action='update',
        target_type='order',
        target_id=order.id,
        description=f"update order: {order.to_dict()}"
    )

    return jsonify({"message": f"Order status updated to {status}"})

#admin only
@orders_bp.route('/<int:order_id>/shipping', methods=['PATCH'])
@admin_required
def update_shipping_info(order_id):
    """
    更新訂單寄送資訊（管理員專用）
    ---
    tags:
      - Orders
    summary: 部分更新訂單寄送資訊（admin）
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: 訂單ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            shipping_method:
              type: string
              example: "711"
              description: 配送方式 ('711', 'familymart' 等)
            recipient_name:
              type: string
              example: "王小明"
            recipient_phone:
              type: string
              example: "0912345678"
            store_name:
              type: string
              example: "台北松江南京門市"
    responses:
      200:
        description: 更新成功
        schema:
          type: object
          properties:
            id:
              type: integer
            order_id:
              type: integer
            shipping_method:
              type: string
            recipient_name:
              type: string
            recipient_phone:
              type: string
            store_name:
              type: string
      400:
        description: 沒有提供任何可更新欄位
        schema:
          properties:
            error:
              type: string
      403:
        description: 權限不足或狀態不可改
        schema:
          properties:
            error:
              type: string
      404:
        description: 找不到訂單或寄送資訊
        schema:
          properties:
            error:
              type: string
    """
    order = Order.get_by_order_id(order_id=order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.json or {}

    # 至少要有一個欄位才 patch
    updatable_fields = ['shipping_method', 'recipient_name', 'recipient_phone', 'store_name']
    if not any(data.get(field) for field in updatable_fields):
        return jsonify({"error": "請至少傳一個可更新欄位"}), 400

    shipping_data={}
    for field in updatable_fields:
        if data.get(field):
            shipping_data[field]=data.get(field) 
    # 建議：user id 也帶給 Service 做審計
    admin_user_id = int(get_jwt_identity())
    shipping = OrderService.update_shipping_info(order_id, shipping_data,admin_user_id)

    return jsonify(shipping.to_dict()), 200




#訪客查詢訂單明細
@orders_bp.route('/guest/<string:guest_id>/<int:order_id>', methods=['GET'])
def get_guest_order_detail(guest_id, order_id):
    """
    訪客查詢自己的單筆訂單（用GET＋query string, 需帶 email 參數）
    範例：/orders/guest/<guest_id>/<order_id>?email=xxx@example.com
    """
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "email is required"}), 400
    detail = OrderService.get_order_detail_guest(order_id, guest_id, email)
    return jsonify(detail)

@orders_bp.route('/guest/<string:guest_id>/<int:order_id>/cancel', methods=['POST'])
def cancel_guest_order(guest_id, order_id):
    email = request.json.get("email")
    if not guest_id or not email:
        return jsonify({"error": "缺少 guest_id 或 email"}), 400
    order = OrderService.cancel_order_guest(order_id, guest_id, email)


    # 日誌紀錄
    AuditService.log(
        user_id=None,
        action='guest_cancel',
        target_type='order',
        target_id=order.id,
        description=f"[guest] cancel order: {order.to_dict()}"
    )

    return jsonify({"message": "Order cancelled"})
