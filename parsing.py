import requests
from bs4 import BeautifulSoup


URL = 'https://pikabu.ru/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) '
                         'Gecko/20100101 Firefox/77.0', 'accept': '*/*'}


class Parser:
    def __init__(self):
        self.url = URL
        self.headers = HEADERS

    def get_html(self, url):
        r = requests.get(url, headers=HEADERS)
        return r

    def get_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        item = str(soup.find_all('article', class_='story'))
        soup2 = BeautifulSoup(item, 'html.parser')
        story = soup.find_all('div', class_='story__content story__typography')
        story = [i.text for i in story]
        story_name = soup.find_all('header', 'story__header')
        story_name = [i.text for i in story_name]
        return [story, story_name]

    def parse(self):
        html = self.get_html(self.url)
        if html.status_code == 200:
            data = self.get_content(html.text)
            return data
        else:
            print('!ERROR!')
