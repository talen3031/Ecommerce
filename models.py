from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

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
    image = db.Column(db.String(255))
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    __table_args__ = (
        db.UniqueConstraint('title', 'category_id', name='unique_product_title_category'),
    )

    @classmethod
    def search(cls, keyword=None, category_id=None, min_price=None, max_price=None):
        query = cls.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        if keyword:
            query = query.filter(cls.title.ilike(f"%{keyword}%"))
        if min_price is not None:
            query = query.filter(cls.price >= min_price)
        if max_price is not None:
            query = query.filter(cls.price <= max_price)
        return query.all()

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
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

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
    #查詢訂單明細
    @classmethod
    def get_items_by_order_id(cls, order_id):
        """
        取得指定訂單（order_id）的所有明細（含商品資料）
        """
        return cls.query.filter_by(order_id=order_id).all()

    #查詢某用戶所有訂單（依日期排序）
    @classmethod
    def for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.order_date.desc()).all()

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

    @classmethod
    def count_total_price(cls, user_id,statuses=None):
        from models import Order  # 避免循環 import
        # 先查該 user_id 的所有 Order id
        query = db.session.query(Order.id).filter(Order.user_id == user_id)
        
        #若有指定要哪種訂單狀態
        if statuses:
            if isinstance(statuses, str):
                statuses = [statuses]
            query = query.filter(Order.status.in_(statuses))
        user_order_ids = query

        # 對 order_items 進行金額總和（單價*數量）
        total = db.session.query(
            func.coalesce(func.sum(cls.price * cls.quantity), 0)
        ).filter(cls.order_id.in_(user_order_ids)).scalar()
        return float(total) if total else 0.0

class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')
    user = db.relationship('User', backref=db.backref('carts', lazy=True))

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
