FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# 啟動指令用 docker-compose 控制，這邊不寫死
CMD ["sh", "-c", "python create_tables.py && python etl.py && gunicorn -k eventlet -w 1 app:app"]

