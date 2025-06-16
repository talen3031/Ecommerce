from models import db, Product

class ProductService:
    @staticmethod
    def search(category_id=None, keyword=None, min_price=None, max_price=None):
        query = Product.query
        if category_id is not None:
            query = query.filter_by(category_id=category_id)
        if keyword:
            query = query.filter(Product.title.ilike(f"%{keyword}%"))
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        return query.all()
    
    @staticmethod
    def create_product(title, price, category_id, description=None, image=None):
            
        if not title or price is None or not category_id:
            raise ValueError('title, price, category_id are required')

        product = Product(
            title=title,
            price=price,
            description=description,
            category_id=category_id,
            image=image
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update_product(product_id, title, price, category_id, description, image):
        product = Product.get_by_product_id(product_id)
        if not product:
            raise ValueError("product not found")
        if title:
            product.title = title
        if price:
            product.price = price
        if description:
            product.description = description
        if category_id:
            product.category_id = category_id
        if image:
            product.image = image
        db.session.commit()
        return product

    @staticmethod
    def delete_product(product_id):
        product = Product.get_by_product_id(product_id)
        if not product:
            raise ValueError("product not found")
        db.session.delete(product)
        db.session.commit()
        return product
