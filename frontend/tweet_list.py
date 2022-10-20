import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime.scriptrunner import add_script_run_ctx
import requests
import json
import os
import numpy as np
import base64
import time
import threading
import queue


def tweet_to_html(url):
    api = f"https://publish.twitter.com/oembed?url={url}"
    res = requests.get(api)
    response = res.json()
    return response["html"]

def back_btn():
    st.button("戻る", on_click=go_login)

def go_login():
    st.session_state.page_name = 'login'


class Worker1(threading.Thread):
    def __init__(self, text_list, twitter_id, **kwargs):
        super().__init__(**kwargs)
        self.queue = queue.Queue()
        self.text_list = text_list
        self.twitter_id = twitter_id

    def run(self):
        for text, tweet_id in self.text_list:
            payload = {
                "text":text,
            }
            res = requests.get(
                f'http://api_server:8080/audio/{self.twitter_id}/{tweet_id}', 
                json=payload
            )
            result = res.json()
            self.queue.put(result)
        
        self.queue.put([{"data":"finish"},1])


class Worker2(threading.Thread):
    def __init__(self, worker, **kwargs):
        super().__init__(**kwargs)
        self.worker = worker
        self.queue = worker.queue

    def run(self):
        while True:
            audio_placeholder = st.empty()
            tweet_info = self.queue.get()
            audio_str = tweet_info[0]["data"]
            play_time = tweet_info[1] 

            if audio_str=="finish":
                break

            audio_html = """
                            <audio autoplay=True>
                            <source src="%s" type="audio/ogg" autoplay=True>
                            Your browser does not support the audio element.
                            </audio>
                        """ %audio_str

            time.sleep(0.5) 
            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
            time.sleep(play_time+1)
            self.queue.task_done()
            

def tweet_list():
    worker1 = None
    worker2 = None

    # worker1 を制御（起動/停止）する部分
    with st.container():
        if st.button('Play'):
            text_list = [[tweet["text"],tweet["id"]] for tweet in st.session_state.tweets if tweet["id"] in st.session_state.play_id]

            worker1 = st.session_state.worker1 = Worker1(text_list=text_list, twitter_id=st.session_state.twitter_id)
            add_script_run_ctx(worker1)
            worker1.start()

            worker2 = st.session_state.worker2 = Worker2(worker=worker1)
            add_script_run_ctx(worker2)
            worker2.start()

            worker1.join()
            worker2.join()
            st.experimental_rerun()

        if worker2:
            while worker2.is_alive():
                time.sleep(1)
    #--------------------------------------

    username = st.session_state.twitter_id
    res = requests.get(f'http://api_server:8080/topics/{username}')
    chosen_topic = res.json()["data"]

    topics = st.multiselect(
            label='トピックを選んでください',
            options=chosen_topic,
        ) or None

    res = requests.get(f'http://api_server:8080/tweets/{username}')
    tweets = json.loads(res.json()["data"])

    if topics is not None:
        tweets = [tweet for tweet in tweets if tweet['topic'] in topics]

    st.session_state.tweets = tweets

    for tweet in tweets[:10]:
        with st.container():
            tweet_id = tweet["id"]
            author_name = tweet["author_name"]

            check = st.checkbox(
                    f'再生リスト',
                    key=tweet_id,
                )
            if check:
                st.session_state.play_id.append(tweet_id)

            url = f"https://twitter.com/{author_name}/status/{tweet_id}"
            html = tweet_to_html(url)
            components.html(html, height=300, scrolling=True)


    back_btn()
