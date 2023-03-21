"""
IPO, ожидаемые сегодня (список запланированных на сегодня IPO с их базовыми характеристиками)
Источник данных: iposcoop.com.
"""

import datetime

from config import urls
from utils.create_soup import create_soup


def normalize_mcap(mcap):
    """
    получаем Market Cap значение в виде `str`
    пример $24mil
    отбрасываем первый и 3 последних символа, если число > 1000 вконце добавим `B` (миллиарды) в остальных случаем `M`(миллионы)
    """
    print('** normalize mcap **')
    postfix = 'M'
    if not mcap:
        return 'N/A'
    mcap = float(mcap[1:-3])
    if mcap >= 1000:
        mcap = round(mcap / 1000, 2)
        postfix = 'B'
    
    return f"$ {mcap}{postfix}"

def get_ipo_info(url):
    """сбор информации по конкретному ipo url"""
    print('** get ipo info **')
    soup = create_soup(url) # получаем html страницу по url
    if not soup:
        print('!!! dont get a soup !!!')
        return None
    
    # ищем в html элемент table с классом 'ipo-table'
    table = soup.find('table', attrs={'class': 'ipo-table'})
    rows = table.find_all('tr') # все строки из таблицы
    data_info = {
        'Ticker' : rows[15].find_all('td')[1].get_text(), # просто берем текст из 16 колонки
        'Exchange' : rows[16].find_all('td')[1].get_text(), # просто берем текст из 17 колонки
        'Company': soup.find('h3', attrs={'class': 'section-title'}).span.get_text(), # в html ищем h3 с классом section-title
        'IPO amount (sh)': f"{rows[17].find_all('td')[1].get_text()}M",
        'Price range': rows[18].find_all('td')[1].get_text(),
        'IPO est. value': rows[19].find_all('td')[1].get_text(),
        'Mcap': normalize_mcap(rows[11].find_all('td')[1].get_text()), # просто берем текст из 12 колонки и нормализуем его
        'Industry': rows[2].find_all('td')[1].get_text()
    }
    return data_info

def main():
    #TODO holiday check
    print('**** IPO function starting ****')

    output = '*IPO, ожидаемые сегодня*\n\n'
    soup = create_soup(urls.url_ipo_calendar) # получаем html страницу по url
    if not soup:
        print('!!! dont get a soup !!!')
        return None
    
    # ищем в html элемент table с классом 'standard-table ipolist'
    calendar = soup.find('table', attrs={'class': 'standard-table ipolist'})
    if not calendar:
        print('!!! dont find a table !!!')
        return None
    
    # цикл по всем строкам таблицы
    for row in calendar.tbody.find_all('tr'):
        row_columns = row.find_all('td') # это все столбцы данной строки
        date_str = row_columns[7].get_text().split(' ')[0] # из 8й колонки берем строку с датой
        date = datetime.datetime.strptime(date_str, '%m/%d/%Y') # из строки делаем объект даты
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # сегодняшняя дата для сравнений
        #если дата IPO не совпадает с сегодняшней датой, переходим к следующей строке
        if not date == today:
            continue
        # row_columns[0].a['href'] ссылка в первой колонке на описание IPO
        info = get_ipo_info(row_columns[0].a['href'])# получаем информацию о конкретном IPO по его url
        if info:
            output += f"{info['Company']} ({info['Exchange']}: {info['Ticker']})\n" \
                    f"IPO amount (sh): {info['IPO amount (sh)']}, Price range: {info['Price range']}\n" \
                    f"IPO est. value: {info['IPO est. value']}, Mcap: {info['Mcap']}\n" \
                    f"Industry: {info['Industry']}\n\n" \
                    
    output += '#ipo #ipo-calendar'
    print('-- done ipo --')
    print(output) #TODO send post to telegram

    