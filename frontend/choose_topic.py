import copy
import time

import streamlit as st


def choose_topic():
    # select topic
    if st.session_state.add_topic:
        chosen_topic = st.multiselect(
            label='あなたがよく見るツイートのトピックを選択してください',
            options=st.session_state.option_topic,
            default=st.session_state.default_topic,
        )
    else:
        chosen_topic = st.multiselect(
            label='あなたがよく見るツイートのトピックを選択してください',
            options=st.session_state.option_topic,
            default=st.session_state.default_topic,
        )
        st.session_state.default_topic = chosen_topic

    # add original topic
    topic = st.text_input(
        label='選択肢にないトピックを追加できます👇',
        value="",
        placeholder='(例)テニス、就活、...etc'
    )
    st.text(topic)
    if st.button(label='追加'):
        if topic not in st.session_state.default_topic:
            st.session_state.default_topic.append(topic)
            if topic not in st.session_state.option_topic:
                st.session_state.option_topic.append(topic)
        st.session_state.add_topic = True
        st.experimental_rerun()
    
    st.session_state.add_topic = False

    next_btn()


def next_btn():
    st.button(
        "いいねしたツイートを見る！",
        on_click=go_tweet_list,
        # args=(chosen_topic,)
    )

def go_tweet_list():
    st.session_state.page_name = 'tweet_list'