-- 建立 categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 建立 products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,  
    title VARCHAR(255) NOT NULL,
    price NUMERIC NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    image VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT unique_product_title_category UNIQUE (title, category_id)
);

-- 建立 users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name VARCHAR(255),
    address TEXT,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    role VARCHAR(20) DEFAULT 'user',
    CONSTRAINT unique_user_account UNIQUE (username, email)
);

-- 建立 orders（對應 carts）
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_date TIMESTAMP,
    total NUMERIC,
    status VARCHAR(50) DEFAULT 'pending'
);


-- 建立 order_items（對應 cart_items）
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    price NUMERIC NOT NULL,
    CONSTRAINT unique_order_product UNIQUE (order_id, product_id)
);

-- （進階）每個 user 只能有一個 active cart (optional)
-- CREATE UNIQUE INDEX unique_user_active_cart ON orders (user_id) WHERE status = 'active';

-- 購物車主表
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);


-- 購物車細項
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT unique_cart_product UNIQUE (cart_id, product_id)
);
-- AuditLog
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,         -- 操作類型: 'add', 'delete', 'update'
    target_type VARCHAR(50) NOT NULL,    -- 目標類型: 'product', 'user', ...
    target_id INTEGER,                   -- 目標ID，例如 product_id
    description TEXT,                    -- 操作說明
    created_at TIMESTAMP DEFAULT NOW(),  -- 操作時間
    CONSTRAINT fk_auditlog_user FOREIGN KEY(user_id) REFERENCES users(id)
);
