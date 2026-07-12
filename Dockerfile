# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# تثبيت المتطلبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الملفات
COPY . .

# تهيئة المجلدات
RUN mkdir -p logs data

# تشغيل البوت
CMD ["python", "-m", "bot.main"]
