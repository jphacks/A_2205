import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from pydantic import BaseModel
import os
import shutil
from typing import List, Tuple

from crawl import crawl_tweets


class Topic(BaseModel):
    topics: List[str]

class Label(BaseModel):
    labels: List[Tuple[int, str]]


app = FastAPI()

if not os.path.exists("users"):
    os.mkdir("users")


def check_if_user_exists(username: str) -> bool:
    return os.path.exists(f"users/{username}")


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}


@app.post("/user/{username}")
def create_user(username: str):
    if check_if_user_exists(username):
        return {"message": f"User {username} already exists!"}

    os.mkdir(f"users/{username}")

    # create config file
    open(f"users/{username}/config", "w").close()

    # create tweets list
    df = pd.DataFrame(columns=["id", "text", "author_name", "topic", "annotated"])
    print(df.columns)
    df.to_csv(f"users/{username}/tweets.csv", index=False)

    return {"message": f"Successfully created user {username}."}


@app.delete("/user/{username}")
def delete_user(username: str):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    shutil.rmtree(f"users/{username}")
    return {"message": f"Successfully deleted user {username}."}


@app.post("/topics/{username}")
def update_topics(username: str, topics: Topic):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    with open(f"users/{username}/config", "w") as f:
        f.write(",".join(topics.topics))

    return {"message": f"Successfully updated topics for {username}."}


@app.get("/topics/{username}")
def get_topics(username: str):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    topics = []
    with open(f"users/{username}/config") as f:
        topics = f.readline().split(",")

    return {"data": topics}



@app.post("/train/{username}")
def train(username: str, labels: Label):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    # annotate
    df = pd.read_csv(f"users/{username}/tweets.csv")
    for tweet_id, label in labels.labels:
        idx = df["id"] == tweet_id
        df.loc[idx, "topic"] = label
        df.loc[idx, "annotated"] = True
    df.to_csv(f"users/{username}/tweets.csv", index=False)

    # TODO: start training

    return {"message": "Training..."}


@app.post("/update/{username}")
def update(username: str):
    crawl_tweets(username)
    return {"message": f"Successfully updated liked tweets for user {username}."}


@app.get("/tweets/{username}")
def get_tweets(username: str, max_results: int = 10, topics: List[str] = Query(None)):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/tweets.csv")
    if topics is not None:
        tweets = tweets[np.isin(tweets["topic"], topics)]

    return {"data": tweets.head(max_results).to_json(orient="records", force_ascii=False)}


@app.get("/podcast/{username}/{topic}")
def get_podcast(username: str, topic: str):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/tweets.csv")
    tweets_matched = tweets[tweets["topic"] == topic]

    script = ""
    for _, tweet in tweets_matched.iterrows():
        script += f"{tweet['author_name']}さんのツイートです．{tweet['text']}\n"

    return {"data": script}

