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

from time import sleep

@st.cache
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
    """
    Convert text to speech.
    Put audio_str and its meta-information into the queue.
    """
    def __init__(self, deamon, text_list, twitter_id, **kwargs):
        super().__init__(**kwargs)
        self.queue = queue.Queue()
        self.text_list = text_list
        self.twitter_id = twitter_id

    def run(self):
        for text, tweet_id, author_name in self.text_list:
            payload = {
                "text":author_name + "さんのツイートです。" + text,
            }
            res = requests.get(
                f'http://api_server:8080/audio/{self.twitter_id}/{tweet_id}', 
                json=payload
            )
            result = res.json()
            self.queue.put(result)
        
        # Put the flag of end.
        self.queue.put([{"data":"finish"},1])


# class Worker2(threading.Thread):
#     """
#     Get tweet_info from the queue and play audio.
#     """
#     def __init__(self, deamon, worker, **kwargs):
#         super().__init__(**kwargs)
#         self.worker = worker
#         self.queue = worker.queue

#     def run(self):
#         while True:
#             audio_placeholder = st.empty()
#             tweet_info = self.queue.get()
#             audio_str = tweet_info[0]["data"]
#             play_time = tweet_info[1] 

#             if audio_str=="finish":
#                 break

#             audio_html = """
#                             <audio autoplay=True>
#                             <source src="%s" type="audio/ogg" autoplay=True>
#                             Your browser does not support the audio element.
#                             </audio>
#                         """ %audio_str

#             time.sleep(0.5) 
#             audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
#             time.sleep(play_time+1)
#             self.queue.task_done()
            

def tweet_list():
    worker1 = None

    col1, col2, _ = st.columns([1,1,10])
    play = col1.button("play")
    stop = col2.button("stop")

    username = st.session_state.twitter_id
    res = requests.get(f'http://api_server:8080/topics/{username}')
    chosen_topic = res.json()["data"]

    topics = st.multiselect(
            label='トピックを選んでください',
            options=chosen_topic,
        ) or None

    res = requests.get(f'http://api_server:8080/tweets/{username}')
    tweets = st.session_state.tweets = json.loads(res.json()["data"])

    if topics is not None:
        tweets = st.session_state.tweets = [tweet for tweet in tweets if tweet['topic'] in topics]

    for tweet in tweets[:10]:
        tweet_id = tweet["id"]
        author_id = tweet["author_id"]

        url = f"https://twitter.com/{author_id}/status/{tweet_id}"
        html = tweet_to_html(url)
        components.html(html, height=300, scrolling=True)

    if play:
        text_list = [[tweet["text"], tweet["id"], tweet["author_name"]] for tweet in st.session_state.tweets]

        worker1 = st.session_state.worker1 = Worker1(deamon=True, text_list=text_list, twitter_id=st.session_state.twitter_id)
        add_script_run_ctx(worker1)
        worker1.start()

        while True:
            audio_placeholder = st.empty()
            tweet_info = worker1.queue.get()
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
            worker1.queue.task_done()
            
        if worker1.is_alive():
            worker1.join()
            st.experimental_rerun()

    if worker1:
        while worker1.is_alive():
            if stop:
                if worker1.is_alive():
                    worker1.join()
                    st.experimental_rerun()
            time.sleep(1)

                