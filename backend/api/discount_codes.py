from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.decorate import admin_required
from service.discount_service import DiscountService
from datetime import datetime
from models import DiscountCode
discount_bp = Blueprint('discount_codes', __name__, url_prefix='/discount_codes')

@discount_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_discount_code():
    """
    管理員新增折扣碼
    """
    data = request.get_json()
    code = data.get("code")
    discount = data.get("discount")
    amount = data.get("amount")
    product_id = data.get("product_id")
    min_spend = data.get("min_spend")
    valid_from = data.get("valid_from")
    valid_to = data.get("valid_to")
    usage_limit = data.get("usage_limit")
    per_user_limit = data.get("per_user_limit")
    description = data.get("description")

    # 必填檢查
    if not code or (discount is None and amount is None) or not valid_from or not valid_to:
        return jsonify({"error": "缺少必填欄位"}), 400
    if discount and amount:
        return jsonify({"error": "discount 與 amount 二擇一"}), 400

    try:
        valid_from = datetime.fromisoformat(valid_from)
        valid_to = datetime.fromisoformat(valid_to)
    except Exception:
        return jsonify({"error": "日期格式錯誤，請用 YYYY-MM-DDTHH:MM:SS"}), 400

    try:
        dc = DiscountService.create_discount_code(
            code=code,
            discount=discount,
            amount=amount,
            product_id=product_id,
            min_spend=min_spend,
            valid_from=valid_from,
            valid_to=valid_to,
            usage_limit=usage_limit,
            per_user_limit=per_user_limit,
            description=description
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(dc.to_dict()), 201
@discount_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def list_discount_codes():
    """
    查詢所有折扣碼（admin only）
    ---
    tags:
      - discount_codes
    security:
      - Bearer: []
    responses:
      200:
        description: 折扣碼列表
        schema:
          type: array
          items:
            type: object
    """
    codes = DiscountCode.query.order_by(DiscountCode.id.desc()).all()
    return jsonify([c.to_dict() for c in codes]), 200

@discount_bp.route('/<int:code_id>/deactivate', methods=['PATCH'])
@jwt_required()
@admin_required
def deactivate_discount_code(code_id):
    """
    停用折扣碼（admin only）
    ---
    tags:
      - discount_codes
    parameters:
      - in: path
        name: code_id
        type: integer
        required: true
    responses:
      200:
        description: 停用成功
        schema:
          type: object
      404:
        description: 折扣碼不存在
    """
    code = DiscountCode.query.get(code_id)
    if not code:
        return jsonify({"error": "折扣碼不存在"}), 404
    DiscountService.deactivate_discount_code(code)
  
    return jsonify(code.to_dict()), 200
