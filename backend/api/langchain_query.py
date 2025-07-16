from flask import Blueprint, request, jsonify, Response
from langchain_openai import ChatOpenAI
import os
import requests
import re
import json

langchain_bp = Blueprint("langchain", __name__, url_prefix="/langchain")

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

API_DOCS = """
你是一個電商客服助理，只能產生下列 API 指令，不可以產生 SQL。
請根據用戶問題，輸出最適合的 API 請求格式：
格式範例：「GET /orders/123?page=1」
可呼叫的 API：
1. 查詢歷史訂單: GET /orders/{user_id}
   可加參數 ?page=1&per_page=10
2. 查詢訂單明細: GET /orders/order/{order_id}。

3. 查詢購物車: GET /carts/{user_id}
4. 查詢商品: GET /products?keyword=XXX
5. 查詢個人資料: GET /users/{user_id}
6. 查詢推薦商品: GET /users/{user_id}/recommend
如無法回答，請回覆：「無法判斷適合的 API」。
"""

@langchain_bp.route("/query", methods=["POST"])
def langchain_query():
    data = request.json or {}
    query = data.get("query")
    user_id = data.get("user_id")
    jwt_token = data.get("jwt_token")

    if not query or not user_id or not jwt_token:
        return jsonify({"error": "請輸入 query、user_id、jwt_token"}), 400

    sys_prompt = API_DOCS.replace("{user_id}", str(user_id))
    llm_input = f"{sys_prompt}\n用戶問題：{query}"
    response = llm.invoke(llm_input)
    llm_response = response.content.strip()

    match = re.match(r'(GET|POST|PATCH|PUT|DELETE)\s+(/[^\s?]+[^\s]*)', llm_response, re.I)
    if not match:
        # 中文安全 json 回傳
        error_obj = {
            "error": "LLM 沒有產生正確的 API 指令",
            "llm_response": llm_response
        }
        return (
            json.dumps(error_obj, ensure_ascii=False),
            400,
            {"Content-Type": "application/json; charset=utf-8"}
        )

    method, path = match.groups()
    path_with_params = path
    url = f"https://ecommerce-backend-latest-6fr5.onrender.com{path_with_params}"

    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        resp = requests.request(method, url, headers=headers, timeout=6)
        resp.raise_for_status()
        try:
            # 1. 確保 json 也用 utf-8 輸出
            return Response(
                json.dumps({
                    "api_call": f"{method} {url}",
                    "api_response": resp.json(),
                    "llm_decision": llm_response
                }, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        except Exception as e2:
            import traceback
            print("LANGCHAIN ERROR:", str(e2).encode('utf-8', errors='replace').decode('utf-8'))
            print(traceback.format_exc())
            # 2. 若 resp.json() 失敗，直接 decode utf-8（處理 bytes）
            try:
                text = resp.content.decode('utf-8', errors='replace')
            except Exception:
                text = resp.text
                import traceback
                print("LANGCHAIN ERROR:", str(e).encode('utf-8', errors='replace').decode('utf-8'))
                print(traceback.format_exc())
            return Response(
                json.dumps({
                    "api_call": f"{method} {url}",
                    "api_response": text,
                    "llm_decision": llm_response
                }, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
    except Exception as e:
        import traceback
        print("LANGCHAIN ERROR:", str(e).encode('utf-8', errors='replace').decode('utf-8'))
        print(traceback.format_exc())
        # 3. Error message 保證 json + utf-8，永不會因為內容含中文字失敗
        error_obj = {
            "error": f"API 呼叫失敗: {e}",
            "api_call": f"{method} {url}",
            "llm_decision": llm_response
        }
        return (
            json.dumps(error_obj, ensure_ascii=False),
            500,
            {"Content-Type": "application/json; charset=utf-8"}
        )
