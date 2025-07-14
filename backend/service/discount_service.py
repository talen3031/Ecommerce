from models import db, DiscountCode, UserDiscountCode,Product
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
    @staticmethod
    def apply_discount_code(user_id, cart, code, items_to_checkout=None):
        """
        檢查折扣碼是否可用，計算折扣後金額，同時回傳優惠規則描述與本次結帳有無實際採用折扣碼
        :return: (success, message, discount_code物件, 折扣後金額, 折扣金額, 規則說明, used_coupon)
        """
        from models import Product  # 避免循環 import

        # 查詢折扣碼
        dc = DiscountCode.query.filter_by(code=code, is_active=True).first()
        if not dc:
            return False, "折扣碼不存在或已停用", None, None, None, "", False

        now = datetime.now()
        # 檢查有效期限
        if dc.valid_from > now or dc.valid_to < now:
            return False, "折扣碼不在有效期限", None, None, None, "", False

        # 查詢該用戶的折扣碼使用次數
        user_dc = UserDiscountCode.query.filter_by(user_id=user_id, discount_code_id=dc.id).first()
        user_usage = user_dc.used_count if user_dc else 0

        # 整理本次要結帳的購物車商品（可以只結帳部分商品）
        def build_items():
            result = []
            if not items_to_checkout:
                return list(cart.cart_items)
            for checkout_item in items_to_checkout:
                for ci in cart.cart_items:
                    if ci.product_id == checkout_item["product_id"]:
                        temp_item = type('obj', (), {})()
                        temp_item.product = ci.product
                        temp_item.quantity = checkout_item.get("quantity", ci.quantity)
                        temp_item.product_id = ci.product_id
                        result.append(temp_item)
                        break
            return result

        items = build_items()
        if not items:
            return False, "沒有任何商品可計算折扣", None, None, None, "", False

        specified_product = Product.get_by_product_id(dc.product_id) if dc.product_id else None
        rule_msg = ""
        used_coupon = False  # 新增：這次有沒有實際用到折扣碼

        # === 商品專屬折扣碼（僅適用於某個商品，不可疊加特價）
        if dc.product_id:
            # 找出是否購物車內有此商品
            target_item = next((item for item in items if item.product_id == dc.product_id), None)
            if not target_item:
                return False, f"此折扣碼僅適用{specified_product.title}", None, None, None, "", False

            original_price = float(target_item.product.price)
            sale_price = float(target_item.product.get_final_price())  # 如果商品有特價，這裡已是特價價格

            # 計算折扣碼後單價 (用original_price 去算!)
            if dc.discount:
                coupon_price = original_price * dc.discount
            elif dc.amount:
                coupon_price = max(original_price - dc.amount, 0)
            else: # 防呆
                coupon_price = original_price 

            # 比較特價與折扣碼，誰優惠就用誰
            lowest_unit_price = min(sale_price, coupon_price)

            # 判斷本次是否有用到折扣碼優惠
            if lowest_unit_price == sale_price and sale_price < coupon_price:
                # 用特價，沒用到折扣碼

                rule_msg = f"商品專屬折扣碼，特價與折扣碼不可疊加，商品{specified_product.title}特價比折扣碼更優惠，因此折扣碼未被消耗"
                used_coupon = False
            elif lowest_unit_price == coupon_price and coupon_price < sale_price:
                # 用折扣碼
                rule_msg = f"本次已套用折扣碼優惠（此為商品{specified_product.title}專屬折扣碼）"
                used_coupon = True
            else:
                rule_msg = f"此為商品{specified_product.title}專屬折扣碼，僅適用指定商品"
                used_coupon = False  # 防呆，其他情境不消耗
            
            discounted_total = 0
            discount_amount = 0
            # 重新加總所有商品金額
            for item in items:
                if item.product_id == dc.product_id:
                    # 該商品採最低價（特價或折扣碼）
                    discounted_total += round(lowest_unit_price * item.quantity, 2)
                    discount_amount += round((original_price - lowest_unit_price) * item.quantity, 2)
                else:
                    # 其他商品無折扣碼優惠，直接用 get_final_price
                    discounted_total += round(float(item.product.get_final_price()) * item.quantity, 2)
        # === 全站折扣碼 ====
        else:
            rule_msg = "此為全站折扣碼，對所有商品加總後再進行折扣"
            subtotal = sum(float(item.product.get_final_price()) * item.quantity for item in items)
            #這個折扣碼是「百分比折扣」模式（例如 0.8 表示 8 折）
            if dc.discount:
                discount_amount = round(subtotal * (1 - dc.discount), 2) #計算折扣金額。例如 8 折就會是 subtotal * (1 - 0.8) = subtotal * 0.2
                discounted_total = round(subtotal * dc.discount, 2)      #計算折扣後總金額。例如 1000 元 8 折就是 1000 * 0.8 = 800 元
            #這個折扣碼是「金額折抵」模式（例如折 100 元）
            elif dc.amount:
                discount_amount = min(subtotal, dc.amount)       #如果消費金額不到折抵金額，例如只買 80 元的商品用 100 元折扣碼，最多只能折 80 元
                discounted_total = max(subtotal - dc.amount, 0)  #折抵後的總金額 = 原本金額扣掉折抵金額，但最低不能低於 0 
            #這張折扣碼既不是百分比、也不是金額折抵，極少發生但防呆
            else:
                discounted_total = subtotal
                discount_amount = 0
            used_coupon = True  # 全站折扣碼必然用到

        # 檢查滿額、次數限制
        if dc.min_spend and discounted_total < dc.min_spend:
            return False, f"未達最低消費金額 {dc.min_spend}", None, None, None, rule_msg, used_coupon
        if dc.usage_limit and dc.used_count >= dc.usage_limit:
            return False, "折扣碼已達總使用上限", None, None, None, rule_msg, used_coupon
        if dc.per_user_limit and user_usage >= dc.per_user_limit:
            return False, "您已達本折扣碼可用次數上限", None, None, None, rule_msg, used_coupon

        # 正常可用回傳（最後一個值就是 used_coupon）
        return True, "折扣碼可用", dc, discounted_total, discount_amount, rule_msg, used_coupon




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