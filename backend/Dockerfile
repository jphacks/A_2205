FROM python:3.9-slim

EXPOSE 8888

WORKDIR /backend

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    cmake \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install numpy
RUN pip3 install uvicorn fastapi transformers setfit pandas tweepy ttslearn

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
