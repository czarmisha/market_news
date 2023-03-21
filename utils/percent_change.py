import yfinance as yf
import datetime


def get_current_percent_change(tickers):
    """
    получает список тикеров, получает изменение относительно вчерашнего закрытия в % и возвращает объект вида 
    {'GapUp': {'CSIQ': '+15.9%', 'ONON': '+25.2%'}, 'GapDown': {'HUYA': '-15.1%', 'TME': '-9.1%'}}
    для вывода
    """
    data = {
        'GapUp': {},
        'GapDown': {} 
    }

    for ticker in tickers:
        if not ticker:
            continue
        start = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d') # любой день подойдет. главное чтобы не был выходным поэтому взял 7дней назад
        end = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            # тянем историческую котировку за прошлую неделю(неважно) и берем самый последний день - это будет вчерашний торговый день. берем его закрытие
            close_pr = yf.Ticker(ticker).history(start='2023-03-13', end='2023-03-21').reset_index().tail(1).iloc[0].Close
            # тянем историческую котировку за сегодня с 04:00 до текущего момента и берем клоуз последней свечки - это самая последняя цена на акцию
            curr_pr = yf.Ticker(ticker).history(period='1d', interval='1m', prepost=True).reset_index().tail(1).iloc[0].Close
            change = round((curr_pr / close_pr - 1) * 100, 1) # считаем %
            
            # добавляем в наш объект и если изменение > 0, добавляем `+` в начало. и всем `%` в конец
            if change >= 0:
                data['GapUp'][ticker] =  f'+{change}%'
            else:
                data['GapDown'][ticker] =  f'{change}%'

        except Exception:
            continue
    
    return data