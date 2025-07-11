import os
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def push_message(user_id, message):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        return True
    except Exception as e:
        print("Line推播失敗:", e)
        return False
