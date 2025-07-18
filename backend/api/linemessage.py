import os
import requests
from flask import Blueprint, request, render_template
from models import db, User  
from utils.line_bot import push_message,push_flex_message
from linebot.models import FlexSendMessage



linemessage_bp = Blueprint('linemessage', __name__, url_prefix='/linemessage')

@linemessage_bp.route("/blinding")
def line_login_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return "Missing code", 400

    # 步驟一：用 code 換 access token
    token_url = "https://api.line.me/oauth2/v2.1/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': 'https://ecommerce-backend-latest-6fr5.onrender.com/linemessage/blinding',
        #'redirect_uri': os.getenv('LINE_LOGIN_CALLBACK_URL'),
        'client_id': os.getenv('LINE_LOGIN_CHANNEL_ID'),
        'client_secret': os.getenv('LINE_LOGIN_CHANNEL_SECRET'),
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_res = requests.post(token_url, data=payload, headers=headers)
    token_data = token_res.json()
    if 'access_token' not in token_data:
        return f"Token error: {token_data}", 400

    access_token = token_data['access_token']

    # 步驟二：用 access token 拿用戶 profile（含 userId、displayName、pictureUrl）
    profile_url = "https://api.line.me/v2/profile"
    profile_headers = {"Authorization": f"Bearer {access_token}"}
    profile_res = requests.get(profile_url, headers=profile_headers)
    profile_data = profile_res.json()

    line_user_id = profile_data.get('userId')
    display_name = profile_data.get('displayName')
    picture_url = profile_data.get('pictureUrl')  # 加頭像

    if not line_user_id:
        return f"Profile error: {profile_data}", 400

    # 用 state 對應會員 user_id（在前端 state=會員user_id）
    user = None
    try:
        user = User.get_by_user_id(int(state))
    except Exception:
        pass

    if user:
        user.line_user_id = line_user_id
        user.line_display_name = display_name   # 如有欄位
        user.line_picture_url = picture_url     # 如有欄位
        db.session.commit()
        return render_template("line_bind_success.html", user=user, display_name=display_name)
    else:
        return f"綁定失敗，請重新登入網站。<br>您的 LINE userId：{line_user_id}"

def get_jwt_token_for_linebot():
    login_url = "https://ecommerce-backend-latest-6fr5.onrender.com/auth/login"
    data = {
        "email": os.getenv("LINEBOT_ADMIN_EMAIL"), 
        "password":os.getenv("LINEBOT_ADMIN_PASSWORD")
    }
    try:
        resp = requests.post(login_url, json=data, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        return result.get("access_token")
    except Exception as e:
        print(f"取得 JWT token 失敗: {e}")
        return None

@linemessage_bp.route("/webhook", methods=["POST"])
def line_webhook():
    try:
        body = request.json
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message" and event["message"].get("type") == "text":
                line_user_id = event["source"]["userId"]
                user_message = event["message"]["text"]

                user = User.query.filter_by(line_user_id=line_user_id).first()
                if not user:
                    push_message(line_user_id, "請先登入網站並綁定 LINE 帳號")
                    continue

                user_id = user.id

                # ==== JWT Token 設定 ====
                jwt_token = get_jwt_token_for_linebot()

                data = {
                    "query": user_message,
                    "user_id": user_id,
                    "jwt_token": jwt_token
                }

                try:
                    resp = requests.post(
                        "https://ecommerce-backend-latest-6fr5.onrender.com/langchain/query",
                        json=data,
                        timeout=10
                    )
                    if resp.status_code == 200:
                        api_data = resp.json()
                        result = api_data.get("api_response")
                        # 格式化結果
                        import json
                        msg = ""
                        if isinstance(result, dict):
                            # 商品查詢
                            if "products" in result:
                                flex_content = make_products_flex(result["products"])
                                push_flex_message(line_user_id, flex_content)
                                # 回文字版
                                #msg = format_products_for_line(result)
                                #push_message(line_user_id, msg)
                             # 判斷為訂單查詢
                            elif "orders" in result:
                                msg = format_orders_for_line(result["orders"])
                            # 判斷為訂單明細（有 order_id 或 total 或 discount_amount）
                            elif "items" in result and ("order_id" in result or "total" in result or "discount_amount" in result):
                                msg = format_order_detail_for_line(result)
                            # 判斷為購物車（有 items、有 status、沒有 order_id/total/discount_amount）
                            elif "items" in result and "status" in result:
                                msg = format_cart_for_line(result)
                            else:
                                msg = json.dumps(result, ensure_ascii=False, indent=2)
                        elif isinstance(result, list):
                            msg = json.dumps(result, ensure_ascii=False, indent=2)
                        else:
                            msg = str(result)
                    else:
                        try:
                            msg = resp.content.decode('utf-8', errors='replace')
                        except Exception:
                            msg = resp.text

                    if len(msg) > 4500:
                        msg = msg[:4500] + "\n...(訊息過長僅顯示部分)"
                except Exception as e:
                    msg = f"系統異常：{e}"

                push_message(line_user_id, msg)
        return "ok"
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Webhook Exception:", e)
        return str(e), 500

    
def format_orders_for_line(orders):
    if not orders:
        return "目前沒有歷史訂單"
    lines = []
    for order in orders[:5]:  # 只顯示最近5筆
        dt = order.get("order_date", "")[:19].replace("T", " ")
        lines.append(
            f"訂單編號: {order['id']}\n"
            f"日期: {dt}\n"
            f"金額: ${order['total']}\n"
            f"狀態: {order['status']}\n"
            f"優惠: {order['discount_amount'] or '-'}"
        )
        lines.append("------------")
    msg = "\n".join(lines)
    return msg + f"\n...共{len(orders)}筆訂單"

def format_order_detail_for_line(order):
    lines = []
    dt = order.get("order_date", "")[:19].replace("T", " ")
    lines.append(f"訂單編號: {order.get('order_id', order.get('id'))}")
    lines.append(f"日期: {dt}")
    lines.append(f"狀態: {order.get('status', '-')}")
    lines.append(f"總金額: ${order.get('total', '-')}")
    lines.append(f"優惠折抵: {order.get('discount_amount') or '-'}")
    lines.append("====== 商品明細 ======")
    for item in order.get("items", []):
        lines.append(
            f"．{item['title']}\n  數量: {item['quantity']}  單價: ${item['price']}"
        )
    return "\n".join(lines)

def format_cart_for_line(cart):
    if not cart or not cart.get("items"):
        return "目前購物車為空"

    dt = cart.get("created_at", "")[:19].replace("T", " ")
    lines = [
        f"購物車編號: {cart.get('id', '-')}",
        f"建立時間: {dt}",
        f"狀態: {cart.get('status', '-')}",
        "====== 商品列表 ======"
    ]
    for item in cart.get("items", []):
        lines.append(
            f"．{item['title']}\n"
            f"  數量: {item['quantity']}  原價: ${item['orginal_price']}  現價: ${item['price']}"
        )
    return "\n".join(lines)
def format_products_for_line(response: dict) -> str:
    """商品查詢結果純文字格式化（for LINE 訊息）"""
    products = response.get("products", [])
    if not products:
        return "查無商品"
    lines = []
    for p in products:
        title = p.get("title", "-")
        price = p.get("price", "-")
        sale_price = p.get("sale_price")
        is_on_sale = p.get("on_sale")
        desc = p.get("description", "")
        line = f"【{title}】\n{desc}\n"
        if is_on_sale and sale_price:
            line += f"特價: ${sale_price}（原價: ${price}）"
        else:
            line += f"售價: ${price}"
        # 顯示第一張圖片網址
        images = p.get("images", [])
        if images:
            line += f"\n圖片: {images[0]}"
        lines.append(line)
        lines.append("------------")
    msg = "\n".join(lines)
    msg += f"\n共 {response.get('total', 0)} 件商品"
    return msg

def make_products_flex(products: list) -> dict:
    """商品列表產生 LINE Flex Message（carousel）格式"""
    bubbles = []
    # 最多顯示5個
    for p in products[:5]:  
        title = p.get("title", "-")
        price = p.get("price", "-")
        sale_price = p.get("sale_price")
        is_on_sale = p.get("on_sale")
        desc = p.get("description", "")
        image_url = p.get("images", [""])[0] if p.get("images") else ""

        # 標價
        if is_on_sale and sale_price:
            price_text = f"特價: ${sale_price}（原價: ${price}）"
            price_color = "#FF5551"
        else:
            price_text = f"售價: ${price}"
            price_color = "#1DB446"

        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": image_url,
                "size": "full",
                "aspectRatio": "1.51:1",
                "aspectMode": "fit",
                "action": {"type": "uri", "uri": image_url} if image_url else None
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": title, "weight": "bold", "size": "md", "wrap": True},
                    {"type": "text", "text": desc, "size": "sm", "wrap": True, "color": "#666666"},
                    {"type": "text", "text": price_text, "size": "lg", "color": price_color, "wrap": True},
                ]
            }
        }
        # 移除空 action（避免部分 sdk 報錯）
        if not image_url:
            bubble["hero"].pop("action", None)
        bubbles.append(bubble)
    flex_content = {
        "type": "carousel",
        "contents": bubbles
    }
    return flex_content
