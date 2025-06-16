
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.decorate import admin_required
from models import db, Product  
from service.product_service import ProductService
from service.audit_service import AuditService

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
      image:
        type: string
        example: "http://img"
      category_id:
        type: integer
        example: 1
"""
products_bp = Blueprint('products', __name__, url_prefix='/products')

# 查詢所有商品
@products_bp.route('', methods=['GET'])
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
    
    products = ProductService.search(
        category_id = category_id, 
        keyword = keyword, 
        min_price = min_price, 
        max_price = max_price
    )

    result =[ product.to_dict() for product in products ] 
    

    return jsonify(result)
def get_products():
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
        "page": products_page.page,
        "per_page": products_page.per_page,
        "pages": products_page.pages
    })
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
    product = Product.get_by_product_id(product_id)
    
    if product:
        return jsonify(product.to_dict())
    else:
        return jsonify({"error": "Product not found"}), 404

# 新增商品
@products_bp.route('/add', methods=['POST'])
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
          id: ProductCreate
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
        description: 建立成功
        schema:
          properties:
            message:
              type: string
              example: "Product created"
            product_id:
              type: integer
              example: 3
      400:
        description: 輸入資料缺漏或錯誤
    """
   
    data = request.json
    title = data.get('title')
    price = data.get('price')
    description = data.get('description', '')
    category_id = data.get('category_id')
    image = data.get('image', '')
    
    product = ProductService.create_product(
          title=title,
          price=price,
          description=description,
          category_id=category_id,
          image=image
    )
    
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
@products_bp.route('/update/<int:product_id>', methods=['PUT'])
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
            image:
              type: string
              example: "http://example.com/pro.jpg"
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
    image = data.get('image')
  
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
        image=image
    )

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
@products_bp.route('/delete/<int:product_id>', methods=['DELETE'])
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
