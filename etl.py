import requests
import psycopg2
import random
from werkzeug.security import generate_password_hash, check_password_hash

PG_CONFIG = {
    "dbname": "Ecommerce",
    "user": "postgres",
    "password": "talen168168", 
    "host": "localhost",
    "port": "5432"
}

def get_pg_conn():
    return psycopg2.connect(**PG_CONFIG)

def etl_categories(cur):
    print("下載 categories...........................................................")
    resp = requests.get("https://fakestoreapi.com/products/categories")
    categories = resp.json()
    cat_name_id_map = {}
    for cat in categories:
        cur.execute("""
            INSERT INTO categories (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id;
        """, (cat,))
        result = cur.fetchone()
        if result:
            cat_id = result[0]
        else:
            cur.execute("SELECT id FROM categories WHERE name = %s;", (cat,))
            cat_id = cur.fetchone()[0]
        cat_name_id_map[cat] = cat_id
    return cat_name_id_map

def etl_products(cur, cat_name_id_map):
    print("下載 products...........................................................")
    resp = requests.get("https://fakestoreapi.com/products")
    products = resp.json()
    for prod in products:
        cat_id = cat_name_id_map[prod['category']]
        cur.execute("""
            INSERT INTO products (id, title, price, description, category_id, image)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """, (
                prod['id'],
                prod['title'],
                prod['price'],
                prod['description'],
                cat_id,
                prod['image']
            )
        )

def etl_users(cur):
    print("下載 users...........................................................")
    resp = requests.get("https://fakestoreapi.com/users")
    users = resp.json()
    for user in users:
        fullname = f"{user['name']['firstname']} {user['name']['lastname']}"

        address = f"{user['address']['number']} {user['address']['street']}, {user['address']['city']}"
        hashed_pw=generate_password_hash(user['password'])
        cur.execute("""
            INSERT INTO users (id, username, email, password, full_name, address, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            RETURNING id;
            """, (
                user['id'],
                user['username'],
                user['email'],
                hashed_pw,
                fullname,
                address,
                user['phone']
            )
        )
def etl_carts_orders(cur):
    print("下載 carts，隨機分配一半進 carts 另一半進 orders（自動計算 total）...........................................................")
    resp = requests.get("https://fakestoreapi.com/carts")
    carts_api = resp.json()
    cart_ids = [cart['id'] for cart in carts_api]
    order_ids = set(random.sample(cart_ids, k=len(cart_ids)//2))
    carts_for_cart = []
    carts_for_order = []
    for cart in carts_api:
        if cart['id'] in order_ids:
            carts_for_order.append(cart)
        else:
            carts_for_cart.append(cart)
    # 寫入 carts
    for cart in carts_for_cart:
        cur.execute("""
            INSERT INTO carts (id, user_id, created_at, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            cart['id'],
            cart['userId'],
            cart['date'],
            'active'
        ))
        # carts_items
        for item in cart['products']:
            cur.execute("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (cart_id, product_id) DO NOTHING
            """, (
                cart['id'],
                item['productId'],
                item['quantity']
            ))
    # 寫入 orders
    for cart in carts_for_order:
        order_id = cart['id']
        cur.execute("""
            INSERT INTO orders (id, user_id, order_date, total, status)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            order_id,
            cart['userId'],
            cart['date'],
            0,  # 先預設 0，等等計算
            'completed'
        ))
        total = 0
        for item in cart['products']:
            cur.execute("SELECT price FROM products WHERE id = %s;", (item['productId'],))
            row = cur.fetchone()
            price = row[0] if row else 0
            subtotal = price * item['quantity']
            total += subtotal
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (order_id, product_id) DO NOTHING
            """, (
                order_id,
                item['productId'],
                item['quantity'],
                price
            ))
        # 計算完total後再update orders
        cur.execute("""
            UPDATE orders SET total = %s WHERE id = %s
        """, (total, order_id))
    return carts_for_cart, carts_for_order
def sync_all_sequences(conn):
    """
    讓所有主鍵 id 欄位自動同步到最大值，避免主鍵衝突。
    請根據你的資料表名稱調整 table 和 sequence 名。
    """
    with conn.cursor() as cur:
        tables_and_cols = [
            ('categories', 'id'),
            ('products', 'id'),
            ('users', 'id'),
            ('orders', 'id'),
            ('order_items', 'id'),
            ('carts', 'id'),
            ('cart_items', 'id')
        ]
        for table, col in tables_and_cols:
            cur.execute("SELECT pg_get_serial_sequence(%s, %s)", (table, col))
            seq = cur.fetchone()[0]
            if seq:
                # 查最大 id
                cur.execute(f"SELECT MAX({col}) FROM {table}")
                max_id = cur.fetchone()[0] or 0
                # 設定 sequence
                cur.execute("SELECT setval(%s, %s)", (seq, max_id))
        conn.commit()
    print("所有主鍵序列已同步到最大值！")


def main():
    with get_pg_conn() as conn:
        with conn.cursor() as cur:
            # Categories
            cat_name_id_map = etl_categories(cur)
            conn.commit()
            # Products
            etl_products(cur, cat_name_id_map)
            conn.commit()
            # Users
            etl_users(cur)
            conn.commit()
            # Carts/Orders + items
            carts, orders = etl_carts_orders(cur)
            conn.commit()
    sync_all_sequences(conn)
    print("全部資料寫入完成！")

if __name__ == "__main__":
    main()
