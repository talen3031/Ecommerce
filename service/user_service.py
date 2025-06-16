from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from exceptions import DuplicateError, UnauthorizedError
class UserService:
    @staticmethod
    def create(username, email, password, full_name=None, address=None, phone=None, role="user"):
        if not username or not email or not password:
            raise ValueError("missing username, email, password")
        # 加唯一性檢查
        if User.query.filter((User.username == username) | (User.email == email)).first():
            raise DuplicateError("Username or email already exists")
        
        hashed_pw = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_pw,
            full_name=full_name,
            address=address,
            phone=phone,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            raise UnauthorizedError('Invalid username or password')
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )
        return {"access_token": access_token, "user_id": user.id, "role": user.role}