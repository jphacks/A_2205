import pandas as pd
import os
import tweepy

bearer_token = os.environ["TWITTER_BEARER_TOKEN"]
api = tweepy.Client(bearer_token=bearer_token)


def crawl_tweets(username: str, twitter_id: str):
    path = f"users/{username}/{twitter_id}/tweets.csv"
    df_tweets = pd.read_csv(path)
    user = api.get_user(username=twitter_id).data
    user_id = user.get("id")

    # get 100 recently liked tweets and remove duplicates
    tweet_info = api.get_liked_tweets(id=user_id, user_fields=["id", "name"], expansions="author_id")
    users = {user.id: user for user in tweet_info.includes["users"]}
    liked_tweets = tweet_info.data

    tweet_set = set(df_tweets["id"])
    df_tweets_new = pd.DataFrame.from_records(
        [
            {
                "id": tweet.id,
                "text": tweet.text,
                "author_id": users[tweet.author_id].username,
                "author_name": users[tweet.author_id].name,
                "annotated": False,
            }
            for tweet in liked_tweets
            if tweet.id not in tweet_set
        ]
    )
    df_tweets = pd.concat([df_tweets_new, df_tweets])
    df_tweets.to_csv(path, index=False)