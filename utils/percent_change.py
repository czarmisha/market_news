import datetime
import yfinance as yf
import pandas as pd


def get_current_percent_change(tickers):
    """
    получает список тикеров, получает изменение относительно вчерашнего закрытия в % и возвращает объект вида 
    {'GapUp': {'CSIQ': '+15.9% (1M)', 'ONON': '+25.2% (100.0K)'}, 'GapDown': {'HUYA': '-15.1% (100.0K)', 'TME': '-9.1% (100.0K)'}}
    для вывода
    """
    data = {
        'GapUp': {},
        'GapDown': {} 
    }

    for ticker in tickers:
        if not ticker:
            continue
        start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d') # любой день подойдет. главное чтобы не был выходным поэтому взял 7дней назад
        end = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            # тянем историческую котировку за прошлую неделю(неважно) и берем самый последний день - это будет вчерашний торговый день. берем его закрытие
            close_pr = yf.Ticker(ticker).history(start=start, end=end).reset_index().iloc[-1].Close
            print('close_pr', close_pr)
            # тянем историческую котировку до текущего момента
            today_data = yf.Ticker(ticker).history(period='max', interval='1m', prepost=True).reset_index()
            # клоуз последней свечки - это самая последняя цена на акцию
            curr_pr_series = today_data.iloc[-1]
            # проверяем так же дату последней свечки с сегодняшней (чтобы не взять вчерашний афтермаркет)
            if not curr_pr_series.Datetime.date() == datetime.date.today():
                continue
            curr_pr = curr_pr_series.Close

            change = round((curr_pr / close_pr - 1) * 100, 1) # считаем %

            premarket_start_dt = datetime.datetime.now().replace(hour=4, minute=0, second=0, microsecond=0) # datetime начало премаркет сессии
            volume = today_data[today_data.Datetime >= pd.Timestamp(premarket_start_dt, tz='America/New_York')].Volume.sum() # считаем объем с 4 до сейчас

            volume_str = str(volume)
            if len(volume_str) < 7:
                volume_str = f'{round(volume / 1000, 2)}k'
            elif len(volume_str) >=7:
                volume_str = f'{round(volume / 1000000, 2)}M'

            # добавляем в наш объект и если изменение > 0, добавляем `+` в начало. и всем `%` в конец
            if change > 0:
                data['GapUp'][ticker] =  f'+{change}% ({volume_str})'
            else:
                data['GapDown'][ticker] =  f'{change}% ({volume_str})'

            #TODO do sorting
        except Exception:
            continue

    # сортировка
    data['GapUp'] = dict(sorted(data['GapUp'].items(), key=lambda x: x[1].split('%')[0], reverse=True))
    data['GapDown'] = dict(sorted(data['GapDown'].items(), key=lambda x: x[1].split('%')[0]))
    return data