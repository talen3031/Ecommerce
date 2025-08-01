import os
import requests
from flask import Blueprint, request, render_template
from models import db, User  
from utils.line_bot import push_message,push_flex_message
from linebot.models import FlexSendMessage
from config import get_current_config
from utils.line_bot import push_message, push_flex_message
linemessage_bp = Blueprint('linemessage', __name__, url_prefix='/linemessage')

@linemessage_bp.route("/blinding")
def line_login_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return "Missing code", 400
    
    base_url = get_current_config().BACKEND_BASE_URL
    redirect_uri = f"{base_url.rstrip('/')}/linemessage/blinding"
    
    
    # 步驟一：用 code 換 access token
    token_url = "https://api.line.me/oauth2/v2.1/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': get_current_config().LINE_LOGIN_CHANNEL_ID,
        'client_secret': get_current_config().LINE_LOGIN_CHANNEL_SECRET,
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
    base_url = get_current_config().BACKEND_BASE_URL
    login_url = f"{base_url.rstrip('/')}/auth/login"

    data = {
        "email": get_current_config().LINEBOT_ADMIN_EMAIL , 
        "password":get_current_config().LINEBOT_ADMIN_PASSWORD
    }
    try:
        resp = requests.post(login_url, json=data, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        return result.get("access_token")
    except Exception as e:
        print(f"取得 JWT token 失敗: {e}")
        return None
    
from utils.line_bot import build_order_detail_flex,build_order_list_flex ,build_product_list_flex # 路徑依你實際目錄
@linemessage_bp.route("/webhook", methods=["POST"])
def line_webhook():
    try:
        body = request.json
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "message" and event["message"].get("type") == "text":
                line_user_id = event["source"]["userId"]
                msg = event["message"]["text"].strip()
                user = User.query.filter_by(line_user_id=line_user_id).first()
                if not user:
                    push_message(line_user_id, "請先到會員中心綁定 LINE 帳號")
                    continue
                 # 推薦商品（個人化，不管有無都給5個）
                if msg.startswith("推薦商品"):
                    from service.product_service import ProductService
                    recommend_limit = 5
                    products = ProductService.recommend_for_user(user.id, recommend_limit)
                    if not products or len(products) < recommend_limit:
                        # 不夠就用熱門/最新補滿
                        # 可以改成 get_top_products、get_products 等
                        products = ProductService.get_top_products(limit=recommend_limit)
                    flex_content = build_product_list_flex(products)
                    push_flex_message(line_user_id, flex_content, alt_text="推薦商品")

                # 歷史訂單列表
                elif msg in ("查詢歷史訂單","查詢訂單", "查詢我的訂單",  "我的訂單", "查訂單紀錄"):
                    from service.order_service import OrderService
                    
                    orders = OrderService.get_user_orders(user.id, page=1, per_page=5)
                    if not orders.items:
                        push_message(line_user_id, "目前沒有訂單紀錄")
                        continue
                    flex_content = build_order_list_flex(orders.items)
                    push_flex_message(line_user_id, flex_content, alt_text="訂單列表")
                # 單筆訂單明細
                elif msg.startswith("查訂單明細#"):
                    try:
                        order_id = int(msg.split("#")[1])
                        from service.order_service import OrderService
                        # 直接查 dict 版本
                        order_detail = OrderService.get_order_detail(order_id)
                        flex_content = build_order_detail_flex(order_detail)
                        push_flex_message(line_user_id, flex_content, alt_text="訂單明細")
                    except Exception:
                        push_message(line_user_id, "查詢訂單明細失敗，請稍後再試")
                else:
                    push_message(line_user_id, "你好")
        return "ok"
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Webhook Exception:", e)
        return str(e), 500
