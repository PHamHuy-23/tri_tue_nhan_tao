# Backend API (gồm thuat_toan). Build từ thư mục Visualization:
#   docker build -t ai-visualizer-api .
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY thuat_toan/ thuat_toan/
COPY backend/app/ backend/app/

ENV PYTHONPATH=/app
WORKDIR /app/backend
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
