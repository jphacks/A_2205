import pandas as pd
from fastapi import FastAPI
import os

from crawl import crawl_tweets


app = FastAPI()

if not os.path.exists("users"):
    os.mkdir("users")


def check_if_user_exists(username: str) -> bool:
    return os.path.exists(f"users/{username}")


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}


@app.post("/create_user/{username}")
def create_user(username: str):
    if check_if_user_exists(username):
        return {"message": f"User {username} already exists!"}

    os.mkdir(f"users/{username}")
    df = pd.DataFrame(columns=["id", "text", "label"])
    df.to_csv(f"users/{username}/tweets.csv", index=False)
    return {"message": f"Successfully created user {username}."}


@app.post("/train/{username}")
def train(username: str):
    return {"message": "Training"}


@app.post("/update/{username}")
def update(username: str):
    crawl_tweets(username)
    return {"message": f"Successfully updated liked tweets for user {username}"}


@app.get("/tweets/{username}")
def get_tweets(username: str, max_results: int = 10):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/tweets.csv")
    return {"data": tweets.head(max_results).to_json(force_ascii=False)}


@app.get("/podcast/{username}/{topic}")
def get_podcast(username: str, topic: str):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/tweets.csv")
    tweets_matched = tweets[tweets["label"] == topic]

    # TODO: create a script from tweets

    # TODO: create an audio from the script

    return {"data": "podcast"}

