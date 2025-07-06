# 電商系統

## 專案簡介
本專案為一套簡易電商 API 伺服器，後端採用 Python Flask 與 PostgreSQL 資料庫設計，前端採用 react 與 javascript 設計。
- **RESTful API 設計、Swagger API 文件**
- **JWT 認證／權限控管**（支援管理員與一般用戶）
- **ORM 資料存取 (SQLAlchemy) 、資料庫實作 建立**
- **測試自動化(pytest)**
- **推薦功能(協同過濾)**
  - 根據目前使用者購物出內容 找出同樣買了這些商品的其他客戶也買了什麼商品
- **管理員操作日誌（Audit Log）**
  - 重要操作（商品增刪改、結帳、購物車異動、用戶登入/註冊...）皆自動寫入日誌表，便於稽核與追蹤
- **分頁查詢**
  - 商品/訂單列表等查詢皆支援分頁
- **整合第三方API (用戶自動通知 Email)**
  - 本專案整合 SendGrid 提供自動通知 Email** 例如當有商品新增特價活動時，若用戶購物車有該商品，會主動通知用戶。
- **Service Layer**
  - 從MVC架構中分離出service layer，將商業邏輯與資料查詢分離，易於擴充與單元測試。 
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
---

## 主要功能

### 用戶（User）
  - 註冊、登入（JWT）、權限控管（管理員/一般用戶）
  - 查詢個人資訊／管理員查詢全用戶
  - 忘記密碼／重新設定密碼

### 商品（Product）
  - 查詢（支援分頁、搜尋、分類篩選）
  - 新增／修改／刪除（管理員）
  - 商品唯一性檢查
  - 商品特價功能

### 購物車（Cart）
  - 加入／移除商品
  - 調整商品數量
  - 查詢購物車
  - 結帳（可選全部或指定商品結帳）

### 訂單（Order）
  - 歷史訂單查詢（支援分頁）
  - 查詢單筆訂單明細
  - 訂單狀態流轉（取消、出貨等）

### 自動 Email 通知功能
  - 用戶購物車結帳成功，系統自動發送訂單成立信到用戶信箱。
  - 訂單狀態（如付款成功、出貨、完成、取消等）異動時，自動寄信通知用戶。 
  - 當有商品新增特價活動時，若用戶購物車有該商品，會主動通知用戶。

### 推薦功能 (你可能喜歡...)
  - 個人推薦(根據使用者訂單紀錄)
  - 協同過濾(根據目前使用者購物出內容 找出同樣買了這些商品的其他客戶也買了什麼商品)

### 操作日誌（Audit Log）
  - 所有重要資料異動皆自動記錄，包含：
  - 商品增刪改
  - 用戶註冊／登入／登入失敗
  - 購物車商品加入／移除／數量調整／結帳
  - 訂單建立與狀態修改
  - 日誌查詢介面（限管理員）

## 容器化 (Docker) 與 CI/CD 流程 (GitHub Actions + Docker Hub)

### 容器化 (Docker)

前端 (React)、後端 (Flask) 及資料庫 (PostgreSQL) 各自獨立打包成 Docker image。可藉由 `docker-compose` 快速在任意平台啟動完整開發/測試/部署環境。

#### 快速啟動

```bash
docker-compose up --build
---
```
###  CI/CD 流程 (GitHub Actions + Docker Hub)
- **GitHub Actions workflow**
  - 每次 Push 到 main/master 分支，會自動啟動 GitHub Actions workflow，分別 build backend/frontend Docker image，自動推送到 Docker Hub（以 latest 標籤），專案根目錄下的 .github/workflows/cicd.yml 定義了完整自動化流程
- **伺服器端部署/升級**
  - 伺服器可直接 docker pull 取回最新版 image，一鍵重啟服務，快速同步最新程式
- **CI/CD流程圖**
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