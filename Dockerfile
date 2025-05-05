FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY led_sales_tracker ./led_sales_tracker
COPY .env.example ./
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "led_sales_tracker.main"]