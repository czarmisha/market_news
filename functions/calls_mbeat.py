import datetime
import pandas as pd
import os

from utils.create_soup import create_soup
from config import credentials as cfg
from telegram import bot


tg_bot = bot.BotHandler()

def main(first=True):
    print('**** Research calls markerbeat ****   first:', first)
    data = []
    soup = create_soup(cfg.URL_MARKET_BEAT)
    if not soup:
        return None

    table = soup.find('table', class_='scroll-table').find('tbody')
    if not table:
        return
    
    rows = table.find_all('tr')
    if not rows or len(rows) <=0:
        return
    

    for row in rows:
        row_columns = row.find_all('td')
        stock_data = {
            'Ticker': '',
            'Action': '',
            'Brokerage': '',
            'Price Target': '',
            'Rating': '',
        }
        try:
            stock_data['Ticker'] = row_columns[0].find('div', class_='ticker-area').get_text(strip=True)
            stock_data['Action'] = row_columns[1].get_text(strip=True).replace('by', '')
            stock_data['Brokerage'] = row_columns[2].find_all('a')[0].get_text(strip=True)
            stock_data['Price Target'] = row_columns[5].get_text(strip=True)
            stock_data['Rating'] = row_columns[6].get_text(strip=True)
        except AttributeError:
            pass

        data.append(stock_data)

    file_path = 'tmp/' + datetime.datetime.now().strftime('%Y-%m-%d_%H') + 'AM.xlsx'
    df = pd.DataFrame(data)

    # sort by action, in this order:
    # 'Initiated', 'Target Raised', 'Upgraded', 'Target Lowered', 'Downgraded'
    df['Action'] = pd.Categorical(
        df['Action'], ['Initiated ', 'Target Raised ', 'Upgraded ', 'Target Set ', 'Target Lowered ',
                    'Downgraded ', 'Reiterated '], ordered=True
    )
    df.sort_values('Action', inplace=True)
    df.to_excel(file_path, index=False, encoding='utf-8')

    if not first:
        date_8am = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime('%Y-%m-%d_%H')
        path_to_prev_file = 'tmp/' + date_8am + 'AM.xlsx'
        if os.path.isfile(path_to_prev_file):
            df2 = pd.read_excel(path_to_prev_file)
            df = pd.merge(df, df2).drop_duplicates()
            df['Action'] = pd.Categorical(
            df['Action'], ['Initiated ', 'Target Raised ', 'Upgraded ', 'Target Set ', 'Target Lowered ',
                        'Downgraded ', 'Reiterated '], ordered=True
            )
            df.sort_values('Action', inplace=True)
            file_path = 'tmp/' + datetime.datetime.now().strftime('%Y-%m-%d') + '.xlsx'
            df.to_excel(file_path, index=False, encoding='utf-8')


    caption_date = datetime.datetime.now().strftime('%B %d, %Y // %H')
    caption = f'Ratings and Targets on {caption_date.split("//")[0]} at {caption_date.split("//")[1]}:00 AM'
    tg_bot.send_file(file_path, caption)

    print('-- done research calls mbeat --')
