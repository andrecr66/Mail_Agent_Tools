FROM python:3.12-slim

# System deps – keep small; lxml wheels usually avoid compilers
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy deps first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY . /app

EXPOSE 8080
ENV PYTHONUNBUFFERED=1

# default entrypoint
CMD ["uvicorn","app.web.app:app","--host","0.0.0.0","--port","8080"]
