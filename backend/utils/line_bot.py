import os
from linebot import LineBotApi
from linebot.models import TextSendMessage,FlexSendMessage

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(user_id, message):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        return True
    except Exception as e:
        print("Line推播失敗:", e)
        return False

def push_flex_message(user_id, flex_content, alt_text="商品列表"):
    """新的 Flex Message 推播，flex_content 是 flex message 的 dict/json 結構"""
    try:
        message = FlexSendMessage(alt_text=alt_text, contents=flex_content)
        line_bot_api.push_message(user_id, message)
        return True
    except Exception as e:
        print("Line推播失敗(Flex):", e)
        return False