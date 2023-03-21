import yfinance as yf
import datetime


def get_current_percent_change(tickers):
    data = {
        'GapUp': {},
        'GapDown': {} 
    }

    for ticker in tickers:
        start = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        end = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            close_pr = yf.Ticker(ticker).history(start='2023-03-13', end='2023-03-21').reset_index().tail(1).iloc[0].Close
            curr_pr = yf.Ticker(ticker).history(period='1d', interval='1m', prepost=True).reset_index().tail(1).iloc[0].Close
            change = round((curr_pr / close_pr - 1) * 100, 1)
            
            if change >= 0:
                data['GapUp'][ticker] =  f'+{change}%'
            else:
                data['GapDown'][ticker] =  f'{change}%'

        except Exception:
            continue
    
    return data