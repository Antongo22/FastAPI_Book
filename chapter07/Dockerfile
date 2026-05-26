FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chapter07 ./chapter07

EXPOSE 8007
CMD ["uvicorn", "chapter07.app.main:app", "--host", "0.0.0.0", "--port", "8007"]
