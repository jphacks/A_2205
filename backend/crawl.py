import pandas as pd
import os
import tweepy

bearer_token = os.environ["TWITTER_BEARER_TOKEN"]
api = tweepy.Client(bearer_token=bearer_token)


def crawl_tweets(username: str):
    df_tweets = pd.read_csv(f"users/{username}/tweets.csv")
    user = api.get_user(username=username).data
    user_id = user.get("id")

    # get 100 recently liked tweets and remove duplicates
    tweet_info = api.get_liked_tweets(
        id=user_id, user_fields=["id", "name"], expansions="author_id"
    )
    liked_tweets = tweet_info.data
    users = tweet_info.includes["users"]

    tweet_set = set(df_tweets["id"])
    df_tweets_new = pd.DataFrame.from_records(
        [
            {
                "id": tweet.id,
                "text": tweet.text,
                "author_id": user.username,
                "author_name": user.name,
                "annotated": False,
            }
            for user, tweet in zip(users, liked_tweets)
            if tweet.id not in tweet_set
        ]
    )
    df_tweets = pd.concat([df_tweets_new, df_tweets])
    df_tweets.to_csv(f"users/{username}/tweets.csv", index=False)
