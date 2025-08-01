from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def create_button_image(filename):
    W, H = 2500, 843
    img = Image.new("RGB", (W, H), (25, 25, 25))  # 黑底 (#191919)
    draw = ImageDraw.Draw(img)

    # 按鈕參數
    n_btn = 3
    btn_width = W // n_btn
    btn_height = 620
    margin_y = (H - btn_height) // 2
    radius = 60

    # 黃色按鈕 #FFD900
    btn_color = (255, 217, 0)
    border_color = (255, 217, 0)
    txt_color = (20, 20, 20)
    btn_texts = ["我的訂單", "推薦商品", "詢問客服"]
    icon_files = ["order.png", "product.png", "support.png"]

    # 文字字型
    try:
        font_path = "C:/Windows/Fonts/msjhbd.ttc"
        font = ImageFont.truetype(font_path, 72)
    except:
        font = ImageFont.load_default()

    for i, (text, icon_file) in enumerate(zip(btn_texts, icon_files)):
        x0 = i * btn_width + 60
        y0 = margin_y
        x1 = (i + 1) * btn_width - 60
        y1 = margin_y + btn_height

        # 畫圓角黃底按鈕
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=btn_color, outline=border_color, width=8)

        # icon 貼圖
        icon_path = os.path.join(os.path.dirname(__file__), icon_file)
        if os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("RGBA")
            icon = icon.resize((120, 120))
            # 加 icon 陰影
            shadow = Image.new('RGBA', icon.size, (0,0,0,0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.ellipse([10, 100, 110, 120], fill=(0,0,0,80))
            img.paste(shadow, (int((x0 + x1) // 2 - 60), y0 + 80), shadow)
            img.paste(icon, (int((x0 + x1) // 2 - 60), y0 + 50), icon)

        # 畫文字（白色）
        bbox = font.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_x = (x0 + x1) // 2 - tw // 2
        text_y = y0 + 220
        draw.text((text_x, text_y), text, font=font, fill=txt_color)

    img.save(filename)
    print("已產生黑底黃按鈕 rich menu：", filename)

if __name__ == "__main__":
    create_button_image("richmenu_buttons.png")
