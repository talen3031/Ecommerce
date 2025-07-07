from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    images = db.Column(JSONB)
    is_active = db.Column(db.Boolean, default=True)  # True: 上架, False: 下架
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    __table_args__ = (
        db.UniqueConstraint('title', 'category_id', name='unique_product_title_category'),
    )

    @classmethod
    def get_by_product_id(cls, product_id):
        return cls.query.filter_by(id=product_id).first()
    @classmethod
    def get_active_by_product_id(cls, product_id):
        return cls.query.filter_by(id=product_id, is_active=True).first()
    
    @classmethod
    def get_by_category_id(cls, category_id):
        return cls.query.filter_by(category_id=category_id).all()

    @classmethod
    def get_by_keyword(cls, keyword):
        return cls.query.filter(cls.title.ilike(f"%{keyword}%")).all()

    @classmethod
    def get_by_min_price(cls, min_price):
        return cls.query.filter(cls.price >= min_price).all()

    @classmethod
    def get_by_max_price(cls, max_price):
        return cls.query.filter(cls.price <= max_price).all()

    @classmethod
    def get_by_price_range(cls, min_price, max_price):
        return cls.query.filter(cls.price >= min_price, cls.price <= max_price).all()

    def get_current_sale(self):
        now = datetime.now()
        for sale in self.sales:
            if sale.start_date <= now <= sale.end_date:
                return sale
        return None
    def get_final_price(self):
        sale = self.get_current_sale()
        if sale:
            return float(self.price) * sale.discount
        else:
            return float(self.price)

    def to_dict(self):
        now = datetime.now()
        current_sale = None
        sale_price = None
        sale_description = None

        # 判斷是否有特價
        for sale in self.sales:
            if sale.start_date <= now <= sale.end_date:
                current_sale = sale
                sale_price = float(self.price) * sale.discount
                sale_description = sale.description
                break

        return {
            "id": self.id,
            "title": self.title,
            "price": float(self.price),  # 原價
            "description": self.description,
            "category_id": self.category_id,
            "images": self.images,
            "on_sale": current_sale is not None,
            "sale_price": round(sale_price, 2) if sale_price else None,  # 折扣後價格
            "sale_discount": current_sale.discount if current_sale else None,
            "sale_start": current_sale.start_date.isoformat() if current_sale else None,
            "sale_end": current_sale.end_date.isoformat() if current_sale else None,
            "sale_description": sale_description,
            "sale_id": current_sale.id if current_sale else None,
            "is_active": self.is_active,
        }


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    full_name = db.Column(db.String(255))
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')
 
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "address": self.address,
            "phone": self.phone,
            "created_at": str(self.created_at) if self.created_at else None,
            "role": self.role
        }
ORDER_STATUS = [
        'pending',
        'paid',
        'processing',
        'shipped',
        'delivered',
        'cancelled',
        'returned',
        'refunded'
    ]
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_date = db.Column(db.DateTime)
    total = db.Column(db.Numeric)
    status = db.Column(Enum(*ORDER_STATUS, name="order_status_enum"), default='pending', nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    

    @classmethod
    def get_by_order_id(cls, order_id):
        return cls.query.filter_by(order_id=order_id).first()
   
    #查詢某用戶所有訂單（依日期排序）
    @classmethod
    def get_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.order_date.desc()).all()

    def to_dict(self, include_user=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "total": float(self.total) if self.total is not None else 0.0,
            "status": self.status
        }
        if include_user:
            data["user"] = self.user.to_dict() if self.user else None
        return data
    
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric, nullable=False)
    order = db.relationship('Order', backref=db.backref('order_items', lazy=True, cascade='all, delete-orphan'))
    product = db.relationship('Product')
    __table_args__ = (
        db.UniqueConstraint('order_id', 'product_id', name='unique_order_product'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": float(self.price) if self.price else 0.0,
        }
    
    @classmethod
    def get_by_order_id(cls, order_id):
        return cls.query.filter_by(order_id=order_id).all()
    
CART_STATUS=[
    "active",
    "checked_out"
]
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)
    status = db.Column(Enum(*CART_STATUS, name="cart_status_enum"), default='active', nullable=False)
    user = db.relationship('User', backref=db.backref('carts', lazy=True))
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "status": self.status,
        }

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    cart = db.relationship('Cart', backref=db.backref('cart_items', lazy=True, cascade='all, delete-orphan'))
    product = db.relationship('Product')
    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
    )
    def to_dict(self):
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id ,
            "quantity": self.quantity,
        }
    
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False) # 'add', 'delete', 'update'
    target_type = db.Column(db.String(50), nullable=False) # 'product', 'user', ...
    target_id = db.Column(db.Integer, nullable=True) # ex: product_id
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User')


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token, used=False).first()
    
    #找到該user最新的token
    @classmethod
    def get_user_newest_token(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id.desc()).first()
    

class ProductOnSale(db.Model):
    __tablename__ = 'products_on_sale'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    discount = db.Column(db.Float, nullable=False)  # 例如 0.8 代表 8 折
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)

    product = db.relationship('Product', backref=db.backref('sales', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "discount": self.discount,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "description": self.description,
        }