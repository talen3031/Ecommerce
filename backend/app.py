# import logging

# class PollingFilter(logging.Filter):
#     def filter(self, record):
#         msg = record.getMessage()
#         # 過濾 /socket.io 所有請求
#         if "/socket.io/" in msg:
#             return False
#         return True

# logging.getLogger("werkzeug").addFilter(PollingFilter())
from flask import Flask, jsonify
from models import db
from api.products import products_bp
from api.users import users_bp
from api.carts import carts_bp
from api.orders import orders_bp
from api.auth import auth_bp
from api.upload import upload_bp
from api.discount_codes import discount_bp
from api.linemessage import linemessage_bp
from api.chat import chat_bp
from exceptions import NotFoundError, DuplicateError, UnauthorizedError, ForbiddenError
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from cache import cache
from flask_cors import CORS
import os
from config import config,get_current_config
import cloudinary
from ext_socketio import socketio

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Ecommerce API",
        "description": "API docs for Ecommerce Platform",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "請輸入 Bearer + 空格 + JWT 權杖（如：Bearer eyJ...）"
        }
    }
}

def create_app(config_name=None, test_config=None):
    app = Flask(__name__)

    # 1. 載入 config（優先以參數/環境變數決定環境）
    config_name = config_name or os.getenv('APP_CONFIG') or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    CurrentConfig = get_current_config()

    # ========== 啟動時印出環境相關設定 ==========
    def print_startup_config():
        print("========== 🚀 服務啟動參數 ===========")
        print(f"🌍 環境：{CurrentConfig.__name__}")
        print(f"🔗 FRONTEND_BASE_URL: {getattr(CurrentConfig, 'FRONTEND_BASE_URL', None)}")
        print(f"🖥️ BACKEND_BASE_URL: {getattr(CurrentConfig, 'BACKEND_BASE_URL', None)}")
        print(f"🗄️ DATABASE URI: {getattr(CurrentConfig, 'SQLALCHEMY_DATABASE_URI', None)}")
        print(f"⚙️ SQLALCHEMY_ENGINE_OPTIONS: {getattr(CurrentConfig, 'SQLALCHEMY_ENGINE_OPTIONS', None)}")
        print(f"🐞 DEBUG: {getattr(CurrentConfig, 'DEBUG', None)}")
        print("====================================")

    print_startup_config()
    # 2. CORS
    CORS(
        app,
        supports_credentials=True,
        origins=[
            "http://localhost:3000",
            "https://ecommerce-frontend-production-d012.up.railway.app"
        ]
    )

    # Cloudinary 初始化（只做一次）
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"]
    )
    # 3. cache & 其他初始化
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    #socket 
    socketio.init_app(app, cors_allowed_origins=[
            "http://localhost:3000",
            "https://ecommerce-frontend-production-d012.up.railway.app"
        ])
    # 4. Swagger 文件
    Swagger(app, template=swagger_template)

    # 5. 測試用 config 覆蓋
    if test_config:
        app.config.update(test_config)

    # 6. DB 初始化
    db.init_app(app)

    # 7. Blueprint 註冊
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(carts_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(discount_bp)
    app.register_blueprint(linemessage_bp)
    app.register_blueprint(chat_bp)
    JWTManager(app)

    # 8. 全域 error handler
    @app.errorhandler(DuplicateError)
    def handle_duplicate_error(e):
        return jsonify({"error": str(e)}), 409

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(e):
        return jsonify({"error": str(e)}), 401

    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(e):
        return jsonify({"error": str(e)}), 403

    @app.errorhandler(NotFoundError)
    def handle_notfound_error(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print("GLOBAL ERROR:", str(e).encode('utf-8', errors='replace').decode('utf-8'))
        print(traceback.format_exc())
        return jsonify({"error": f"GLOBAL ERROR: {str(e)}"}), 500

    @app.route('/')
    def index():
        return "Welcometo Raw type backend! \n Nginx is listening http://0.0.0.0:8080 \n API is running on http://127.0.0.1:8000 \n socketio is running on http://127.0.0.1:8001"

    return app
app = create_app() 

# 本地啟動
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)