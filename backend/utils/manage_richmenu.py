from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, MessageAction
import os

def get_line_bot_api():
    """動態抓 LINE access token，支援 Flask context 或純 script 執行"""
    try:
        from flask import current_app
        token = current_app.config["LINE_CHANNEL_ACCESS_TOKEN"]
    except Exception:
        # 允許純 script 執行
        token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        if not token:
            try:
                from config import config
                token = config["default"].LINE_CHANNEL_ACCESS_TOKEN
            except Exception:
                raise Exception("找不到 LINE_CHANNEL_ACCESS_TOKEN，請設定環境變數或 config 檔")
    return LineBotApi(token)

line_bot_api = get_line_bot_api()

def delete_all_rich_menus():
    menus = line_bot_api.get_rich_menu_list()
    for menu in menus:
        print(f"刪除 RichMenu: {menu.rich_menu_id} ({menu.name})")
        line_bot_api.delete_rich_menu(menu.rich_menu_id)

def create_recommend_rich_menu(image_filename="richmenu_buttons.png"):
    # 建立推薦商品 Rich Menu
    rich_menu_to_create = RichMenu(
        size={"width": 2500, "height": 843},
        selected=True,
        name="MainMenu",
        chat_bar_text="Menu",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                action=MessageAction(label='Order', text='我的訂單')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=834, y=0, width=833, height=843),
                action=MessageAction(label='Recommend', text='推薦商品')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
                action=MessageAction(label='Support', text='聯絡客服')
            ),
        ]
    )

    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print("RichMenu created, id:", rich_menu_id)

    # 上傳圖片
    img_path = os.path.join(os.path.dirname(__file__), image_filename)
    with open(img_path, "rb") as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
    print("RichMenu image uploaded.")

    # 設為預設
    line_bot_api.set_default_rich_menu(rich_menu_id)
    print("RichMenu set as default.")

if __name__ == "__main__":
    delete_all_rich_menus()
    create_recommend_rich_menu("richmenu_buttons.png")
    print("Rich Menu 已自動重設完成。")
