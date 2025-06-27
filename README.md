# 簡易電商後台系統_資料庫助教庫

## 專案簡介
本專案為一套**簡易電商後台 API 伺服器**，支援用戶註冊登入、商品管理、訂單管理等核心功能。  
提供 JWT 使用者認證、Swagger API 文件、ORM 資料存取，後端採用 Python Flask 與 PostgreSQL 資料庫設計。  
包含 API 架構、RESTful 設計、資料庫實作、權限驗證、測試自動化(pytest)、管理員操作日誌（Audit Log）、分頁查詢、Service Layer 重構。  
---

## 系統架構特色

- **RESTful API 設計，前後端分離，支援 JWT 權杖認證**
- **Service Layer 分層**
  - 商業邏輯與資料查詢分離，易於擴充與單元測試
- **操作日誌（Audit Log）**  
  - 重要操作（商品增刪改、結帳、購物車異動、用戶登入/註冊...）皆自動寫入日誌表，便於稽核與追蹤
- **分頁功能**  
  - 商品/訂單列表等查詢皆支援分頁
- **Swagger/OpenAPI 自動產生 API 文件**  
- **異常統一處理與友善錯誤回傳**

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
## 主要功能

### 用戶（User）
- 註冊、登入（JWT）、權限控管（管理員/一般用戶）
- 查詢個人資訊／管理員查詢全用戶

### 商品（Product）
- 查詢（支援分頁、搜尋、分類篩選）
- 新增／修改／刪除（管理員）
- 商品唯一性檢查

### 購物車（Cart）
- 加入／移除商品
- 調整商品數量
- 查詢購物車
- 結帳（可選全部或指定商品結帳）

### 訂單（Order）
- 歷史訂單查詢（支援分頁）
- 查詢單筆訂單明細
- 訂單狀態流轉（取消、出貨等）

### **操作日誌（Audit Log）**
- 所有重要資料異動皆自動記錄，包含：
  - 商品增刪改
  - 用戶註冊／登入／登入失敗
  - 購物車商品加入／移除／數量調整／結帳
  - 訂單建立與狀態修改
- 日誌查詢介面（限管理員）

---

## Service Layer 範例

所有商業邏輯集中於 service 層，例如：

```python
class ProductService:
    @staticmethod
    def search(..., page=1, per_page=10):
        ...
        return query.paginate(page=page, per_page=per_page, error_out=False)
