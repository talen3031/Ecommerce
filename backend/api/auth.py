from flask import Blueprint, request, jsonify,make_response
from service.user_service import UserService
from service.audit_service import AuditService
from models import User
# refresh（從 cookie 讀 token）
from flask_jwt_extended import jwt_required,decode_token,create_access_token
from flask import Blueprint, request, jsonify, make_response
from config import get_current_config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
# auth.py

@auth_bp.route('/google', methods=['POST'])
def login_with_google():
    """
    前端送上 Google Identity Services 取得的 ID Token（credential）
    body: { "credential": "<Google ID Token>" }
    回傳：{ access_token, user_id, role }，並在 Cookie 設置 refresh_token
    """
    data = request.get_json() or {}
    credential = data.get("credential")
    if not credential:
        # 交給全域 ValueError handler 回 400
        raise ValueError("Missing credential")

    tokens = UserService.login_with_google_id_token(credential)

    # 設置 HttpOnly refresh_token Cookie（本地 secure=False；正式請 True + samesite 視網域）
    resp = make_response(jsonify({
        "access_token": tokens["access_token"],
        "user_id": tokens["user_id"],
        "role": tokens["role"]
    }))
    resp.set_cookie(
        "refresh_token",
        tokens["refresh_token"],
        httponly=True,
        secure=True,        # 本地 False；上線請改 True（需 HTTPS）
        samesite="Strict",   # 多網域可改 'Lax' 或 'None'（需 secure=True）
        max_age=7*24*60*60
    )
    return resp



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
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        # result: { "access_token": ..., "refresh_token": ..., "user_id": ..., "role": ... }
        result = UserService.login(email, password)   # 你要讓 login 支援 email
        # 寫入日誌
        AuditService.log(
            user_id=result["user_id"],
            action='login',
            target_type='user',
            target_id=result["user_id"],
            description=f"User login success: email={email}"
        )
        # 把 refresh token 寫到 HttpOnly Cookie
        resp = make_response(jsonify({
            "access_token": result["access_token"],
            "user_id": result["user_id"],
            "role": result["role"]
        }))
        resp.set_cookie(
            "refresh_token",
            result["refresh_token"],
            httponly=True,
            secure=False,         # 開發用 False，正式記得 True（需要 https）
            samesite='Strict',    # 如果多域名可設 Lax/None
            max_age=7*24*60*60    # 7天
        )
        return resp

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


#refresh token 
@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'Missing refresh token'}), 401
    try:
        #decoded = decode_token(refresh_token, allow_expired=False, algorithms=["HS256"])

        decoded = decode_token(refresh_token)
        user_id = decoded['sub']
        user = User.get_by_user_id(user_id)
        if not user:
          return jsonify({'error': 'User not found'}), 401
        access_token = create_access_token(
                                  identity=str(user_id),
                                  additional_claims={"role": user.role, "user_id": user.id}
                              )
        return jsonify({"access_token": access_token,
                        "user_id": user_id,
                        "role": user.role } )
    except Exception as e:
        print(e)
        return jsonify({'error': 'Invalid or expired refresh token'}), 401

# 登出
@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = make_response(jsonify({"message": "Logout success"}))
    resp.delete_cookie("refresh_token")
    return resp

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
        return jsonify({"message": "If this email exists... a reset link will be sent"}), 200

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
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Missing token or new password"}), 400

    UserService.reset_password(token, new_password)
    return jsonify({"message": "Password has been reset"}), 200

