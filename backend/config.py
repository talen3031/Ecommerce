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
     # SQLAlchemy 連線池設定
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 2,         # 每個 Gunicorn worker 預留 2 條連線
        "max_overflow": 2,      # 額外允許臨時 2 條
        "pool_recycle": 300,    # 300 秒強制回收，避免閒置被 Railway 收掉
        "pool_pre_ping": True,  # 取用前先測試，壞連線會自動丟掉
    }
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
    LINE_LOGIN_CALLBACK_URL = None
    LINEBOT_ADMIN_EMAIL = os.getenv("LINEBOT_ADMIN_EMAIL")
    LINEBOT_ADMIN_PASSWORD = os.getenv("LINEBOT_ADMIN_PASSWORD")
    # GOOGLE AUTH
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")  # 若日後改用授權碼流程會用到
    GOOGLE_REDIRECT_URI =  None
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
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI_LOCALHOST", "postgresql://postgres:talen168168@localhost:5432/Ecommerce")

    FRONTEND_BASE_URL = "http://localhost:3000"
    BACKEND_BASE_URL = "http://localhost:5000"
    
    GOOGLE_REDIRECT_URI = BACKEND_BASE_URL + "/auth/google/callback"
    LINE_LOGIN_CALLBACK_URL = BACKEND_BASE_URL + "/linemessage/bliding"
    
class ProductionConfig(BaseConfig):
    DEBUG = False
    FRONTEND_BASE_URL = "https://ecommerce-frontend-production-d012.up.railway.app"
    BACKEND_BASE_URL = "https://ecommerce-backend-production-a470.up.railway.app"
    
    GOOGLE_REDIRECT_URI = BACKEND_BASE_URL + "/auth/google/callback"
    LINE_LOGIN_CALLBACK_URL = BACKEND_BASE_URL + "/linemessage/bliding"

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
    #config_name = os.getenv("FLASK_ENV", "default")
    config_name = os.getenv('APP_CONFIG') or os.getenv('FLASK_ENV', 'default')
    return config[config_name]