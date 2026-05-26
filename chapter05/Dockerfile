FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chapter05 ./chapter05

EXPOSE 8005
CMD ["uvicorn", "chapter05.app.main:app", "--host", "0.0.0.0", "--port", "8005"]
