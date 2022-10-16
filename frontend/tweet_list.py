import streamlit as st
import streamlit.components.v1 as components 
import requests
import json
import os

def tweet_to_html(url):
    api = f"https://publish.twitter.com/oembed?url={url}"
    res = requests.get(api)
    response = res.json()
    return response["html"]

def tweet_list():
    # username = st.session_state.twitter_id
    username = "i_amppp"
    if username:
        res = requests.post(f"http://api_server:8080/create_user/{username}")
        st.write(res)
        res = requests.post(f"http://api_server:8080/update/{username}")
        st.write(res)

        if st.button("ツイートを表示する"):
            res = requests.get(f'http://api_server:8080/tweets/{username}')

            result = res.json()["data"]
            tweet_id = json.loads(result)["id"]
            author_name = json.loads(result)["author_name"]

            for id, name in zip(tweet_id.values(), author_name):
                url = f"https://twitter.com/{name}/status/{id}"
                html = tweet_to_html(url)
                st.components.v1.html(html)

tweet_list()