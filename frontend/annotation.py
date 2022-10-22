import os
import json
import requests
import streamlit as st

API_ENDPOINT = os.environ.get("API_ENDPOINT")


@st.cache
def tweet_to_html(url):
    api = f"https://publish.twitter.com/oembed?url={url}"
    res = requests.get(api)
    print(res.raise_for_status())
    response = res.json()
    return response["html"]


def annotation():
    NUM_MIN_TWEET = 3
    NUM_DEAFULT_SHOW_TWEET = 10
    # get tweet at only first time
    if not st.session_state.init_annotation:
        res = requests.get(f"{API_ENDPOINT}/tweets/{st.session_state.twitter_id}")
        st.session_state.not_annotated_tweets = json.loads(res.json()["data"])
        st.session_state.init_annotation = True

    show_tweets = st.session_state.not_annotated_tweets[:NUM_DEAFULT_SHOW_TWEET]

    # count annotated topic num
    if st.session_state.annotate_count <= len(st.session_state.chosen_topic) - 1:
        if st.button("次のラベルへ"):
            st.session_state.annotate_count += 1
            # exclude labeled tweets
            st.session_state.not_annotated_tweets = [
                tw
                for tw in st.session_state.not_annotated_tweets
                if tw["id"] not in st.session_state.labels
            ]
            show_tweets = st.session_state.not_annotated_tweets[:NUM_DEAFULT_SHOW_TWEET]
        # reload to hide this button
        if st.session_state.annotate_count == len(st.session_state.chosen_topic):
            st.experimental_rerun()
    # show next page
    if st.session_state.annotate_count == len(st.session_state.chosen_topic):
        st.balloons()
        next_btn()

    try:
        topic = st.session_state.chosen_topic[st.session_state.annotate_count]
    except IndexError:
        topic = st.session_state.chosen_topic[-1]
    num_selected_tweets = sum(
        True for v in st.session_state.labels.values() if v == topic
    )
    # topic progress bar
    st.progress(st.session_state.annotate_count / len(st.session_state.chosen_topic))

    if st.session_state.annotate_count != len(st.session_state.chosen_topic):
        # show title
        st.header(f"{topic}のツイートを選択してください")
        # tweet selection progress bar
        st.text(f"{num_selected_tweets}/{NUM_MIN_TWEET}")
        st.progress(min(num_selected_tweets / NUM_MIN_TWEET, 1.0))

        # show tweets
        for tweet in show_tweets:
            tweet_id = tweet["id"]
            author_id = tweet["author_id"]
            url = f"https://twitter.com/{author_id}/status/{tweet_id}"
            html = tweet_to_html(url)
            with st.container():
                check = st.checkbox(
                    f"{topic}のツイートです",
                    key=tweet_id,
                )
                if check:
                    st.session_state.labels[tweet_id] = topic
                    # reload to refrect to progress-bar
                    if not st.session_state.done_reload.get(tweet_id):
                        st.session_state.done_reload[tweet_id] = True
                        st.experimental_rerun()
                # st.markdown(html, unsafe_allow_html=True)
                st.components.v1.html(html, height=300, scrolling=True)
                st.write("---")
    else:
        st.header(f"全てのアノテーションが完了しました🎉")


def next_btn():
    st.button(
        "ツイートを見る🤗",
        on_click=go_tweet_list,
    )


def go_tweet_list():
    payload = {
        "labels": list(st.session_state.labels.items()),
    }
    res = requests.post(
        f"{API_ENDPOINT}/annotation/{st.session_state.twitter_id}",
        json=payload,
    )
    st.session_state.page_name = "tweet_list"
