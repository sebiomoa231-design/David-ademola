FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY david_fabric ./david_fabric
COPY config ./config
COPY scripts ./scripts
COPY .env.example ./

RUN mkdir -p /app/data /app/artifacts

EXPOSE 8000

CMD ["uvicorn","david_fabric.main:app","--host","0.0.0.0","--port","8000"]
