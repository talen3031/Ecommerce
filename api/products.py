
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.decorate import admin_required
from models import db, Product  
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

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if keyword:
        query = query.filter(Product.title.ilike(f"%{keyword}%"))

    products = query.all()
    result = [
        {
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "description": p.description,
            "image": p.image,
            "category_id": p.category_id
        }
        for p in products
    ]
    return jsonify(result)

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
    product = db.session.get(Product, product_id)
    if product:
        result = {
            "id": product.id,
            "title": product.title,
            "price": float(product.price),
            "description": product.description,
            "image": product.image,
            "category_id": product.category_id
        }
        return jsonify(result)
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
    if not title or price is None or not category_id:
        return jsonify({"error": "title, price, category_id are required"}), 400

    product = Product(
        title=title,
        price=price,
        description=description,
        category_id=category_id,
        image=image
    )
    db.session.add(product)
    db.session.commit()
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
    description = data.get('description', '')
    category_id = data.get('category_id')
    image = data.get('image', '')
    if not title or price is None or not category_id:
        return jsonify({"error": "title, price, category_id are required"}), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    product.title = title
    product.price = price
    product.description = description
    product.category_id = category_id
    product.image = image

    db.session.commit()
    return jsonify({"message": "Product updated", "product_id": product.id})

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
    product =  db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted", "product_id": product_id})
