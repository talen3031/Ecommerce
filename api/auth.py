from flask import Blueprint, request, jsonify
from flask_jwt_extended import  jwt_required
from models import db, User
from service.user_service import UserService

auth_bp = Blueprint('auth', __name__)

# 會員註冊
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    會員註冊
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: RegisterRequest
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "newuser"
            email:
              type: string
              example: "user@example.com"
            password:
              type: string
              example: "abc12345"
    responses:
      200:
        description: 註冊成功
        schema:
          properties:
            message:
              type: string
              example: "Register success"
            user_id:
              type: integer
              example: 1
      400:
        description: 缺少欄位
        schema:
          properties:
            error:
              type: string
              example: "Missing username, email or password"
      409:
        description: 帳號或信箱已存在
        schema:
          properties:
            error:
              type: string
              example: "Username or email already exists"
    """
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role','user')
    full_name = data.get('full_name',None) 
    address = data.get('address',None) 
    phone = data.get('phone',None) 
    try:
      user = UserService.create(username = username, 
                            email = email, 
                            password = password, 
                            full_name = full_name, 
                            address = address, 
                            phone = phone, 
                            role = role)
    except ValueError as e:
        # 檢查訊息內容決定 400 or 409
        msg = str(e)
        code = 409 if "already exists" in msg else 400
        return jsonify({"error": msg}), code
    
    return jsonify({'message': 'Register success', 'user_id': user.id}), 201

# 登入
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    會員登入
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: LoginRequest
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "newuser"
            password:
              type: string
              example: "abc12345"
    responses:
      200:
        description: 登入成功
        schema:
          properties:
            access_token:
              type: string
              example: "jwt.token...."
            user_id:
              type: integer
              example: 1
            role:
              type: string
              example: "user"
      400:
        description: 缺少欄位
        schema:
          properties:
            error:
              type: string
              example: "Missing username or password"
      401:
        description: 帳號或密碼錯誤
        schema:
          properties:
            error:
              type: string
              example: "Invalid username or password"
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    try:
        result = UserService.login(username, password)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401  # 401 Unauthorized
# 登出
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # 若要做黑名單進階功能可加
    return jsonify({"message": "Logout success"})
