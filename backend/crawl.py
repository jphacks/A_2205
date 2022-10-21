import pandas as pd
import os
import tweepy
import aiohttp
import asyncio

bearer_token = os.environ["TWITTER_BEARER_TOKEN"]
api = tweepy.Client(bearer_token=bearer_token)

async def get_reqest(session, url):
    async with session.get(url) as resp:
        res = await resp.json()
        html = res["html"]
        a_name, a_id = (
            html.split("</p>&mdash; ")[1].split(" <a href=")[0].rsplit(" ", 1)
        )
        a_id = a_id[2:-1]
        return a_name, a_id


async def get_author(tweet_id_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for tweet_id in tweet_id_list:
            url = f"https://publish.twitter.com/oembed?url=https://twitter.com/ppp/status/{tweet_id}"
            tasks.append(asyncio.ensure_future(get_reqest(session, url)))
        author_info = await asyncio.gather(*tasks)
    return author_info


def crawl_tweets(username: str):
    df_tweets = pd.read_csv(f"users/{username}/tweets.csv")
    user = api.get_user(username=username).data
    user_id = user.get("id")

    # get 100 recently liked tweets and remove duplicates
    tweet_info = api.get_liked_tweets(id=user_id)
    liked_tweets = tweet_info.data
    tweet_id_list = [tweet.id for tweet in liked_tweets]
    author_info = asyncio.run(get_author(tweet_id_list))

    tweet_set = set(df_tweets["id"])
    df_tweets_new = pd.DataFrame.from_records(
        [
            {
                "id": tweet.id,
                "text": tweet.text,
                "author_id": author[1],
                "author_name": author[0],
                "annotated": False,
            }
            for author, tweet in zip(author_info, liked_tweets)
            if tweet.id not in tweet_set
        ]
    )
    df_tweets = pd.concat([df_tweets_new, df_tweets])
    df_tweets.to_csv(f"users/{username}/tweets.csv", index=False)