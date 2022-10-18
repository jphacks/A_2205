import copy
import time
import requests

import streamlit as st


def choose_topic():
    # select topic
    if st.session_state.add_topic:
        chosen_topic = st.multiselect(
            label='あなたがよく見るツイートのトピックを選択してください',
            options=st.session_state.option_topic,
            default=st.session_state.chosen_topic,
        )
    else:
        chosen_topic = st.multiselect(
            label='あなたがよく見るツイートのトピックを選択してください',
            options=st.session_state.option_topic,
            default=st.session_state.chosen_topic,
        )
        st.session_state.chosen_topic = chosen_topic
    
    # add original topic
    topic = st.text_input(
        label='選択肢にないトピックを追加できます👇',
        value="",
        placeholder='(例)テニス、就活、...etc'
    )
    if st.button(label='追加'):
        if topic:
            if topic not in st.session_state.chosen_topic:
                st.session_state.chosen_topic.append(topic)
                if topic not in st.session_state.option_topic:
                    st.session_state.option_topic.append(topic)
            st.session_state.add_topic = True
            st.experimental_rerun()
    
    st.session_state.add_topic = False

    next_btn()


def next_btn():
    st.button(
        "タグ付けに進む💪",
        on_click=go_annotation,
    )

def go_annotation():
    payload = {
        'topics': st.session_state.chosen_topic,
    }
    res = requests.post(
        f"http://api_server:8080/topics/{st.session_state.twitter_id}",
        json=payload,
    )
    st.session_state.page_name = 'annotation'