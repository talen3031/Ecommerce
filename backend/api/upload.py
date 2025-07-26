import cloudinary.uploader
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/upload_image', methods=['POST'])
@jwt_required()
def upload_image():
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
    
