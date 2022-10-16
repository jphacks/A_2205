import streamlit as st

def choose_topic_page():
    from audioop import add
    from click import option
    from numpy import choose
    import streamlit as st

    option_topic = [
        'ファッション','ビューティー', 'アウトドア', 'アート', 'カルチャー',
        'アニメ', '漫画', 'ビジネス', '金融', '食べ物', '旅行', 'エンターテインメント',
        '音楽', 'ゲーム業界', 'キャリア', 'ライフスタイル', 'フィットネス',
        'スポーツ', 'テクノロジー', '科学'
    ]

    st.session_state.chosen_topic = []

    st.multiselect(
        label='あなたがよく見るツイートのトピックを選択してください',
        options=option_topic,
        list=st.session_state.chosen_topic
    )

    topic = st.text_input(
        label='選択肢にないトピックを追加できます👇',
        value="",
        placeholder='(例)テニス、就活、...etc'
    )

    st.button(
        label='追加',
        on_click=add_topic(topic=topic)
    )

    st.button(
        label="次のページへ",
        # on_click=go_next_page()
    )

    def add_topic(topic):
        st.session_state.chosen_topic.append(topic)
