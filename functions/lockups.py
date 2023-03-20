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
    date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
    next_date = date + datetime.timedelta(days=1)
    start = date.strftime('%Y-%m-%d')
    end = next_date.strftime('%Y-%m-%d')
    history = yf.Ticker(ticker).history(start=start, end=end, interval='1d')
    if history.empty:
        return '-'
    open_price = history[history == start].Open[0]
    return open_price


def get_mcap(ticker):
    """берем market cap по тикеру из finviz.com"""
    print('** get_mcap **')
    soup = create_soup(urls.url_finviz_ticker, {'t': ticker})
    if not soup:
        print('!! can\'t get a soup !!')
        return '-'
    
    mcap_td = soup.find('td', string='Market Cap')
    if not mcap_td:
        print('!! can\'t find market cap column !!')
        return '-'
    
    mcap = mcap_td.next.next.text
    return mcap


def get_info(columns):
    print('** get_info **')
    try:
        ticker = columns[0].find('div', attrs={'class': 'ticker-area'}).text
    except AttributeError:
        print('!! can\'t find a ticker !!')
        return None
    data = {
        'Ticker': ticker,
        'Mcap': get_mcap(ticker),
        'IPO price': columns[4].text,
        'Open price': get_open_price(ticker, columns[6].text),
    }
    return data


def create_output_str():
    output = '*Календарь завершения локап-периодов на следующую неделю:*\n(ticker / mcap / IPO price / open price)\n\n'
    for day, lockups in lockup_data.items():
        tmp_str = f'*{day}*:\n'
        if len(lockups) == 0:
            tmp_str += 'No lockups\n\n'
            output += tmp_str
            continue

        for lockup in lockups:
            tmp_str += f"{lockup['Ticker']} / {lockup['Mcap']} / {lockup['IPO price']} / {lockup['Open price']}\n\n"

        output += tmp_str

    return output


def get_next_week_day(i):
    next_week_day = now + datetime.timedelta(days=7-week_day+i)
    return next_week_day.strftime('%m/%d/%Y')

week = [get_next_week_day(i) for i in range(5)]
lockup_data = {datetime.datetime.strptime(day, '%m/%d/%Y').strftime('%A'): [] for day in week}


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
        row_columns = row.find_all('td')
        row_date = row_columns[2].text
        row_date_dt = datetime.datetime.strptime(row_date, '%m/%d/%Y')
        row_date = row_date_dt.strftime('%m/%d/%Y')
        if not row_date in week:
            continue

        info = get_info(row_columns)
        if not info:
            continue
        lockup_week_day = row_date_dt.strftime('%A')
        lockup_data[lockup_week_day].append(info)

    output = create_output_str()
    output += '#lockups'
    print('-- done lockups --')
    print(output) #TODO send to telegram
