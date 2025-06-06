from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

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
    role = data.get('role')
    
    if not username or not email or not password:
        return jsonify({'error': 'Missing username, email or password'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 409
    #產生雜湊
    hashed_pw = generate_password_hash(password)

    #若是admin...................................
    if role=='admin':
        user = User(username=username, email=email, password=hashed_pw,role=role)
    else:
        user = User(username=username, email=email, password=hashed_pw)

    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Register success', 'user_id': user.id})

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

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role if hasattr(user, "role") else "user"})
    return jsonify({'access_token': access_token, 'user_id': user.id, 'role': user.role if hasattr(user, "role") else "user"})

# 登出
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # 若要做黑名單進階功能可加
    return jsonify({"message": "Logout success"})
