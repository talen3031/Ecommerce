
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.decorate import admin_required
from models import db, User 


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

    user = db.session.get(User, user_id)
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "address": user.address,
            "phone": user.phone,
            "created_at": str(user.created_at) if user.created_at else None,
            "role": user.role 
        })
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
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "address": user.address,
            "phone": user.phone,
            "created_at": str(user.created_at) if user.created_at else None,
            "role": user.role 
        })
    return jsonify(result)
