import base64
import streamlit as st
import re
from extractcontent3 import ExtractContent
import requests

def set_png_as_page_bg(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
    page_bg_img = f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """
    st.markdown(page_bg_img, unsafe_allow_html=True)


def extract_url_from_(tweet): 
    url = re.findall('https?://(?:[-\w./]|(?:%[\da-fA-F]{2}))+', tweet)
    return url 


def extract_text_from_(url):
    extractor = ExtractContent()

    opt = {
        "threshold": 0,
    }
    extractor.set_option(opt)

    res = requests.get(url)
    html = res.text
    extractor.analyse(html)
    text, title = extractor.as_text()

    return text, title


def convert_text_into_speechable(text):
    # replace link into 'リンク'
    text, replace_num = re.subn('https?://(?:[-\w./]|(?:%[\da-fA-F]{2}))+', 'リンク', text)
    # if tweet have more than 2 links, last one links itself.
    if replace_num>=2 and text[-3:]=='リンク':
        text = text[:-3]
    # replace # into 'ハッシュタグ'
    speechable_text = re.sub('#', 'ハッシュタグ', text)
    return speechable_text


def gen_manuscript(tweet_text):
    st.text(tweet_text)
    text = convert_text_into_speechable(tweet_text)

    links = extract_url_from_(tweet_text)
    st.text(links)
    for link in links:
        content, title = extract_text_from_(link)
        if content and title:
            st.text(title)
            st.text(content)
            text += '。リンク内容。'
            text += convert_text_into_speechable(title)
            text += convert_text_into_speechable(content)
        else:
            text = text.replace('リンク', '', 1)

    return text