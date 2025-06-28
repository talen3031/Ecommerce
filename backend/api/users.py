from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.decorate import admin_required
from models import db, User 
from service.user_service import UserService 
from service.product_service import ProductService
users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    查詢單一用戶資訊（需登入）
    ---
    tags:
      - users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
    responses:
      200:
        description: 用戶資訊
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              example: "john@example.com"
            role:
              type: string
              example: "user"
            created_at:
              type: string
              format: date-time
              example: "2024-03-20T10:00:00Z"
      403:
        description: 僅能查詢本人
        schema:
          properties:
            error:
              type: string
              example: "you only can search your own information"
      404:
        description: 用戶不存在
        schema:
          properties:
            error:
              type: string
              example: "User not found"
    """
    # 只允許本人查自己
    
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "you only can search your own information"}), 403

    user = User.get_by_user_id(user_id=user_id)

    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404
    

#查詢所有使用者
@users_bp.route('/all', methods=['GET'])
@admin_required
def get_all_user():
    """
    查詢全部用戶資訊（需管理員）
    ---
    tags:
      - users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
    responses:
      200:
        description: 用戶資訊列表
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              example: "john@example.com"
            role:
              type: string
              example: "user"
            created_at:
              type: string
              format: date-time
              example: "2024-03-20T10:00:00Z"
    """
    users = User.query.all()
    result = []
    
    for user in users:
        result.append(user.to_dict())
    
    return jsonify(result)

# 修改會員資料
@users_bp.route('/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    """
    修改會員資料（需登入）
    ---
    tags:
      - users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            full_name:
              type: string
              description: 新的姓名
            address:
              type: string
              description: 新的地址
            phone:
              type: string
              description: 新的電話
    responses:
      200:
        description: 修改後的會員資料
        schema:
          type: object
      403:
        description: 僅能修改本人
        schema:
          properties:
            error:
              type: string
              example: "you only can update your own information"
      404:
        description: 用戶不存在
        schema:
          properties:
            error:
              type: string
              example: "User not found"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "you only can update your own information"}), 403
    res = request.get_json() or {}
    full_name = res.get('full_name')
    phone = res.get('phone')
    address = res.get('address')
    user = UserService.update_user_info(user_id, full_name=full_name, address=address, phone=phone)
    return jsonify(user.to_dict())

@users_bp.route('/<int:user_id>/recommend', methods=['GET'])
@jwt_required()
def recommend_for_user(user_id):
    """
    個人化推薦（依購買紀錄 推薦同類別的熱賣商品）
    ---
    tags:
      - users
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: query
        name: limit
        type: integer
        required: false
        description: 推薦幾個商品，預設5
    responses:
      200:
        description: 推薦商品列表
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              title:
                type: string
                example: "iPhone 99"
              price:
                type: number
                example: 9999
              description:
                type: string
                example: "旗艦手機"
              category_id:
                type: integer
                example: 1
              image:
                type: string
                example: "http://img"
      403:
        description: 權限不足
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Permission denied"
    """

    # 僅允許本人查詢
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    limit = request.args.get('limit', 5, type=int)
    products = ProductService.recommend_for_user(user_id, limit)
    return jsonify([p.to_dict() for p in products])