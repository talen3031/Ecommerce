from dotenv import load_dotenv
load_dotenv()
import cloudinary
import cloudinary.uploader
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.decorate import admin_required
# Cloudinary 設定（只要設定一次即可）
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


upload_bp = Blueprint('upload', __name__, url_prefix='/upload')
# 查詢所有商品
@upload_bp.route('/upload_image', methods=['POST'])
@jwt_required()
def upload_image():
    """
    上傳商品圖片至 Cloudinary
    需注意 header: Authorization: Bearer <JWT>
    需注意 form-data: image = <file>
    """
    if "image" not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        result = cloudinary.uploader.upload(file)
        image_url = result.get("secure_url")
        return jsonify({"url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
