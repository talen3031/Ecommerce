from models import CartItem, Product,User  # 避免循環 import
from utils.send_email import send_email  # 你自己的寄信工具
import sys
from utils.line_bot import push_message
import threading

def async_send_order_notify(order, user, order_items):
    def _notify():
        from utils.notify_util import send_email_notify_order_created, send_line_notify_order_created
        send_email_notify_order_created(order)
        send_line_notify_order_created(user, order, order_items)
    t = threading.Thread(target=_notify)
    t.start()

def send_email_notify_order_created(order):
    user = order.user
    if user and user.email:
        subject = "您在Nerd.com的訂單已成立！"
        items_html = ""
        for item in order.order_items:
            items_html += f"{item.product.title} x {item.quantity}：{float(item.price):.2f}元<br>"

        # 折扣資訊（只顯示折扣金額）
        discount_lines = []
        if getattr(order, "discount_code_id", None):
            discount_amount = getattr(order, "discount_amount", 0)
            discount_lines.append(f"折扣金額：{discount_amount:.0f} 元<br>")

        # 組合 email 內容
        html_lines = [
            f"您好，<br>",
            f"感謝您的訂購，您的訂單已成功成立！<br>",
            f"訂單編號：<b>{order.id}</b><br>",
            f"訂單金額：{float(order.total):.2f} 元<br>",
            f"訂單日期：{order.order_date.strftime('%Y-%m-%d %H:%M') if order.order_date else ''}<br>",
        ]
        if discount_lines:
            html_lines.extend(discount_lines)
        html_lines.append(f"訂購商品：<br>{items_html}<hr>")
        html_lines.append(
            "感謝您的訂購！請匯款至 (700) 03112790016408 後，我們會盡快出貨～<br>若有任何問題，請隨時聯繫客服 0923956156。"
        )

        html_content = "".join(html_lines)

        try:
            from utils.send_email import send_email
            send_email(user.email, subject, html_content)
            print(f"下單 email 發送成功!: {user.email}", file=sys.stderr)
        except Exception as e:
            print(f"下單 email 發送失敗: {user.email}, error: {e}")

def send_email_notify_user_order_status(order):
    user = order.user
    if user and user.email:
        subject = f"您在Nerd.com的訂單狀態已更新為「{order.status}」"
        html_content = (
            f"您好，<br>"
            f"您的訂單（編號：{order.id}）狀態已更新為：<b>{order.status}</b>。<br>"
            f"訂單總金額：{float(order.total):.2f} 元<br>"
            f"訂單日期：{order.order_date.strftime('%Y-%m-%d %H:%M') if order.order_date else ''}<br>"
            f"<hr>"
            f"您可以登入會員中心查詢訂單詳情。"
        )
        try:
            from utils.send_email import send_email   # 避免循環 import
            send_email(user.email, subject, html_content)
        except Exception as e:
            print(f"訂單狀態 email 寄送失敗：{user.email}, error: {e}")

def send_email_notify_users_cart_product_on_sale(product_id, discount, start_date, end_date, description):
    """
    傳送email 通知給用戶 購物車的東西正在特價
    """
    cart_items = CartItem.query.filter_by(product_id=product_id).all()
    notified_user_ids = set()
    product = Product.get_by_product_id(product_id)
    start_date_str = start_date.strftime("%Y/%m/%d")
    end_date_str = end_date.strftime("%Y/%m/%d")
    for item in cart_items:
        cart = item.cart
        if cart.status == "active":
            user = cart.user
            if user and user.email and user.id not in notified_user_ids:
                subject = f"您在Nerd.com購物車內的「{product.title}」開始特價囉！"
                
                html_content = (
                    f"您好，您Nerd.com購物車中的商品 <b>{product.title}</b> 現正特價！<br>"
                    f"原價：<s>{float(product.price)}</s> 元<br>"
                    f"特價：<span style='color:red;font-size:20px;'>{float(product.price) * discount:.2f}</span> 元<br>"
                    f"優惠期間：{start_date_str} ~ {end_date_str}<br>"
                    f"特價說明：{description or ''}<br>"
                    
                )
                try:
                    send_email(user.email, subject, html_content)
                except Exception as e:
                    print(f"email 發送失敗: {user.email}, error: {e}", file=sys.stderr)
                notified_user_ids.add(user.id)

def send_line_notify_order_created(user, order, order_items):
    """
    傳送LINE通知給用戶（包含訂單資訊、商品明細）
    :param user: User 物件
    :param order: Order 物件
    :param order_items: List[OrderItem]（含 item.product 物件）
    """
    if not user or not user.line_user_id:
        return False

    # 商品明細組成
    items_lines = []
    for item in order_items:
        # 若有 join，可直接 item.product.title
        product_title = getattr(item.product, "title", f"商品ID:{item.product_id}")
        items_lines.append(f"{product_title} x{item.quantity}  {item.price:.0f}元")
    items_text = "\n".join(items_lines)
     # 折扣資訊
    discount_info = None
    if getattr(order, "discount_code_id", None):
        # 有 discount_code_id 時才顯示折扣資訊
        discount_amount = getattr(order, "discount_amount", 0)
        discount_info = (
            f"折扣金額：{discount_amount:.0f} 元"
        )

    msg_lines = [
        f"Hi {user.email}，您的訂單已成立！",
        f"訂單編號：{order.id}",
        "商品明細：",
        items_text,
    ]
    if discount_info:
        msg_lines.append(discount_info)
    msg_lines.append(f"總金額：{order.total:.0f} 元")
    msg_lines.append("感謝您的訂購！請匯款至 (700) 03112790016408 後 我們會盡快出貨～")

    msg = "\n".join(msg_lines)
    return push_message(user.line_user_id, msg)

def send_line_notify_user_order_status(user, order):
    """
    訂單狀態變更時推播 LINE 通知給用戶
    :param user: User 物件
    :param order: Order 物件（需有 status 欄位）
    """
    if not user or not user.line_user_id:
        return False

    status_map = {
        "pending": "等待付款",
        "paid": "已付款",
        "processing": "處理中",
        "shipped": "已出貨",
        "delivered": "已送達",
        "cancelled": "已取消",
        "returned": "已退貨",
        "refunded": "已退款"
    }
    status_txt = status_map.get(order.status, order.status)

    msg = (
        f"Hi {user.email}，您的訂單狀態有更新！\n"
        f"目前狀態：{status_txt}\n"
        "如有疑問請聯繫客服 0923956156 ，感謝您的支持。"
    )
    return push_message(user.line_user_id, msg)

def send_line_cart_promo_notify(user, promo_products , discount, start_date, end_date, description):
    """
    傳送購物車商品特價提醒給用戶
    :param user: User 物件
    :param promo_products: List[Product] 正在特價的商品
    """
    if not user or not user.line_user_id:
        return False
    if not promo_products:
        return False

    promo_lines = []
    for p in promo_products:
        promo_lines.append(f"・{p.title} 目前特價 {float(p.price) * discount:.0f} 元（原價 {p.price:.0f} 元）")
    promo_text = "\n".join(promo_lines)
    start_date_str = start_date.strftime("%Y/%m/%d")
    end_date_str = end_date.strftime("%Y/%m/%d")
    msg = (
        f"Hi {user.email}，好消息！\n"
        "您購物車裡有商品正在特價：\n"
        f"{promo_text}\n"
        f"優惠期間：{start_date_str} ~ {end_date_str}\n"
        "快到網站搶購吧！"
                    
    )
    return push_message(user.line_user_id, msg)

def send_line_notify_users_cart_product_on_sale(product_id, discount, start_date, end_date, description):
    # 查所有有這個商品在購物車、且還沒結帳的會員
    cart_items = CartItem.query.filter_by(product_id=product_id).all()
    user_ids = set()
    for item in cart_items:
        if item.cart and item.cart.status == "active":
            user_ids.add(item.cart.user_id)

    promo_product = Product.query.get(product_id)
    for uid in user_ids:
        user = User.get_by_user_id(uid)
        send_line_cart_promo_notify(user, [promo_product] , discount, start_date, end_date, description)