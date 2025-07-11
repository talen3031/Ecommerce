CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price NUMERIC NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    images JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT unique_product_title_category UNIQUE (title, category_id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name VARCHAR(255),
    address TEXT,
    phone VARCHAR(50),
    created_at TIMESTAMP,
    role VARCHAR(20) DEFAULT 'user'
);

CREATE TYPE order_status_enum AS ENUM (
    'pending', 'paid', 'processing', 'shipped',
    'delivered', 'cancelled', 'returned', 'refunded'
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_date TIMESTAMP,
    total NUMERIC,
    status order_status_enum NOT NULL DEFAULT 'pending',
    discount_code_id INTEGER REFERENCES discount_codes(id)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    price NUMERIC NOT NULL,
    CONSTRAINT unique_order_product UNIQUE (order_id, product_id)
);

CREATE TYPE cart_status_enum AS ENUM ('active', 'checked_out');

CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    status cart_status_enum NOT NULL DEFAULT 'active'
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT unique_cart_product UNIQUE (cart_id, product_id)
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    token VARCHAR(128) UNIQUE NOT NULL,
    expire_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE products_on_sale (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) NOT NULL,
    discount FLOAT NOT NULL,
    start_date TIMESTAMP NOT NULL DEFAULT now(),
    end_date TIMESTAMP NOT NULL,
    description TEXT
);

CREATE TABLE discount_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    product_id INTEGER REFERENCES products(id),
    discount FLOAT,
    amount FLOAT,
    min_spend FLOAT,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    per_user_limit INTEGER,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_discount_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    discount_code_id INTEGER REFERENCES discount_codes(id) NOT NULL,
    used_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP DEFAULT now()
);
