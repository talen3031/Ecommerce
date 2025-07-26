
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.decorate import admin_required
from models import db, Product  
from service.product_service import ProductService
from service.audit_service import AuditService
from datetime import datetime
# 引入 cache 實體
from cache import cache


"""
definitions:
  Product:
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
      images:
        type: string
        example: ["https://img1.jpg", "https://img2.jpg"]
      category_id:
        type: integer
        example: 1
"""
products_bp = Blueprint('products', __name__, url_prefix='/products')

# 查詢所有商品
@products_bp.route('', methods=['GET'])
@cache.cached(timeout=300, query_string=True)   # <== 這行才是真正快取
def get_products():
    """
    查詢所有商品
    ---
    tags:
      - products
    parameters:
      - in: query
        name: category_id
        type: integer
        required: false
        description: 以分類過濾
      - in: query
        name: keyword
        type: string
        required: false
        description: 關鍵字模糊搜尋商品標題
    responses:
      200:
        description: 商品列表
        schema:
          type: array
          items:
            $ref: '#/definitions/Product'
    """
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', type=str)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    products_page = ProductService.search(
        category_id = category_id, 
        keyword=keyword, 
        min_price=min_price, 
        max_price=max_price,
        page=page,
        per_page=per_page
    )
    result = [product.to_dict() for product in products_page.items]

    return jsonify({
        "products": result,
        "total": products_page.total,
        "page": products_page.page,   #page 當前頁，pages 總頁數，total 總商品數，per_page 每頁幾筆
        "per_page": products_page.per_page,
        "pages": products_page.pages
    })

@products_bp.route('/admin', methods=['GET'])
@jwt_required()
@admin_required
def get_products_admin():
    """
    查詢所有商品（管理員，含上架/下架）
    ---
    tags:
      - products
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        required: false
      - in: query
        name: per_page
        type: integer
        required: false
    responses:
      200:
        description: 所有商品列表
        schema:
          type: object
          properties:
            products:
              type: array
              items:
                type: object
      403:
        description: 權限不足
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    products_page = ProductService.search_all_admin(page=page, per_page=per_page)
    products = [p.to_dict() for p in products_page.items]
    return jsonify({"products": products, "total": products_page.total, "page": page, "per_page": per_page})

# 查詢單一商品
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    查詢單一商品
    ---
    tags:
      - products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: 商品ID
    responses:
      200:
        description: 商品資訊
        schema:
          id: Product
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
            category_id:
              type: integer
              example: 1
      404:
        description: 商品不存在
    """
    product = Product.get_active_by_product_id(product_id)
    
    if product:
        return jsonify(product.to_dict())
    else:
        return jsonify({"error": "Product not found"}), 404

# 新增商品
@products_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    """
    新增商品（需管理員）
    ---
    tags:
      - products
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
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
            images:
              type: string
              example: ["https://img1.jpg", "https://img2.jpg"]
    responses:
      200:
        description: 建立成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product created"
            product_id:
              type: integer
              example: 3
      400:
        description: 輸入資料缺漏或錯誤
        schema:
          type: object
          properties:
            error:
              type: string
              example: "title, price, category_id are required"
      401:
        description: 權限不足
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unauthorized"
    """
   
    data = request.json
    title = data.get('title')
    price = data.get('price')
    description = data.get('description', '')
    category_id = data.get('category_id')
    images = data.get('images', [])
    
    product = ProductService.create_product(
          title=title,
          price=price,
          description=description,
          category_id=category_id,
          images=images
    )
    cache.clear()
    admin_id = get_jwt_identity()
    #寫入日志
    AuditService.log(
        user_id= admin_id,
        action='add',
        target_type='product',
        target_id=product.id,
        description=f"Added product: {product.to_dict()}"
    )
    return jsonify({"message": "Product created", "product_id": product.id})

# 修改商品（全部覆蓋）
@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """
    修改商品（需管理員）
    ---
    tags:
      - products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: 商品ID
      - in: body
        name: body
        required: true
        schema:
          id: ProductUpdate
          required:
            - title
            - price
            - category_id
          properties:
            title:
              type: string
              example: "iPhone 99 Pro"
            price:
              type: number
              example: 10999
            description:
              type: string
              example: "新一代旗艦"
            category_id:
              type: integer
              example: 2
            images:
              type: string
              example: ["https://img1.jpg", "https://img2.jpg"]
    responses:
      200:
        description: 修改成功
        schema:
          properties:
            message:
              type: string
              example: "Product updated"
            product_id:
              type: integer
              example: 2
      400:
        description: 輸入資料缺漏或錯誤
      404:
        description: 商品不存在
    """

    data = request.json
    title = data.get('title')
    price = data.get('price')
    description = data.get('description')
    category_id = data.get('category_id')
    images = data.get('images', None)
    # 取得修改前的資料（可選，方便比較差異）
    old_product = Product.get_by_product_id(product_id)
    old_data = old_product.to_dict() if old_product else {}

    # 修改商品
    product_update = ProductService.update_product(
        product_id=product_id,
        title=title, 
        price=price, 
        category_id=category_id,
        description=description, 
        images = images
    )
    cache.clear()
    # 取得操作者ID
    admin_id = get_jwt_identity()

    # 日誌內容
    description_log = (
        f"Before: {old_data}\nAfter: {product_update.to_dict()}"
    )

    # 寫入日誌
    AuditService.log(
        user_id = admin_id,
        action = 'update',
        target_type = 'product',
        target_id = product_update.id,
        description = description_log
    )
    return jsonify({"message": "Product updated", "product_id": product_update.id})

# 刪除商品
@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    """
    刪除商品（需管理員）
    ---
    tags:
      - products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: 商品ID
    responses:
      200:
        description: 刪除成功
        schema:
          properties:
            message:
              type: string
              example: "Product deleted"
            product_id:
              type: integer
              example: 2
      404:
        description: 商品不存在
    """

    product = ProductService.delete_product(product_id)
    cache.clear()
    admin_id = get_jwt_identity()

     #寫入日志
    AuditService.log(
        user_id= admin_id,
        action='delete',
        target_type='product',
        target_id=product.id,
        description=f"update product: {product.to_dict()}"
    )
        

    
    return jsonify({"message": "Product deleted", "product_id": product.id})

@products_bp.route('/sale/<int:product_id>', methods=['POST'])
@jwt_required()
@admin_required
def add_product_sale(product_id):
    """
    新增商品特價（需管理員）
    ---
    tags:
      - products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: 商品ID
      - in: body
        name: body
        required: true
        schema:
          required: [discount, start_date, end_date]
          properties:
            discount:
              type: number
              example: 0.8
            start_date:
              type: string
              example: "2024-07-01T00:00:00"
            end_date:
              type: string
              example: "2024-07-15T23:59:59"
            description:
              type: string
              example: "暑假八折特賣"
    responses:
      200:
        description: 建立成功
        schema:
          properties:
            message:
              type: string
              example: "Sale created"
            sale_id:
              type: integer
              example: 10
      400:
        description: 格式錯誤
        schema:
          properties:
            error:
              type: string
              example: "start_date or end_date format error"
    """
    data = request.json
    discount = data.get("discount")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")
    description = data.get("description")
   
    sale=ProductService.add_product_onsale(product_id=product_id,
                                           discount=discount,
                                           start_date=start_date_str,
                                           end_date=end_date_str,
                                           description=description)
    cache.clear()
    admin_id = get_jwt_identity() 
    # 寫入日誌
    AuditService.log(
        user_id = admin_id,
        action = 'add on sale',
        target_type = 'product',
        target_id = sale.product_id,
        description = f"update product: {sale.to_dict()}"
    )
   
    return jsonify({"message": "Sale created", "sale_id": sale.id})


@products_bp.route('/<int:product_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def deactivate_product(product_id):
    """
    下架商品（需管理員）
    ---
    tags:
      - products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: 商品ID
    responses:
      200:
        description: 商品下架成功
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product deactivated"
      404:
        description: 商品不存在
        schema:
          properties:
            error:
              type: string
              example: "product not found"
    """
    
    product = ProductService.set_product_active_status(product_id, False)
    cache.clear()

    AuditService.log(
        user_id=get_jwt_identity(),
        action='deactivate',
        target_type='product',
        target_id=product_id,
        description=f"Product {product_id} deactivated"
    )
    return jsonify({"message": f"Product{product.title}  deactivated"})

@products_bp.route('/<int:product_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_product(product_id):
    product = ProductService.set_product_active_status(product_id, True)
    cache.clear()
    AuditService.log(
        user_id=get_jwt_identity(),
        action='activate',
        target_type='product',
        target_id=product_id,
        description=f"Product {product_id} activated"
    )
    return jsonify({"message": f"Product{product.title} activated"})
