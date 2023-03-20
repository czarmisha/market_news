import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# утилита для получения заголовков 'User-Agent' разных браузеров.
# Имитируем запрос на сайт по ссылке как будто через браузер
ua = UserAgent()

def create_soup(url, params=None):
    """
    
    """
    res = requests.get(url, headers={'User-Agent': ua.chrome}, params=params) # запрос по url.
    # всегда при удачном запросе в ответе будет 200й статус
    if not res.status_code == 200:
        print('!!! status code is not OK !!!')
        return None
    # BeautifulSoup парсит html документ в читабельный вид и позволяет гибко с ним работать
    # res.content то что мы получили от сервера, в нашем случае строку с html кодом страницы по url
    return BeautifulSoup(res.content, 'html.parser')