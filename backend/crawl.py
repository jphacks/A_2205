import pandas as pd
import tweepy
import os

bearer_token = os.environ["TWITTER_BEARER_TOKEN"]
api = tweepy.Client(bearer_token=bearer_token)

def crawl_tweets(username: str, max_results: int = 10):
    df_tweets = pd.read_csv(f"users/{username}/tweets.csv")
    user = api.get_user(username=username).data
    user_id = user.get("id")
    liked_tweets = api.get_liked_tweets(id=user_id, max_results=max_results).data
    for tweet in liked_tweets:
        df_tweets = df_tweets.append({"id": tweet.id, "text": tweet.text}, ignore_index=True)
    df_tweets.to_csv(f"users/{username}/tweets.csv", index=False)