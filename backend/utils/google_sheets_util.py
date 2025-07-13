def append_order_to_sheet(order, order_items=None):
    from models import User, Product
    print("GOOGLE_SHEET_ID", GOOGLE_SHEET_ID)
    print("GOOGLE_SHEET_CRED", GOOGLE_SHEET_CRED)
    creds = Credentials.from_service_account_file(GOOGLE_SHEET_CRED, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

    # 取得 user info
    user_id = getattr(order, "user_id", None) or order.get("user_id")
    if hasattr(order, "user") and order.user:
        user_email = order.user.email
        user_fullname = order.user.full_name
    else:
        user = User.query.filter_by(id=user_id).first()
        user_email = user.email if user else f"UID:{user_id}"
        user_fullname = user.full_name if user else ""

    # 取得折扣碼與折扣金額
    discount_code = ""
    discount_amount = 0
    discount_info = ""
    if hasattr(order, "discount_code_id") and order.discount_code_id:
        from models import DiscountCode
        dc = DiscountCode.query.get(order.discount_code_id)
        if dc:
            discount_code = dc.code
            if dc.discount:
                percentage_off = int(dc.discount * 10)
                discount_info = f"{percentage_off}折"
            elif dc.amount:
                discount_info = f"折 {int(dc.amount)}"
            discount_amount = float(getattr(order, "discount_amount", 0)) or 0

    # 處理每個商品攤平成多欄
    item_columns = []
    items_to_process = order_items or getattr(order, "order_items", []) or order.get("items", [])
    for idx, item in enumerate(items_to_process, 1):
        if hasattr(item, "product") and item.product:
            title = item.product.title
            price = float(item.price) if hasattr(item, "price") else (item.product.price if hasattr(item.product, "price") else 0)
        else:
            product = Product.query.get(getattr(item, "product_id", None) or item.get("product_id"))
            title = product.title if product else f"PID:{item.get('product_id', '')}"
            price = float(item.get("price", 0)) if isinstance(item, dict) else 0
        qty = getattr(item, "quantity", None) or item.get("quantity")
        item_columns.extend([title, qty, price])

    row = [
        safe_val(getattr(order, "id", None) or order.get("id")),
        safe_val(user_id),
        safe_val(user_email),     
        safe_val(user_fullname),
        safe_val(str(getattr(order, "order_date", None) or order.get("order_date"))),
        safe_val(float(getattr(order, "total", 0) or order.get("total", 0))),
        safe_val(getattr(order, "status", None) or order.get("status")),
        safe_val(discount_code),
        safe_val(discount_info),
        safe_val(discount_amount),
    ] + [safe_val(col) for col in item_columns]

    sheet.append_row(row, value_input_option="USER_ENTERED")

def safe_val(val):
    if isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False)
    return val
