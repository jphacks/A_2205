import re
from bs4 import BeautifulSoup
import pandas as pd
import requests as req


def extract_url_from_(tweet): 
    url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tweet)
    return url 

def extract_text_from_(url):
    html = req.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.prettify)

    for script in soup(["script", "style"]):
        script.decompose()

    #print(soup)

    text=soup.get_text()
    #print(text)
    lines= [line.strip() for line in text.splitlines()]
    text="\n".join(line for line in lines if line)

    return text