from models import db, User,PasswordResetToken
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from exceptions import DuplicateError, UnauthorizedError,NotFoundError
import secrets
from datetime import datetime, timedelta
from utils.send_email import send_email

class UserService:
    @staticmethod
    def create(email, password, full_name=None, address=None, phone=None, role="user"):
        if not email or not password:
            raise ValueError("missing email or password")
        if User.query.filter_by(email=email).first():
            raise DuplicateError("Email already exists")
        created_at = datetime.now()
        hashed_pw = generate_password_hash(password)
        user = User(
            email=email,
            password=hashed_pw,
            full_name=full_name,
            address=address,
            phone=phone,
            created_at=created_at,  
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def login(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            raise UnauthorizedError('Invalid email or password')
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )
        return {"access_token": access_token, "user_id": user.id, "role": user.role}
    @staticmethod
    def send_reset_link(user_id):
          # 產生安全亂數 token
        token = secrets.token_urlsafe(32)
        expire = datetime.now() + timedelta(hours=1)

        # 寫入 token 表
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expire_at=expire,
            used=False
        )
        db.session.add(reset_token)
        db.session.commit()
        # 發送重設信
        reset_link = f"https://ecommerce-frontend-latest.onrender.com/login/reset_password?token={token}"
        user = User.get_by_user_id(user_id)
        
        if user and user.email:
            subject = "【Nerd.com】密碼重設連結"
            content = f"請點擊以下連結重設密碼：<br><a href='{reset_link}'>{reset_link}</a>"
            send_email(user.email, subject, content)

        return reset_link

    @staticmethod
    def reset_password(token,new_password):
       
        # 查找尚未使用且未過期的 token
        reset_token = PasswordResetToken.get_by_token(token)
        
        if not reset_token or reset_token.expire_at < datetime.now():
            raise ValueError("Reset link is invalid or expired")

        user = User.get_by_user_id(reset_token.user_id)
        if not user:
            raise ValueError("User not found")

        if generate_password_hash(new_password)==user.password:
            raise DuplicateError("rest password can not be the same")
        
        # 設定新密碼並註銷 token
        user.password = generate_password_hash(new_password)
        reset_token.used = True
        db.session.commit()
        return user
    @staticmethod
    def update_user_info(user_id,full_name=None,address=None,phone=None):
       
        user = User.get_by_user_id(user_id=user_id)
        if not user:
            raise NotFoundError("User not found")
        if full_name:
            user.full_name = full_name
        if address:
            user.address = address
        if phone:
            user.phone = phone
        db.session.commit()
        return user
    
