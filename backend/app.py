from dotenv import load_dotenv
load_dotenv()
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
from exceptions import NotFoundError, DuplicateError, UnauthorizedError, ForbiddenError
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_cors import CORS
import os
import sys
from datetime import timedelta
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
def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["http://localhost:3000","https://ecommerce-frontend-latest.onrender.com"])

    # 預設用正式資料庫
    
    #app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI_LOCALHOST")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    print("Flask SQLALCHEMY_DATABASE_URI = ", os.environ.get("SQLALCHEMY_DATABASE_URI_LOCALHOST"))
    
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)  # access token 60分
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)     # refresh token 7天
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "your_default_jwt_key")

    Swagger(app, template=swagger_template)


    # 如果有測試用 config 傳進來，會覆蓋預設設定
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    
    # ====== 全域 error handler 依 Exception 分類 ======
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
        return "Ecommerce API is running!"
    # ===========  註冊 Blueprint  =======  
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(carts_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(discount_bp)
    app.register_blueprint(linemessage_bp)
    JWTManager(app)

    return app

# 只在本機執行才會啟動 Flask 伺服器
if __name__ == '__main__':
    
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)