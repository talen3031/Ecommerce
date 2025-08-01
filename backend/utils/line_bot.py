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
def build_product_list_flex(products):
    """給定商品清單（list of ORM/dict），組成 Flex carousel"""
    bubbles = []
    for prod in products:
        img = None
        imgs = prod.images if hasattr(prod, "images") else prod.get("images", [])
        if isinstance(imgs, list) and imgs:
            img = imgs[0]
        title = prod.title if hasattr(prod,"title") else prod.get("title", "")
        price = float(prod.price if hasattr(prod,'price') else prod.get('price', 0))
        desc = prod.description if hasattr(prod,"description") else prod.get("description", "")
        desc = str(desc) if desc is not None else ""
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": img or "https://img.icons8.com/?size=100&id=QtvvP6am9oP5&format=png",
                "size": "full",
                "aspectRatio": "1.51:1",
                "aspectMode": "cover",
                "action": { "type": "uri", "uri": img or "https://img.icons8.com/?size=100&id=QtvvP6am9oP5&format=png" }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": title, "weight": "bold", "size": "md"},
                    {"type": "text", "text": f"價格：{price:.0f}元", "size": "sm", "color": "#DA3743", "margin": "sm"},
                    {"type": "text", "text": desc, "wrap": True, "size": "sm", "color": "#555555", "margin": "md"}
                ]
            }
        }
        bubbles.append(bubble)
    # 保證不超過 12
    return {
        "type": "carousel",
        "contents": bubbles[:12]
    }

def build_order_detail_flex(order):
    """
    輸入 order dict（get_order_detail 回傳格式），產生 Flex message
    """
    # 商品明細
    item_boxes = []
    for item in order["items"]:
        product_title = item["title"]
        product_img = None
        imgs = item.get("images", [])
        if isinstance(imgs, list) and imgs:
            product_img = imgs[0]
        image_obj = {"type": "image", "url": product_img, "size": "sm", "aspectRatio": "1:1", "aspectMode": "cover"}
        if product_img:
            image_obj["action"] = { "type": "uri", "uri": product_img }
        else:
            image_obj = { "type": "text", "text": "無圖", "size": "sm", "color": "#cccccc" }
        item_box = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                image_obj,
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": product_title, "size": "sm", "weight": "bold", "color": "#222222"},
                        {"type": "text", "text": f"x{item['quantity']}  {float(item['price']):.0f}元", "size": "sm", "color": "#888888"}
                    ],
                    "margin": "md"
                }
            ],
            "spacing": "md",
            "margin": "md"
        }
        item_boxes.append(item_box)

    # Hero 圖片
    hero_url = None
    if order["items"]:
        imgs = order["items"][0].get("images", [])
        if isinstance(imgs, list) and imgs:
            hero_url = imgs[0]
    if not hero_url:
        hero_url = "https://img.icons8.com/?size=100&id=QtvvP6am9oP5&format=png"
    hero_obj = {
        "type": "image",
        "url": hero_url,
        "size": "full",
        "aspectRatio": "20:13",
        "aspectMode": "cover",
        "action": { "type": "uri", "uri": hero_url }
    }

    # 折扣碼資訊
    discount_info_box = None
    if order.get("discount_code_id"):
        from models import DiscountCode
        dc = DiscountCode.query.get(order["discount_code_id"])
        if dc:
            discount_info_box = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {"type": "text", "text": f"折扣碼：{dc.code}", "size": "sm", "color": "#209e61"},
                    {"type": "text", "text": f"-{float(order['discount_amount']):.0f}元", "size": "sm", "color": "#209e61", "align": "end"}
                ],
                "margin": "md"
            }

    # shipping info（這裡一定有 shipping_info，直接取值）
    shipping = order["shipping_info"]
    shipping_info_box = {
        "type": "box",
        "layout": "vertical",
        "margin": "md",
        "contents": [
            { "type": "text", "text": "取貨資訊", "size": "sm", "weight": "bold", "color": "#3468c4" },
            { "type": "text", "text": f"方式：{shipping.get('shipping_method','')}", "size": "sm", "color": "#555555" },
            { "type": "text", "text": f"收件人：{shipping.get('recipient_name','')}", "size": "sm", "color": "#555555" },
            { "type": "text", "text": f"電話：{shipping.get('recipient_phone','')}", "size": "sm", "color": "#555555" },
            { "type": "text", "text": f"門市：{shipping.get('store_name','')}", "size": "sm", "color": "#555555" }
        ]
    }

    # 組合 body 內容
    body_contents = [
        { "type": "text", "text": f"訂單編號：{order['order_id']}", "weight": "bold", "size": "md" },
        { "type": "text", "text": f"訂單日期：{order['order_date']}", "size": "sm", "color": "#999999", "margin": "sm" },
        { "type": "text", "text": f"狀態：{order['status']}", "size": "sm", "color": "#555555", "margin": "sm" },
        { "type": "separator", "margin": "md" },
        { "type": "box", "layout": "vertical", "contents": item_boxes, "margin": "md" }
    ]
    if discount_info_box:
        body_contents.append(discount_info_box)
    body_contents.append(shipping_info_box)
    body_contents.append({ "type": "text", "text": f"總金額：{float(order['total']):.0f}元", "size": "lg", "color": "#DA3743", "weight": "bold", "margin": "md" })

    flex_content = {
        "type": "bubble",
        "hero": hero_obj,
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": body_contents
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                { "type": "text", "text": "感謝您的訂購！", "align": "center", "color": "#555555", "size": "sm" }
            ]
        }
    }
    return flex_content


def build_order_list_flex(orders):
    """
    輸入 order list，回傳 carousel，每筆 order 一張 bubble
    """
    bubbles = []
    for order in orders:
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    { "type": "text", "text": f"訂單編號：{order.id}", "weight": "bold", "size": "md" },
                    { "type": "text", "text": f"日期：{order.order_date.strftime('%Y-%m-%d %H:%M') if order.order_date else ''}", "size": "sm", "color": "#999999", "margin": "sm" },
                    { "type": "text", "text": f"金額：{float(order.total):.0f}元", "size": "md", "color": "#DA3743", "weight": "bold", "margin": "sm" },
                    { "type": "text", "text": f"狀態：{order.status}", "size": "sm", "color": "#555555", "margin": "sm" },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#4653DF",
                        "action": {
                            "type": "message",
                            "label": "查詢明細",
                            "text": f"查訂單明細#{order.id}"  # 點擊時送出這個訊息
                        }
                    }
                ]
            }
        }
        bubbles.append(bubble)
    return {
        "type": "carousel",
        "contents": bubbles
    }
# 允許命令列執行
if __name__ == "__main__":
    create_default_rich_menu()