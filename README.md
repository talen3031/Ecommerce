# 電商系統（Nerd.com）

## 專案總覽

本專案是一個**全端電商平台Nerd.com**，涵蓋後端 API、前端網站、用戶通知、資料庫、CI/CD、第三方服務整合與推薦系統等多種功能。  
後端以 **Python Flask + PostgreSQL** 開發，前端採用 **React.js**，並已部署於 Render。

- [Nerd.com](https://ecommerce-frontend-latest.onrender.com)
- [後端 API（Swagger 文件）](https://ecommerce-backend-latest-6fr5.onrender.com/apidocs/)
> 免費 Render Web Service 會在 15 分鐘無人使用時自動休眠，喚醒需 10~60 秒，請耐心等候。

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
- sendgrid
- dotenv
- cloudinary
- gspread 
- google-auth
- line-bot-sdk
---

## 系統架構特色

- **系統架構（簡化圖）**：  
    ```text
    Client ←→ View Layer(前端React)←→ Route Layer(API Route) ←→ Service Layer ←→ ORM Layer ←→ PostgreSQL 資料庫
    ```                
- **RESTful API 設計、Swagger API 文件**
- **JWT 認證／權限控管**（區分管理員、一般用戶）
- **ORM（SQLAlchemy）**
- **Service Layer 商業邏輯分層**
- **自動化測試（pytest）** ：Intergration TEST 整合測試
- **推薦系統**：協同過濾、個人化推薦
- **操作稽核日誌（Audit Log）**：所有關鍵操作皆自動記錄至Audit Log
- **第三方 API 整合**：SendGrid Email、LINE Messaging API、Cloudinary 圖片雲
- **Docker 容器化**：  前端 (React)、後端 (Flask) 及資料庫 (PostgreSQL) 各自獨立打包成 Docker image。
- **CI/CD 自動化部署**（GitHub Actions + Docker Hub）
    - 執行 pytest(intergration test) 成功後 build & push backend/frontend Docker image
    - CI/CD流程圖
    ```text
    Git push / PR
        │
        ▼
    GitHub Actions 啟動 Workflow
        │
        │
        ├──► [Services] 啟動 Postgres 容器 (在 Runner VM 內)
        │         │
        │         ▼
        │   Postgres 服務 (Runner 上的 localhost:5432)
        │
        ├──► [Test] Runner VM 安裝依賴、執行 pytest
        │         │
        │         ▼
        │   測試時連 localhost:5432（實際是上面那個 Postgres 容器）
        │
        │
        └──► [Build & Push] 
                  │
                  ├── build backend image
                  ├── build frontend image
                  └── push 到 Docker Hub (talen3031/ecommerce-backend:latest, frontend:latest)
    ```

    
---

## 主要技術

- **後端**：Python 3.8+ / Flask / Flask-JWT-Extended / SQLAlchemy / Flasgger / psycopg2 / dotenv
- **資料庫**：PostgreSQL
- **前端**：React.js / Ant Design / Axios
- **測試**：pytest
- **DevOps**：Docker  / GitHub Actions / Docker Hub
- **雲端整合**：Render（主機及資料庫部署）、SendGrid（Email）、Cloudinary（圖片上傳）、LINE Messaging API（綁定後可即時通知）

---

## 功能總覽

### 1. 用戶管理
- 註冊、登入、JWT 驗證
- 查詢個人／全部用戶資料（管理員專屬）
- 重設密碼（Email 發送驗證連結）
- 綁定 LINE 帳號（登入／通知）

### 2. 商品系統
- 商品查詢（支援分頁、分類、關鍵字、價格區間）
- 管理員新增／修改／刪除／上下架商品
- 商品唯一性檢查
- 圖片上傳（Cloudinary）
- 商品特價設定（區間／折扣）

### 3. 購物車系統
- 加入／移除商品、調整數量
- 查詢目前購物車（僅顯示未結帳的 active 狀態）
- 支援部分結帳（選擇部分商品進行結帳）
- 分頁查詢、推薦相關商品

### 4. 訂單管理
- 下單（結帳）、歷史訂單查詢、明細查詢
- 訂單狀態流轉
- 用戶可取消、查詢自己的訂單，管理員可查詢所有訂單、調整狀態

### 5. 折扣碼與優惠券
- 管理員新增／停用折扣碼，支援金額與折扣率兩種型態(ex.折扣100元 or 9折)
- 支援專屬商品折扣、滿額限制、總次數／每人次數限制
- 用戶購物車可查詢並套用折扣碼，結帳時自動計算

### 6. 推薦商品
- **個人推薦**：依用戶歷史訂單，推薦同分類熱賣商品
- **購物車推薦**：根據購物車內容推薦相關商品
- **協同過濾**：推薦其他同時購買「你購物車內商品」的客戶還買過哪些商品

### 7. 通知系統
- **Email 通知**：訂單成立／異動、特價提醒、忘記密碼等自動發信
- **LINE web message API**：訂單成立、狀態變更推播通知，購物車商品特價提醒
- **日誌系統（Audit Log）**：所有重要操作皆自動記錄於資料庫，便於稽核與追蹤

### 8. 圖片雲端上傳
- 商品圖片可上傳至 Cloudinary，返回雲端公開網址

### 9. Swagger API 文件
- 內建 `/apidocs/` 提供全 API 自動文件，可直接線上測試
- https://ecommerce-backend-latest-6fr5.onrender.com/apidocs/

### 10. CI/CD 與 Docker
- 開發、測試、部署全自動化，CI 通過後自動 build/push 至 Docker Hub
---
