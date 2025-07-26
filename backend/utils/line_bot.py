from flask import current_app
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage

def get_line_bot_api():
    """動態抓 LINE access token，支援 Flask context 或純 script 執行"""
    try:
        token = current_app.config["LINE_CHANNEL_ACCESS_TOKEN"]
    except RuntimeError:
        from config import config
        token = config["default"].LINE_CHANNEL_ACCESS_TOKEN
    return LineBotApi(token)

def push_message(user_id, message):
    line_bot_api = get_line_bot_api()
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        return True
    except Exception as e:
        print("Line推播失敗:", e)
        return False

def push_flex_message(user_id, flex_content, alt_text="商品列表"):
    line_bot_api = get_line_bot_api()
    try:
        message = FlexSendMessage(alt_text=alt_text, contents=flex_content)
        line_bot_api.push_message(user_id, message)
        return True
    except Exception as e:
        print("Line推播失敗(Flex):", e)
        return False
