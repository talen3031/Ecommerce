FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# 啟動指令用 docker-compose 控制，這邊不寫死
CMD ["sh", "-c", "python create_tables.py && python etl.py && python app.py"]

