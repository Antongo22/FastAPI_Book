FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chapter04 ./chapter04

EXPOSE 8004
CMD ["uvicorn", "chapter04.app.main:app", "--host", "0.0.0.0", "--port", "8004"]
