import streamlit as st

def login():
    with st.container():
        for i in range(30):
            st.text('')
        st.header('Enter Twitter ID')
    
    col1, col2 = st.columns([1,28])
    with col1:
        st.subheader('@')
    with col2:
        st.session_state.twitter_id = st.text_input('', label_visibility='collapsed')
    next_btn()

def next_btn():
    st.button("いいねしたツイートを見る！", on_click=go_choose_topic)

def go_choose_topic():
    st.session_state.page_name = 'choose_topic'