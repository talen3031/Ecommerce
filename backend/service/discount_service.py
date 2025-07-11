from models import db, DiscountCode, UserDiscountCode
from datetime import datetime

class DiscountService:
    @staticmethod
    def create_discount_code(
        code, discount=None, amount=None, product_id=None, min_spend=None,
        valid_from=None, valid_to=None, usage_limit=None, per_user_limit=None,
        description=None
    ):
        # 檢查重複
        if DiscountCode.query.filter_by(code=code).first():
            raise ValueError("折扣碼已存在")
        # 至少要 discount 或 amount
        if (discount is None and amount is None) or (discount and amount):
            raise ValueError("discount 與 amount 必須二擇一")

        dc = DiscountCode(
            code=code,
            discount=discount,
            amount=amount,
            product_id=product_id,
            min_spend=min_spend,
            valid_from=valid_from,
            valid_to=valid_to,
            usage_limit=usage_limit,
            per_user_limit=per_user_limit,
            description=description,
            is_active=True
        )
        db.session.add(dc)
        db.session.commit()
        return dc

    # 更多：查詢、驗證、更新、停用，可照你需求加

    @staticmethod
    def get_discount_code_by_code(code):
        return DiscountCode.query.filter_by(code=code).first()
    @staticmethod
    def apply_discount_code(user_id, cart, code, items_to_checkout=None):
        """
        檢查折扣碼是否可用，計算折扣後金額
        :param user_id: 當前用戶ID
        :param cart: 當前購物車對象
        :param code: 用戶輸入的折扣碼
        :return: (success, message, discount_code物件, 折扣後金額, 折扣金額)
        """
        dc = DiscountCode.query.filter_by(code=code, is_active=True).first()
        if not dc:
            return False, "折扣碼不存在或已停用", None, None, None

        now = datetime.now()
        if dc.valid_from > now or dc.valid_to < now:
            return False, "折扣碼不在有效期限", None, None, None

        # 查詢該用戶使用次數
        user_dc = UserDiscountCode.query.filter_by(user_id=user_id, discount_code_id=dc.id).first()
        user_usage = user_dc.used_count if user_dc else 0
        
        
        # 計算總金額（判斷單一商品或結帳商品清單）
        if items_to_checkout is None:
            items = cart.cart_items
        else:
            # 只用本次結帳的 items!
            items = []
            for checkout_item in items_to_checkout:
                cart_item = next(
                    (ci for ci in cart.cart_items if ci.product_id == checkout_item["product_id"]),
                    None
                )
                if cart_item:
                    temp_item = type('obj', (), {})()
                    temp_item.product = cart_item.product
                    temp_item.quantity = checkout_item.get("quantity", cart_item.quantity)
                    temp_item.product_id = cart_item.product_id  
                    items.append(temp_item)
        if not items:
            return False, "沒有任何商品可計算折扣", None, None, None
        order_total = 0

        if dc.product_id:
        # 商品專屬折扣，只計算這次要結帳的該商品總價
            target_item = next((item for item in items if item.product_id == dc.product_id), None)
            if not target_item:
                return False, "此折扣碼僅適用特定商品", None, None, None
            order_total = float(target_item.product.price) * target_item.quantity
        else:
            # 只算本次結帳商品
            for item in items:
                order_total+=float(item.product.price) * item.quantity


        # 滿額限制
        if dc.min_spend and order_total < dc.min_spend:
            return False, f"未達最低消費金額 {dc.min_spend}", None, None, None

        # 使用次數限制
        if dc.usage_limit and dc.used_count >= dc.usage_limit:
            return False, "折扣碼已達總使用上限", None, None, None
        if dc.per_user_limit and user_usage >= dc.per_user_limit:
            return False, "您已達本折扣碼可用次數上限", None, None, None

        # 計算折扣
        #  金額折抵（如 amount=100）時，discount_amount = 折抵金額（如果消費 50 元，用 100 元折價券，只會折 50 元）
        if dc.amount:
            discount_amount = min(order_total, dc.amount)
            discounted_total = max(order_total - dc.amount, 0)
        #百分比折扣（如 discount=0.8 代表 8 折），discount_amount = 原價 × (1-折扣率)。
        elif dc.discount:
            discount_amount = round(order_total * (1 - dc.discount), 2)
            discounted_total = round(order_total * dc.discount, 2)
        else:
            discount_amount = 0             
            discounted_total = order_total

        return True, "折扣碼可用", dc, discounted_total, discount_amount
    @staticmethod
    def consume_discount_code(user_id, code):
        """結帳成功後，折扣碼用掉一次（全局＋該用戶）"""
        dc = DiscountCode.query.filter_by(code=code, is_active=True).first()
        if not dc:
            return
        dc.used_count = (dc.used_count or 0) + 1
        # 該用戶的紀錄
        user_dc = UserDiscountCode.query.filter_by(user_id=user_id, discount_code_id=dc.id).first()
        if not user_dc:
            user_dc = UserDiscountCode(user_id=user_id, discount_code_id=dc.id, used_count=1)
            db.session.add(user_dc)
        else:
            user_dc.used_count += 1
            user_dc.last_used_at = datetime.now()
        db.session.commit()
    @staticmethod
    def deactivate_discount_code(code):
        code.is_active = False
        #code.valid_to = min(code.valid_to, datetime.now())  # 可以強制失效（可選）
        db.session.commit()
        return code