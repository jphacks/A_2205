import pandas as pd
import tweepy
import os

bearer_token = os.environ["TWITTER_BEARER_TOKEN"]
api = tweepy.Client(bearer_token=bearer_token)

def crawl_tweets(username: str, max_results: int = 10):
    df_tweets = pd.read_csv(f"users/{username}/tweets.csv")
    user = api.get_user(username=username).data
    user_id = user.get("id")
    tweet_info = api.get_liked_tweets(id=user_id, max_results=max_results, expansions="author_id")
    author_info = tweet_info.includes['users']
    liked_tweets = tweet_info.data
    for author, tweet in zip(author_info, liked_tweets):
        df_tweets = df_tweets.append({"id": tweet.id, "text": tweet.text, "author_name": author.username, "annotated": False}, ignore_index=True)
    df_tweets.to_csv(f"users/{username}/tweets.csv", index=False)
