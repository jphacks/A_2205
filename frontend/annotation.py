import json
import requests
import streamlit as st

def tweet_to_html(url):
    api = f"https://publish.twitter.com/oembed?url={url}"
    res = requests.get(api)
    response = res.json()
    return response["html"]

def annotation():
    MIN_NUM_TWEET = 3
    res = requests.get(f"http://api_server:8080/tweets/{st.session_state.twitter_id}")
    result = json.loads(res.json()["data"])

    if st.button('次へ'):
        st.session_state.annotate_count += 1
    topic = st.session_state.chosen_topic[st.session_state.annotate_count]

    # topic progress bar
    st.progress(st.session_state.annotate_count/len(st.session_state.chosen_topic))

    st.header(
        f'{topic}のツイートを選択してください'
    )

    # tweet selection progress bar
    num_selected_tweets = sum(True for v in st.session_state.labels.values() if v==topic)
    st.text(f'{num_selected_tweets}/{MIN_NUM_TWEET}')
    st.progress(num_selected_tweets/MIN_NUM_TWEET)
    if num_selected_tweets==MIN_NUM_TWEET:
        st.balloons()
        st.balloons()
        st.balloons()
    
    for tweet in result[:3]:
        tweet_id = tweet["id"]
        author_name = tweet["author_name"]
        url = f"https://twitter.com/{author_name}/status/{tweet_id}"
        html = tweet_to_html(url)

        with st.container():
            check = st.checkbox(
                f'{topic}のツイートです',
                key=tweet_id,
            )
            if check:
                st.session_state.labels[tweet_id] = topic
                # reload to refrect to progress-bar
                if not st.session_state.done_reload.get(tweet_id):
                    st.session_state.done_reload[tweet_id] = True
                    st.experimental_rerun()
            st.components.v1.html(html)
            st.write('---')
