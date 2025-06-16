from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Cart, CartItem, Product, Order, OrderItem
from datetime import datetime
from service.cart_service import CartService


carts_bp = Blueprint('carts', __name__, url_prefix='/cart')
#查詢購物車

@carts_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_cart(user_id):
    """
    查詢單一用戶購物車（需登入）
    ---
    tags:
      - carts
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
    responses:
      200:
        description: 購物車資訊
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: "Product Name"
                  price:
                    type: number
                    example: 99.99
                  quantity:
                    type: integer
                    example: 2
                  subtotal:
                    type: number
                    example: 199.98
            total:
              type: number
              example: 199.98
      403:
        description: 僅能查詢本人
        schema:
          properties:
            error:
              type: string
              example: "Permission denied"
      404:
        description: 用戶不存在
        schema:
          properties:
            error:
              type: string
              example: "User not found"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    cart = CartService.get_cart(user_id=user_id)
    if not cart:
        return jsonify({"cart": None, "items": []})
    return jsonify(cart)

#加入商品至購物車
@carts_bp.route('/<int:user_id>/add', methods=['POST'])
@jwt_required()
def add_to_cart(user_id):
    """
    加入商品至購物車（需登入）
    ---
    tags:
      - carts
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: Product_info
          required:
            - title
            - price
            - category_id
          properties:
            title:
              type: string
              example: "iPhone 99"
            price:
              type: number
              example: 9999
            description:
              type: string
              example: "最新旗艦手機"
            category_id:
              type: integer
              example: 1
            image:
              type: string
              example: "http://example.com/img.jpg"
    responses:
      200:
        description: 加入購物車
        schema:
          properties:
            message:
              type: string
              example: "Added to cart , cart_id=..."
      403:
        description: 僅能查詢本人
        schema:
          properties:
            error:
              type: string
              example: "Permission denied"
      404:
        description: 用戶不存在
        schema:
          properties:
            error:
              type: string
              example: "User not found"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    cart_item = CartService.add_to_cart(user_id=user_id, product_id=product_id, quantity=quantity)
    
    return jsonify({"message": "Added to cart", "cart_id": cart_item.cart_id})



#從購物車移除商品
@carts_bp.route('/<int:user_id>/remove', methods=['DELETE'])
@jwt_required()
def remove_from_cart(user_id):
    """
    從購物車移除商品（需登入）
    ---
    tags:
      - carts
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: Product_id
          properties:
            prodcut_id:
              type: number
              example: 1
    responses:
      200:
        description: 成功從購物車移除商品
        schema:
          properties:
            message:
              type: string
              example: "Removed product from cart , cart_id=..."
      403:
        description: 僅能查詢本人
        schema:
          properties:
            error:
              type: string
              example: "Permission denied"
      400:
        description: 不存在該產品
        schema:
          properties:
            error:
              type: string
              example: "Missing product_id"
      404-1:
        description: 該用戶購物車不存在
        schema:
          properties:
            error:
              type: string
              example: "No active cart found"
      404-2:
        description: 購物車不存在該產品id
        schema:
          properties:
            error:
              type: string
              example: "Product not in cart"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    data = request.json
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    try:
        cart_item = CartService.remove_from_cart(user_id=user_id, product_id=product_id)
        return jsonify({"message": "Removed product from cart", "cart_id": cart_item.cart_id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    

# 調整購物車內商品數量
@carts_bp.route('/<int:user_id>/update', methods=['PUT'])
@jwt_required()
def update_cart_item(user_id):
    """
    從購物車調整商品數量（需登入）
    ---
    tags:
      - carts
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: Product_id_quantity
          properties:
            prodcut_id:
              type: number
              example: "iPhone 99"
            quantity:
              type: number
              example: 6
    responses:
      200:
        description: 成功從購物車更新商品數量
        schema:
          properties:
            message:
              type: string
              example: "Removed product from cart , cart_id=..."
      403:
        description: 僅能查詢本人
        schema:
          properties:
            error:
              type: string
              example: "Permission denied"
      400:
        description: 不存在該產品
        schema:
          properties:
            error:
              type: string
              example: "Missing product_id"
      404-1:
        description: 該用戶購物車不存在
        schema:
          properties:
            error:
              type: string
              example: "No active cart found"
      404-2:
        description: 購物車不存在該產品id
        schema:
          properties:
            error:
              type: string
              example: "Product not in cart"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    if not product_id or quantity is None:
        return jsonify({"error": "Missing product_id or quantity"}), 400
    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1"}), 400

    try:
        cart_item = CartService.update_cart_item(user_id=user_id, product_id=product_id, quantity=quantity)
        return jsonify({"message": "Updated product quantity in cart", "cart_id": cart_item.cart_id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# 結帳
@carts_bp.route('/<int:user_id>/checkout', methods=['POST'])
@jwt_required()
def checkout_cart(user_id):
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    data = request.json
    items_to_checkout = data.get("items")
    
    if not items_to_checkout or not isinstance(items_to_checkout, list):
        return jsonify({"error": "Must provide items to checkout"}), 400
    try:
        result = CartService.checkout_cart(user_id=user_id, items_to_checkout=items_to_checkout)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400