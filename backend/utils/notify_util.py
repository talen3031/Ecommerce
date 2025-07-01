from models import CartItem, Product  # 避免循環 import
from utils.send_email import send_email  # 你自己的寄信工具

def notify_users_cart_product_on_sale(product_id, discount, start_date, end_date, description):

    cart_items = CartItem.query.filter_by(product_id=product_id).all()
    notified_user_ids = set()
    product = Product.get_by_product_id(product_id)
    for item in cart_items:
        cart = item.cart
        if cart.status == "active":
            user = cart.user
            if user and user.email and user.id not in notified_user_ids:
                subject = f"您Ecommerce購物車內的「{product.title}」開始特價囉！"
                html_content = (
                    f"您好，您Ecommerce購物車中的商品 <b>{product.title}</b> 現正特價！<br>"
                    f"原價：<s>{float(product.price)}</s> 元<br>"
                    f"特價：<span style='color:red;font-size:20px;'>{float(product.price) * discount:.2f}</span> 元<br>"
                    f"優惠期間：{start_date} ~ {end_date}<br>"
                    f"特價說明：{description or ''}<br>"
                )
                try:
                    send_email(user.email, subject, html_content)
                except Exception as e:
                    print(f"email 發送失敗: {user.email}, error: {e}")
                notified_user_ids.add(user.id)

def notify_user_order_created(order):
    user = order.user
    if user and user.email:
        subject = "您在Ecommerce的訂單已成立！"
        items_html = ""
        for item in order.order_items:
            items_html += f"{item.product.title} x {item.quantity}：{float(item.price):.2f}元<br>"
        html_content = (
            f"您好，<br>"
            f"感謝您的訂購，您的訂單已成功成立！<br>"
            f"訂單編號：<b>{order.id}</b><br>"
            f"訂單金額：{float(order.total):.2f} 元<br>"
            f"訂單日期：{order.order_date.strftime('%Y-%m-%d %H:%M') if order.order_date else ''}<br>"
            f"...<br>訂購商品：<br>{items_html}<hr>..."
            f"<hr>"
            f"若有任何問題，請隨時聯繫客服。"
        )
        try:
            from utils.send_email import send_email
            send_email(user.email, subject, html_content)
            print(f"下單 email 發送成功!: {user.email}")
        except Exception as e:
            print(f"下單 email 發送失敗: {user.email}, error: {e}")

def notify_user_order_status(order):
    user = order.user
    if user and user.email:
        subject = f"您在Ecommerce的訂單狀態已更新為「{order.status}」"
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