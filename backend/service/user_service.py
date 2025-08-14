from models import db, User,PasswordResetToken
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token
from exceptions import DuplicateError, UnauthorizedError,NotFoundError
import secrets

from datetime import datetime, timedelta
from utils.send_email import send_email
from config import get_current_config
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from service.audit_service import AuditService
from werkzeug.security import generate_password_hash

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
            additional_claims={"user_id": user.id,
                                "role": user.role}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "role": user.role
        }
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
        base_url = get_current_config().FRONTEND_BASE_URL
        reset_link = f"{base_url.rstrip('/')}/reset_password?token={token}"
        user = User.get_by_user_id(user_id)
        
        if user and user.email:
            subject = "【Nerd.com】密碼重設連結"
            content = f"請點擊以下連結重設密碼：<br><a href='{reset_link}'>{reset_link}</a>"
            try:
                send_email(user.email, subject, content)
            except Exception as e:
                print("重設密碼 寄信失敗", e)
                import traceback; traceback.print_exc()
            print("重設密碼 寄信成功 reset_link:",reset_link)

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
    
    @staticmethod
    def login_with_google_id_token(credential: str):
        """
        驗證 Google ID Token，找/建使用者，回傳我方 JWT 與基本資訊。
        只做商業邏輯，不處理 HTTP Cookie（交給 route 設置）。
        """
        if not credential:
            raise ValueError("Missing credential")

        # 驗證 Google ID Token（簽章/時效/受眾）
        info = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            get_current_config().GOOGLE_CLIENT_ID
        )
        sub = info.get("sub")
        email = info.get("email")
        email_verified = info.get("email_verified", False)
        name = info.get("name")

        if not email or not email_verified:
            raise UnauthorizedError("Email not verified by Google")

        # 先用 google_sub 找，其次用 email 找
        user = None
        if sub:
            user = User.query.filter_by(google_sub=sub).first()
        if not user and email:
            user = User.query.filter_by(email=email).first()

        # 更新或建立使用者
        if user:
            changed = False
            if not getattr(user, "google_sub", None) and sub:
                user.google_sub = sub
                user.oauth_provider = "google"
                changed = True
            if hasattr(user, "full_name") and not user.full_name and name:
                user.full_name = name
                changed = True
            if changed:
                db.session.commit()
        else:
            # 全新使用者：建立本地帳號（給隨機密碼）
            pwd = secrets.token_urlsafe(16)
            hashed = generate_password_hash(pwd)
            user = User(
                email=email,
                password=hashed,
                role="user",
                full_name=name if hasattr(User, "full_name") else None,
                oauth_provider="google",
                google_sub=sub
            )
            db.session.add(user)
            db.session.commit()

        # 簽發系統自己的 JWT（沿用既有風格）
        tokens = {
            "access_token": create_access_token(
                identity=str(user.id),
                additional_claims={"user_id": user.id, "role": user.role}
            ),
            "refresh_token": create_refresh_token(identity=str(user.id)),
            "user_id": user.id,
            "role": user.role,
        }

        # 審計（失敗不影響主流程）
        try:
            AuditService.log(
                user_id=user.id,
                action='login_google',
                target_type='user',
                target_id=user.id,
                description=f"Google login success: {email}"
            )
        except Exception:
            pass

        return tokens