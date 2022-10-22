import os
import json
import requests
import streamlit as st

API_ENDPOINT = os.environ.get("API_ENDPOINT")
    
def login():
    with st.container():
        for i in range(30):
            st.text("")
        
        st.header("Enter Username")
        st.session_state.username = st.text_input("", label_visibility="collapsed", key=1)

        st.header("Enter Twitter ID")

    col1, col2 = st.columns([1, 28])
    with col1:
        st.subheader("@")
    with col2:
        st.session_state.twitter_id = st.text_input("", label_visibility="collapsed", key=2)
    next_btn()


def next_btn():
    st.button("いいねしたツイートを見る！", on_click=go_choose_topic)


def go_choose_topic():
    res = requests.post(
        f"{API_ENDPOINT}/user/{st.session_state.username}/{st.session_state.twitter_id}",
    )
    res = requests.get(f"{API_ENDPOINT}/tweets/{st.session_state.username}/{st.session_state.twitter_id}")
    result = json.loads(res.json()["data"])

    # st.session_state.result = result

    if result == []:
        res = requests.post(
            f"{API_ENDPOINT}/update/{st.session_state.username}/{st.session_state.twitter_id}",
        )

    if sum(r["annotated"] for r in result):
        st.session_state.page_name = "tweet_list"
    else:
        st.session_state.page_name = "choose_topic"
