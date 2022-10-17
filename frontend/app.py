import base64
import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import copy
import os

from login import login
from choose_topic import choose_topic
from tweet_list import tweet_list
from utils import set_png_as_page_bg


BACKGROUND_IMAGE_PATH = {
    'login': 'images/login.png',
    'choose_topic': 'images/black.png',
    'tweet_list': 'images/black.png',
    'page2': 'images/black.png'
}

def init():
    if st.session_state.get('init') is None:
        st.session_state.init=True
        st.session_state.page_name = 'login'
        st.session_state.twitter_id = None
        st.session_state.option_topic = [
            'ファッション','ビューティー', 'アウトドア', 'アート', 'カルチャー',
            'アニメ', '漫画', 'ビジネス', '金融', '食べ物', '旅行', 'エンターテインメント',
            '音楽', 'ゲーム業界', 'キャリア', 'ライフスタイル', 'フィットネス',
            'スポーツ', 'テクノロジー', '科学'
        ]
        st.session_state.add_topic = False
        st.session_state.default_topic = []

def page2():
    with st.container():
        st.write('page2')

pages = {'login':login, 'choose_topic':choose_topic, 'tweet_list':tweet_list, 'page2':page2}


init()

# set background
bg_img_path = BACKGROUND_IMAGE_PATH[st.session_state.page_name]
set_png_as_page_bg(bg_img_path)

now_page = pages[st.session_state.page_name]
now_page()


