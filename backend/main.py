import numpy as np
import pandas as pd
from fastapi import FastAPI, Query, BackgroundTasks
from pydantic import BaseModel
import os
import shutil
from typing import List, Tuple

from ttslearn.pretrained import create_tts_engine
from scipy.io.wavfile import read, write
import base64
import wave

from crawl import crawl_tweets

import datasets
from setfit import SetFitModel, SetFitModelTrainer

BASE_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class Topic(BaseModel):
    topics: List[str]


class Label(BaseModel):
    labels: List[Tuple[int, str]]


class Text(BaseModel):
    text: str


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

    # TODO: reshape annotated data
    dataset = datasets.Dataset.from_pandas(df)
    model = SetFitModel.from_pretrained(BASE_MODEL_NAME)
    trainer = SetFitModelTrainer(
        model=model,
        train_dataset=dataset,
    )
    trainer.train()
    trainer.model.save_pretrained(f"users/{username}/model")

    return {"message": "Training..."}


@app.post("/annotation/{username}")
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

    return {"message": "Training..."}


@app.post("/update/{username}")
def update(username: str):
    crawl_tweets(username)
    return {"message": f"Successfully updated liked tweets for user {username}."}


@app.get("/tweets/{username}")
def get_tweets(username: str, max_results: int = 30, topics: List[str] = Query(None)):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/tweets.csv")
    if topics is not None:
        tweets = tweets[np.isin(tweets["topic"], topics)]

    return {
        "data": tweets.head(max_results).to_json(orient="records", force_ascii=False)
    }


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


@app.get("/audio/{username}/{tweet_id}")
async def get_audio(
    username: str, tweet_id: str, text: Text, background_tasks: BackgroundTasks
):
    if not check_if_user_exists(username):
        return {"message": f"User {username} does not exist!"}

    pwg_engine = create_tts_engine("multspk_tacotron2_pwg_jvs16k", device="cpu")
    wav, sr = pwg_engine.tts(text.text, spk_id=93)
    write(f"users/{username}/{tweet_id}.wav", rate=sr, data=wav)

    with open(f"users/{username}/{tweet_id}.wav", "rb") as f:
        contents = f.read()
    with wave.open(f"users/{username}/{tweet_id}.wav", "rb") as f:
        fr = f.getframerate()
        fn = f.getnframes()

    play_time = fn / fr
    result = {
        "data": "data:audio/ogg;base64,%s" % (base64.b64encode(contents).decode())
    }

    return result, play_time
