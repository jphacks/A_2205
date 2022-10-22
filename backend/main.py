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
from setfit import SetFitModel, SetFitTrainer

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


def check_if_user_exists(username: str, twitter_id: str) -> bool:
    return os.path.exists(f"users/{username}") and os.path.exists(f"users/{username}/{twitter_id}")


def train_model(username: str, twitter_id: str, df: pd.DataFrame) -> None:
    print(f"user {username}/{twitter_id} : model training start")
    print()
    dataset = datasets.Dataset.from_pandas(df[["text", "label"]])
    model = SetFitModel.from_pretrained(BASE_MODEL_NAME)
    trainer = SetFitTrainer(
        model=model,
        train_dataset=dataset,
    )
    trainer.train()
    trainer.model.save_pretrained(f"users/{username}/{twitter_id}/model")
    print(f"user {username}/{twitter_id} : model training end")


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}


@app.post("/user/{username}/{twitter_id}")
def create_user(username: str, twitter_id: str):
    if check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} already exists!"}

    if not os.path.exists(f"users/{username}"):
        os.mkdir(f"users/{username}")
    os.mkdir(f"users/{username}/{twitter_id}")

    # create config file
    open(f"users/{username}/{twitter_id}/config", "w").close()

    # create tweets list
    df = pd.DataFrame(columns=["id", "text", "author_name", "topic", "annotated"])
    print(df.columns)
    df.to_csv(f"users/{username}/{twitter_id}/tweets.csv", index=False)

    return {"message": f"Successfully created user {username}/{twitter_id}."}


@app.delete("/user/{username}/{twitter_id}")
def delete_user(username: str, twitter_id: str):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}

    shutil.rmtree(f"users/{username}/{twitter_id}")
    return {"message": f"Successfully deleted user {username}/{twitter_id}."}


@app.post("/topics/{username}/{twitter_id}")
def update_topics(username: str, twitter_id: str, topics: Topic):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}
    with open(f"users/{username}/{twitter_id}/config", "w") as f:
        f.write(",".join(topics.topics))

    return {"message": f"Successfully updated topics for {username}/{twitter_id}."}


@app.get("/topics/{username}/{twitter_id}")
def get_topics(username: str, twitter_id: str):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}

    topics = []
    with open(f"users/{username}/{twitter_id}/config") as f:
        topics = f.readline().split(",")

    return {"data": topics}


@app.post("/annotation/{username}/{twitter_id}")
async def annotate(username: str, twitter_id: str, labels: Label, background_tasks: BackgroundTasks):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}
    # annotate
    df = pd.read_csv(f"users/{username}/{twitter_id}/tweets.csv")
    for tweet_id, label in labels.labels:
        idx = df["id"] == tweet_id
        df.loc[idx, "topic"] = label
        df.loc[idx, "annotated"] = True
    df.to_csv(f"users/{username}/{twitter_id}/tweets.csv", index=False)

    with open(f"users/{username}/{twitter_id}/config", "r") as f:
        topics: List[str] = f.readline().split(",")
    topics_to_label = {label: i for i, label in enumerate(topics)}

    df = pd.read_csv(f"users/{username}/{twitter_id}/tweets.csv")
    df = df[df["annotated"]]
    df["label"] = df["topic"].apply(lambda x: topics_to_label[x])

    # TODO: reshape annotated data
    background_tasks.add_task(train_model, username, df)

    return {"message": "Training..."}


@app.post("/update/{username}/{twitter_id}")
def update(username: str, twitter_id: str):
    crawl_tweets(username, twitter_id)
    return {"message": f"Successfully updated liked tweets for user {username}/{twitter_id}."}


@app.get("/tweets/{username}/{twitter_id}")
def get_tweets(username: str, twitter_id: str, max_results: int = 30, topics: List[str] = Query(None)):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/{twitter_id}/tweets.csv")
    if topics is not None:
        tweets = tweets[np.isin(tweets["topic"], topics)]

    return {
        "data": tweets.head(max_results).to_json(orient="records", force_ascii=False)
    }


@app.get("/podcast/{username}/{twitter_id}/{topic}")
def get_podcast(username: str, twitter_id: str, topic: str):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}

    tweets = pd.read_csv(f"users/{username}/{twitter_id}/tweets.csv")
    tweets_matched = tweets[tweets["topic"] == topic]

    script = ""
    for _, tweet in tweets_matched.iterrows():
        script += f"{tweet['author_name']}さんのツイートです．{tweet['text']}\n"

    return {"data": script}


@app.get("/audio/{username}/{twitter_id}/{tweet_id}")
def get_audio(
    username: str, twitter_id: str, tweet_id: str, text: Text
):
    if not check_if_user_exists(username, twitter_id):
        return {"message": f"User {username}/{twitter_id} does not exist!"}

    pwg_engine = create_tts_engine("multspk_tacotron2_pwg_jvs16k", device="cpu")
    wav, sr = pwg_engine.tts(text.text, spk_id=93)
    write(f"users/{username}/{twitter_id}/{tweet_id}.wav", rate=sr, data=wav)

    with open(f"users/{username}/{twitter_id}/{tweet_id}.wav", "rb") as f:
        contents = f.read()
    with wave.open(f"users/{username}/{twitter_id}/{tweet_id}.wav", "rb") as f:
        fr = f.getframerate()
        fn = f.getnframes()

    play_time = fn / fr
    result = {
        "data": "data:audio/ogg;base64,%s" % (base64.b64encode(contents).decode())
    }

    return result, play_time
