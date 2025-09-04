FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 安裝 nginx（不用 gettext-base）
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
# 起 API（8000） gunicorn -w 2 -b 127.0.0.1:8000 app:app 
# 起 SocketIO（8001）gunicorn -k eventlet -w 1 -b 127.0.0.1:8001 app:app  
# 用 envsubst 把 $PORT 帶進 nginx.conf 
# 啟動 Nginx（監聽 $PORT，分流到 8000/8001）
CMD ["sh", "-c", "python create_tables.py && gunicorn -w 2 -b 127.0.0.1:8000 app:app & gunicorn -k eventlet -w 1 -b 127.0.0.1:8001 app:app & nginx -g 'daemon off;'"]
