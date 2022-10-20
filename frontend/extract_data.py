import re
from extractcontent3 import ExtractContent
import requests


def extract_url_from_(tweet): 
    url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tweet)
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