import requests
import pytz
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

TRUMP_SITE_URL = 'https://www.donaldjtrump.com/desk'

def scrape_desk():
    posts = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    pattern = re.compile('desk-([a-z0-9]+)')
    tz = pytz.timezone('US/Eastern')
    page = requests.get(TRUMP_SITE_URL, headers=headers, timeout=15)
    soup = BeautifulSoup(page.text, 'html.parser')

    for a in soup.find_all('article'):
        post = {}
        id_raw = a.find("div", {'class': 'title ftd-d'})['onclick']
        post['id'] =  pattern.search(id_raw)[1]

        ts_txt = a.find("div", {'class': 'date ftd-d'}).find('p').text
        ts = datetime.strptime(ts_txt, '%I:%M%p %B %d, %Y')
        utc_ts = tz.normalize(tz.localize(ts)).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        post['timestamp'] = utc_ts

        content = a.find("div", {'class': 'ftdli-main-content ftd-d'})
        post['text'] = re.sub(r'[\n]{2,}', r'\n', content.find('p').text)

        media_url = None
        if a['data-video'] == 'true':
            media_url = a['data-video-url']
        elif content.find('img'):
            media_url = content.find('img')['src']
        post['media_url'] = media_url
        posts.append(post)

    return posts

if __name__ == '__main__':
    posts = scrape_desk()
    json_posts = json.dumps(posts, indent=4)
    print(json_posts)

