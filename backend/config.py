# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
class BaseConfig:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_DATABASE_URI_LOCALHOST = os.getenv("SQLALCHEMY_DATABASE_URI_LOCALHOST")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # LINE BOT / LOGIN
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    LINE_LOGIN_CHANNEL_ID = os.getenv("LINE_LOGIN_CHANNEL_ID")
    LINE_LOGIN_CHANNEL_SECRET = os.getenv("LINE_LOGIN_CHANNEL_SECRET")
    LINE_LOGIN_CALLBACK_URL = os.getenv("LINE_LOGIN_CALLBACK_URL")
    LINEBOT_ADMIN_EMAIL = os.getenv("LINEBOT_ADMIN_EMAIL")
    LINEBOT_ADMIN_PASSWORD = os.getenv("LINEBOT_ADMIN_PASSWORD")

    # Email/Resend/Sendgrid
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# 新增通用參數（如果你需要跨檔案都可共用的話）
    FRONTEND_BASE_URL = None
    BACKEND_BASE_URL = None

    # 其他設定可陸續加進來...

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # 可以自行選擇用哪個資料庫（local時）
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI_LOCALHOST", BaseConfig.SQLALCHEMY_DATABASE_URI)
    FRONTEND_BASE_URL = "http://localhost:3000"
    BACKEND_BASE_URL = "http://localhost:5000"
class ProductionConfig(BaseConfig):
    DEBUG = False
    FRONTEND_BASE_URL = "https://ecommerce-frontend-latest.onrender.com/"
    BACKEND_BASE_URL = "https://ecommerce-backend-latest-6fr5.onrender.com/"
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI_TEST", "postgresql://postgres:talen168168@localhost:5432/Ecommerce_test")
    JWT_SECRET_KEY = 'testkey'

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,  # 這一定要有
    "default": DevelopmentConfig,
}

def get_current_config():
    import os
    config_name = os.getenv("FLASK_ENV", "default")
    return config[config_name]