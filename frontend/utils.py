import base64
import streamlit as st
import os
import re
from extractcontent3 import ExtractContent
import requests

SUMMARIZE_API_KEY = os.environ.get("SUMMARIZE_API_KEY")

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



def masic_translate(text):
    masic_words = {'JPHACKS':'ジャパンハックス'}
    for key, value in masic_words.items():
        text = text.replace(key, value)
    return text


def convert_text_into_speechable(text):
    # replace link into 'リンク'
    text, replace_num = re.subn('https?://(?:[-\w./]|(?:%[\da-fA-F]{2}))+', 'リンク', text)
    # if tweet have more than 2 links, last one links itself.
    if replace_num>=2 and text[-3:]=='リンク':
        text = text[:-3]
    # replace # into 'ハッシュタグ'
    text = re.sub('#', 'ハッシュタグ', text)
    # translate masic words
    text = masic_translate(text)
    return text


def summarize_text(text):
    endpoint = 'https://clapi.asahi.com/extract'
    headers = {
        'x-api-key':SUMMARIZE_API_KEY,
    }
    payload = {
        'text':text, 
        'rate':0.1,
    }
    res = requests.post(endpoint, headers=headers, data=payload)
    print(res)
    result = res.json()['result']
    
    summary = ''.join(result)
    summary = summary.replace('<nl>', '')
    summary = summary.replace(' ', '')
    return summary


def gen_manuscript(author_name, tweet_text):
    st.text(tweet_text)
    author_name = convert_text_into_speechable(author_name)
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
            text += summarize_text(convert_text_into_speechable(content))
        else:
            text = text.replace('リンク', '', 1)

    return author_name + "さんのツイートです。" + text

