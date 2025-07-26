from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Cart
from datetime import datetime
from service.cart_service import CartService
from service.product_service import ProductService 
from service.discount_service import DiscountService
carts_bp = Blueprint('carts', __name__, url_prefix='/carts')
#用戶查詢購物車
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


#用戶加入商品至購物車
@carts_bp.route('/<int:user_id>', methods=['POST'])
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
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            product_id:
              type: integer
              example: 1
            quantity:
              type: integer
              example: 1
          required:
            - product_id
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
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400
    cart_item = CartService.add_to_cart(user_id=user_id, product_id=product_id, quantity=quantity)
    
    
    return jsonify({"message": "Added to cart", "cart_id": cart_item.cart_id})



#從購物車移除商品
@carts_bp.route('/<int:user_id>', methods=['DELETE'])
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
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            product_id:
              type: integer
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

    cart_item = CartService.remove_from_cart(user_id=user_id, product_id=product_id)
     
    return jsonify({"message": "Removed product from cart", "cart_id": cart_item.cart_id}), 200

    

# 調整購物車內商品數量
@carts_bp.route('/<int:user_id>', methods=['PUT'])
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
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            product_id:
              type: integer
              example: 1
            quantity:
              type: integer
              example: 1
          required:
            - product_id
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
    product_id = int(data.get("product_id"))
    quantity = data.get("quantity")
    
    if not product_id or quantity is None:
        return jsonify({"error": "Missing product_id or quantity"}), 400
    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"error": "Invalid product_id"}), 400

    cart_item ,old_qty= CartService.update_cart_item(user_id=user_id, product_id=product_id, quantity=quantity)
    
    
    return jsonify({"message": f"Updated product quantity {old_qty} -> {quantity} in cart{cart_item.cart_id}"}), 200

# 結帳
@carts_bp.route('/<int:user_id>/checkout', methods=['POST'])
@jwt_required()
def checkout_cart(user_id):
    """
    結帳 (需登入)
    ---
    summary: 結帳（將購物車商品生成訂單）
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
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            items:
              type: array
              description: "要結帳的商品清單，若傳 'all' 則結帳購物車內所有商品"
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 1
                  quantity:
                    type: integer
                    example: 2
              example:
                - product_id: 1
                  quantity: 2
                - product_id: 3
                  quantity: 1
          required:
            - items
    responses:
      200:
        description: 結帳成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Partial checkout success"
            order_id:
              type: integer
              example: 1001
            total:
              type: number
              example: 3999.0
      400:
        description: 資料格式錯誤或缺少結帳商品
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Must provide items to checkout"
      403:
        description: 權限不足
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Permission denied"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    data = request.json or {}
    items_to_checkout = data.get("items")
    discount_code = data.get("discount_code")
    shipping_info = data.get("shipping_info")
    
    #shipping_info is necessary!
    if not shipping_info :
        return jsonify({"error": "shipping_info is empty"}), 400
    # 若傳入'all' or 'ALL'
    if isinstance(items_to_checkout, str) and items_to_checkout.lower() == "all":
        cart = CartService.get_cart(user_id=user_id)
        if not cart or not cart.get("items"):
            return jsonify({"error": "Cart is empty"}), 400

        items_to_checkout = [
            {"product_id": item["product_id"], "quantity": item["quantity"]}
            for item in cart["items"]
        ]
        if not items_to_checkout:
            return jsonify({"error": "Cart is empty"}), 400

    # 檢查 items_to_checkout 是否為 list 並且非空
    if not items_to_checkout or not isinstance(items_to_checkout, list):
        return jsonify({"error": "Please provide items to checkout or enter 'all'"}), 400
    if len(items_to_checkout) == 0:
        return jsonify({"error": "Cart is empty"}), 400

    # 執行結帳
    result = CartService.checkout_cart(user_id=user_id, items_to_checkout=items_to_checkout,discount_code=discount_code ,shipping_info=shipping_info)
    
    
    return jsonify(result), 200

@carts_bp.route('/<int:user_id>/recommend', methods=['GET'])
@jwt_required()
def recommend_for_cart(user_id):
    """
    個人化推薦（依購物車內容 推薦同類別的熱賣商品）
    ---
    tags:
      - carts
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: query
        name: limit
        type: integer
        required: false
        description: 推薦商品數量（預設5）
    responses:
      200:
        description: 推薦商品列表
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              title:
                type: string
                example: "iPhone 99"
              price:
                type: number
                example: 9999
              description:
                type: string
                example: "旗艦手機"
              category_id:
                type: integer
                example: 1
              image:
                type: string
                example: "http://img"
      403:
        description: 權限不足
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Permission denied"
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    limit = request.args.get('limit', 5, type=int)
    products = ProductService.recommend_for_cart(user_id, limit)
    return jsonify([p.to_dict() for p in products])

#協同過濾推薦購物車商品
@carts_bp.route('/<int:user_id>/recommend/collaborative', methods=['GET'])
@jwt_required()
def recommend_cart_collaborative(user_id):
    """
    協同過濾推薦購物車商品
    ---
    tags:
      - carts
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: 用戶ID
      - in: query
        name: limit
        type: integer
        required: false
        description: 推薦商品數量（預設5）
    responses:
      200:
        description: 推薦商品列表
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              title:
                type: string
                example: "iPhone 99"
              price:
                type: number
                example: 9999
              description:
                type: string
                example: "旗艦手機"
              category_id:
                type: integer
                example: 1
              image:
                type: string
                example: "http://img"
      403:
        description: 權限不足
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Permission denied"
    """

    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    limit = request.args.get('limit', 5, type=int)
    products = ProductService.recommend_for_cart_collaborative(user_id, limit)
    return jsonify([p.to_dict() for p in products])

@carts_bp.route('/<int:user_id>/apply_discount', methods=['POST'])
@jwt_required()
def apply_discount(user_id):
    """
    在購物車套用折扣碼
    ---
    tags:
      - carts
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            code:
              type: string
              example: SPRINGSALE
    responses:
      200:
        description: 套用結果
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            discounted_total:
              type: number
            discount_amount:
              type: number
      400:
        description: 參數錯誤
    """
    current_user = get_jwt_identity()
    if int(current_user) != user_id:
        return jsonify({"error": "Permission denied"}), 403

    code = request.json.get("code")
    if not code:
        return jsonify({"error": "請輸入折扣碼"}), 400

    cart = Cart.query.filter_by(user_id=user_id, status='active').order_by(Cart.created_at.desc()).first()
    if not cart or not cart.cart_items:
        return jsonify({"error": "購物車為空"}), 400

    ok, msg, dc, discounted_total, discount_amount, rule_msg ,used_coupon =  DiscountService.apply_discount_code(user_id=user_id, cart=cart, code=code)
    return jsonify({
        "success": ok,
        "message": msg,
        "discounted_total": discounted_total,
        "discount_amount": discount_amount,
        "rule_msg": rule_msg,
        "discount_code": dc.to_dict() if dc else None,
        "used_coupon": used_coupon,
    })


# 查詢訪客購物車
@carts_bp.route('/guest/<string:guest_id>', methods=['GET'])
def get_cart_guest(guest_id):
    cart = CartService.get_cart(guest_id=guest_id)
    if not cart:
        return jsonify({"cart": None, "items": []})
    return jsonify(cart)

# 加入商品至訪客購物車
@carts_bp.route('/guest/<string:guest_id>', methods=['POST'])
def add_to_cart_guest(guest_id):
    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400
    cart_item = CartService.add_to_cart(guest_id=guest_id, product_id=product_id, quantity=quantity)
    return jsonify({"message": "Added to cart", "cart_id": cart_item.cart_id})

# 移除商品
@carts_bp.route('/guest/<string:guest_id>', methods=['DELETE'])
def remove_from_cart_guest(guest_id):
    data = request.json
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400
    cart_item = CartService.remove_from_cart(guest_id=guest_id, product_id=product_id)
    return jsonify({"message": "Removed product from cart", "cart_id": cart_item.cart_id}), 200

# 訪客調整商品數量
@carts_bp.route('/guest/<string:guest_id>', methods=['PUT'])
def update_cart_item_guest(guest_id):
    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    if not product_id or quantity is None:
        return jsonify({"error": "Missing product_id or quantity"}), 400
    cart_item, old_qty = CartService.update_cart_item(guest_id=guest_id, product_id=product_id, quantity=quantity)
    return jsonify({"message": f"Updated product quantity {old_qty} -> {quantity} in cart {cart_item.cart_id}"}), 200

# 訪客結帳
@carts_bp.route('/guest/<string:guest_id>/checkout', methods=['POST'])
def checkout_cart_guest(guest_id):
    data = request.json or {}
    items_to_checkout = data.get("items")
    discount_code = data.get("discount_code")
    shipping_info = data.get("shipping_info")
    if not shipping_info:
        return jsonify({"error": "shipping_info is empty"}), 400
    if isinstance(items_to_checkout, str) and items_to_checkout.lower() == "all":
        cart = CartService.get_cart(guest_id=guest_id)
        if not cart or not cart.get("items"):
            return jsonify({"error": "Cart is empty"}), 400
        items_to_checkout = [
            {"product_id": item["product_id"], "quantity": item["quantity"]}
            for item in cart["items"]
        ]
        if not items_to_checkout:
            return jsonify({"error": "Cart is empty"}), 400
    if not items_to_checkout or not isinstance(items_to_checkout, list):
        return jsonify({"error": "Please provide items to checkout or enter 'all'"}), 400
    if len(items_to_checkout) == 0:
        return jsonify({"error": "Cart is empty"}), 400
    result = CartService.checkout_cart(guest_id=guest_id, items_to_checkout=items_to_checkout,
                                       discount_code=discount_code, shipping_info=shipping_info)
    return jsonify(result), 200

# 套用折扣碼
@carts_bp.route('/guest/<string:guest_id>/apply_discount', methods=['POST'])
def apply_discount_guest(guest_id):
    code = request.json.get("code")
    if not code:
        return jsonify({"error": "請輸入折扣碼"}), 400

    # 取得原始 ORM 物件
    cart = Cart.query.filter_by(guest_id=guest_id, status='active').order_by(Cart.created_at.desc()).first()
    if not cart or not cart.cart_items:
        return jsonify({"error": "購物車為空"}), 400

    ok, msg, dc, discounted_total, discount_amount, rule_msg, used_coupon = \
        DiscountService.apply_discount_code(guest_id=guest_id, cart=cart, code=code)
    
    return jsonify({
        "success": ok,
        "message": msg,
        "discounted_total": discounted_total,
        "discount_amount": discount_amount,
        "rule_msg": rule_msg,
        "discount_code": dc.to_dict() if dc else None,
        "used_coupon": used_coupon,
    })
