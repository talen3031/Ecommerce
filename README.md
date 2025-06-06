# 簡易電商後台系統_資料庫助教庫

## 專案簡介
本專案為一套**簡易電商後台 API 伺服器**，支援用戶註冊登入、商品管理、訂單管理等核心功能。  
提供 JWT 使用者認證、Swagger API 文件、ORM 資料存取，後端採用 Python Flask 與 PostgreSQL 資料庫設計。  
包含 API 架構、RESTful 設計、資料庫實作、權限驗證、測試自動化等主題。

---

## Requirement

- Python >= 3.8
- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy (或 SQLModel)
- psycopg2
- flasgger
- pytest
- PostgreSQL
---

## 常見功能範例

### 使用者認證 (`/auth/register`, `/auth/login`)
- JWT 註冊、登入、驗證
- 權限控管、Token 管理

### 用戶資訊 (`/users`)
- 查詢用戶資訊 (需登入)

### 商品管理 (`/products`)
- 商品資料查詢
- 商品資料新增（管理員模式）
- 商品資料修改（管理員模式）
- 商品資料刪除（管理員模式）

### 購物車管理 (`/carts`)
- 查詢購物車 (需登入)
- 加入商品至購物車 (需登入)
- 從購物車移除商品 (需登入)
- 更新購物車內容 (需登入)

### 訂單管理 (`/orders`)
- 建立訂單、查詢訂單、訂單明細管理 (需登入)
- 訂單狀態修改 (需登入)

### API 文件 (`/apidocs`)
- Swagger UI 提供互動式 API 測試介面
- 需帶入 JWT Token 驗證

---
