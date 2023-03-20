"""
Календарь завершения локап-периодов (информация по завершающихся на следующей неделе локап-периодах)
"""
import datetime
import yfinance as yf
import datetime

from utils.create_soup import create_soup
from config import urls


now = datetime.datetime.now()
week_day = now.weekday()

def get_open_price(ticker, date_str):
    """скачиваем историческую дату на момент открытия торгов и берем цену открытия"""
    print('** get_open_price **')
    date = datetime.datetime.strptime(date_str, '%m/%d/%Y') # конвертируем строку даты начала торгов в дату
    next_date = date + datetime.timedelta(days=1) # дата начала торгов + 1 день. Это для поиска yfinance.
    start = date.strftime('%Y-%m-%d') # дата начала торгов переводим в строку под формат yfinance
    end = next_date.strftime('%Y-%m-%d')
    history = yf.Ticker(ticker).history(start=start, end=end, interval='1d').reset_index() # получаем данные на 1й день торгов
    if history.empty:
        return '-'
    open_price = history[history.Date == start].Open[0] # получаем цену открытия за 1й день торгов
    return f'${open_price}' if open_price else '-' # если цена открытия есть то добавляем к ней знак `$`, если ее нет то возвращаем знак `-`


def get_mcap(ticker):
    """берем market cap по тикеру из finviz.com"""
    print('** get_mcap **')
    soup = create_soup(urls.url_finviz_ticker, {'t': ticker}) # берем html с url
    if not soup:
        print('!! can\'t get a soup !!')
        return '-'
    
    mcap_td = soup.find('td', string='Market Cap') # ищем элемент с тегом <td> и строкой внутри 'Market Cap' (он один на сайте)
    if not mcap_td:
        print('!! can\'t find market cap column !!')
        return '-'
    
    mcap = mcap_td.next.next.text # берем соседний элемент справа и его значение внутри (значение 'Market Cap')
    return mcap


def get_info(columns):
    """собираем нужные данные о конкретном локапе"""
    print('** get_info **')
    try:
        ticker = columns[0].find('div', attrs={'class': 'ticker-area'}).text # ищем <div class='ticker-area'> в первой колонке строки - это тикер 
    except AttributeError:
        print('!! can\'t find a ticker !!')
        return None
    data = {
        'Ticker': ticker,
        'Mcap': get_mcap(ticker), # получаем market cap по тикеру
        'IPO price': columns[4].text, # в 4й колонке лежит IPO Price
        'Open price': get_open_price(ticker, columns[6].text),  # получаем цену открытия по тикеру и дате начало торгов
    }
    return data


def create_output_str():
    output = '*Календарь завершения локап-периодов на следующую неделю:*\n(ticker / mcap / IPO price / open price)\n\n'
    for day, lockups in lockup_data.items(): # бегаем по всем дням недели. 
        tmp_str = f'*{day}*:\n' # Monday:
        if len(lockups) == 0: # если за этот день нет локапов 
            tmp_str += 'No lockups\n\n'
            output += tmp_str
            continue

        for lockup in lockups:
            tmp_str += f"{lockup['Ticker']} / {lockup['Mcap']} / {lockup['IPO price']} / {lockup['Open price']}\n\n" # ticker / mcap / ipo price / open price

        output += tmp_str

    return output


def get_next_week_day(i):
    next_week_day = now + datetime.timedelta(days=7-week_day+i)
    return next_week_day.strftime('%m/%d/%Y')

week = [get_next_week_day(i) for i in range(5)] # получаем массив из строк с датами следующей недели
lockup_data = {datetime.datetime.strptime(day, '%m/%d/%Y').strftime('%A'): [] for day in week} # получаем объект вида {'Monday': [], 'Tuesday': [], ...}


def main():
    #TODO holiday check
    print('**** lockups function starting ****')

    soup = create_soup(urls.url_marketbeat_lockups) # получаем html страницу по url
    if not soup:
        print('!!! dont get a soup !!!')
        return None
    
    # ищем в html элемент table
    table = soup.find('table')
    if not table:
        print('!!! dont find a table !!!')
        return None
    
    # цикл по всем строкам таблицы
    for row in table.tbody.find_all('tr'):
        row_columns = row.find_all('td') # все колонки конкретной строки

        # этот блок кода нужен, потому что на сайте формат данные 3/2/2022, а у нас в массиве дат следующей недели 03/02/2022
        row_date = row_columns[2].text # дата локапа в виде строки
        row_date_dt = datetime.datetime.strptime(row_date, '%m/%d/%Y') # дата локапа: из строки в дату
        row_date = row_date_dt.strftime('%m/%d/%Y') # дата локапа в виде строки

        if not row_date in week: # если дата локапа не на следующей неделе
            continue

        info = get_info(row_columns) # получаем нужные данные по локапу
        if not info:
            continue
        lockup_week_day = row_date_dt.strftime('%A') # получаем название дня недели
        lockup_data[lockup_week_day].append(info) # добавляем локап ко всем локапам по дню недели

    output = create_output_str()
    output += '#lockups'
    print('-- done lockups --')
    print(output) #TODO send to telegram
