import os
import requests
from flask import Blueprint, request, render_template
from models import db, User  

linemessage_bp = Blueprint('linemessage', __name__, url_prefix='/linemessage')

@linemessage_bp.route("/callback")
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
        'redirect_uri': 'https://ecommerce-backend-latest-6fr5.onrender.com/linemessage/callback',
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
