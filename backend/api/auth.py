from flask import Blueprint, request, jsonify
from service.user_service import UserService
from service.audit_service import AuditService
from models import User
from flask_jwt_extended import jwt_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 會員註冊
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    會員註冊
    ---
    tags:
      - auth
    summary: 新增會員帳號
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "user@example.com"
            password:
              type: string
              example: "abc12345"
            role:
              type: string
              example: "user"
            full_name:
              type: string
              example: "張三"
            address:
              type: string
              example: "台北市中山區"
            phone:
              type: string
              example: "0912345678"
    responses:
      201:
        description: 註冊成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Register success"
            user_id:
              type: integer
              example: 3
      400:
        description: 缺少欄位
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing email or password"
      409:
        description: 信箱已存在
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Email already exists"
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    full_name = data.get('full_name', None)
    address = data.get('address', None)
    phone = data.get('phone', None)
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
  

    user = UserService.create(
        email=email,
        password=password,
        full_name=full_name,
        address=address,
        phone=phone,
        role=role
    )
    # 日誌
    AuditService.log(
        user_id=user.id,
        action='register',
        target_type='user',
        target_id=user.id,
        description=f"User registered: email={email}"
    )
    return jsonify({'message': 'Register success', 'user_id': user.id}), 201

# 登入
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    會員登入
    ---
    tags:
      - auth
    summary: 會員登入取得 JWT
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "user@example.com"
            password:
              type: string
              example: "abc12345"
    responses:
      200:
        description: 登入成功
        schema:
          type: object
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
          type: object
          properties:
            error:
              type: string
              example: "Missing email or password"
      401:
        description: 帳號或密碼錯誤
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid email or password"
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        result = UserService.login(email, password)
        # 登入成功日誌
        AuditService.log(
            user_id=result["user_id"],
            action='login',
            target_type='user',
            target_id=result["user_id"],
            description=f"User login success: email={email}"
        )
        return jsonify(result), 200

    except Exception as e:
        # 登入失敗日誌
        user = User.get_by_email(email)
        AuditService.log(
            user_id=user.id if user else None,
            action='login_fail',
            target_type='user',
            target_id=user.id if user else None,
            description=f"User login failed: email={email}, error={str(e)}"
        )
        return jsonify({'error': str(e)}), 401

# 登出
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logout success"})

# 忘記密碼：發送重設密碼連結
@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    """
    忘記密碼：發送重設密碼連結
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email]
          properties:
            email:
              type: string
              example: "user@example.com"
    responses:
      200:
        description: 如果信箱存在會寄出重設信
    """
    data = request.json
    email = data.get('email')
    user = User.get_by_email(email=email)
    if not user:
        # 防止暴露用戶資訊，直接回覆
        return jsonify({"message": "If this email exists, a reset link will be sent"}), 200

    reset_link = UserService.send_reset_link(user_id=user.id)
    return jsonify({"message": f"If this email exists, a reset link will be sent"}), 200

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """
    重設密碼
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [token, new_password]
          properties:
            token:
              type: string
              example: "xxxx"
            new_password:
              type: string
              example: "abc12345"
    responses:
      200:
        description: 密碼已重設
      400:
        description: token 無效或已過期
    """
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({"error": "Missing token or new password"}), 400

    UserService.reset_password(token, new_password)
    return jsonify({"message": "Password has been reset"}), 200
