FROM python:3.9-slim

EXPOSE 8888

WORKDIR /backend

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install uvicorn fastapi transformers setfit pandas numpy tweepy

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]