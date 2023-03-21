"""
Описание:
Данные по изменению фьючерсов на америкканские фондовые индексы,
основных фондовых индексов Азии и Европы,
а также фьючерсов на сырье плюс календарь ожидаемых данных и событий

Время публикации: 05:00 EST
Источник данных: MarketWatch/Finviz.com

"""
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from utils.create_soup import create_soup 
from config import urls
from telegram import bot


def marketwatch_parse(url, name):
    """парсинг сайта marketwatch для получения изменения по инструментам"""

    print('** parsing marketwatch **')
    # получаем читабельный html с url в виде объекта BeautifulSoup
    soup = create_soup(url)
    if not soup:
        print('!! error !!\n can not create soup')
        return None
    
    # тут облигации на сайте подаются не в виде %го изменения а в виде изменения в поинтах
    # поэтому классы элементов разные
    class_to_find = 'change--percent--q'
    if name == 'US 10y Bonds':
        class_to_find = 'change--point--q'

    # ищем элементы в html в которых хранятся значения изменения инструмента
    span = soup.find('span', attrs={'class': class_to_find})
    if not span:
        print('!! error !!\ndo not find span while parsing', name)
        return None

    # получаем значение из элемента
    change_val = str(span.string)

    return change_val


def finviz_parse():
    """парсинг сайта finviz для получения календаря экономических событий"""

    print('** parsing finviz **')
    # получаем читабельный html с url в виде объекта BeautifulSoup
    soup = create_soup(urls.url_finviz)

    calendar_list = ''
    # ищем таблицу в которой календарь событий на сайте
    table = soup.find('table', attrs={'class': 'calendar'})
    if not table:
        print('!! error !!\ndo not find calendar table')
        return ''
    # пробегаемся по каждый строке таблицы
    for row in table.find_all('tr', attrs={
                            'class' : "table-light-row-cp",
                            'onclick' : "window.location='calendar.ashx'"
                            }):
        cols = row.find_all('td') # берем все колонки каждой строки
        if len(cols) == 3:
            return ''
        calendar_list += f'{cols[1].text} {cols[3].text}\n' # cols[1].text - время, cols[3].text - название события
    return calendar_list


def main():
    print('**** Indexes parse starting ****')
    output = '' # строка куда мы будет клеить текст и в итоге тут получится вся строка которую надо отправить в канал

    #  indexes_data словарь, где ключи Название интрумента и аргументы ссылки из utils.urls
    indexes_data = {
        'S&P' : urls.url_marketwatch_spx_futures,
        'NASDAQ' : urls.url_marketwatch_nq_futures,
        'Crude Oil WTI' : urls.url_marketwatch_crude_oil,
        'Gold' : urls.url_marketwatch_gold,
        'US 10y Bonds' : urls.url_marketwatch_bond_yield,
        'FTSE' : urls.url_marketwatch_uk_futures,
        'DAX' : urls.url_marketwatch_germany_futures,
        'Shanghai Comp. (SSEC)' : urls.url_marketwatch_shanghai_futures,
        'NIKKEI' : urls.url_marketwatch_japan_futures,
        'VIX' : urls.url_marketwatch_spx_vix_futures,
    }

    for index in indexes_data:
        # получаем изменение по инструменту
        percent_ch = marketwatch_parse(indexes_data[index], index)
        if not percent_ch:
            percent_ch = 'N/A'
        else:
            percent_ch = f"+{percent_ch}" if '-' not in percent_ch else percent_ch # добавим + в начало строки если в ней нет минуса изначально

        output += f"{index} {percent_ch} \n"

    calendar = finviz_parse()
    output += f'\n{calendar}'

    # добавляем теги в конце
    if calendar:
        output += '\n\n#futures'
        output += '\n#fincalendar'
    else:
        output += '\n#futures'

    print('-- done index parsing --')
    print(output)
    tg_bot = bot.BotHandler()
    tg_bot.send_post(output)
    tg_bot.send_message('-- done index parsing --')
