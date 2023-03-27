"""
Conference Calls (список пресс-конференций, посвященных опубликованным квартальным отчетам; пример сообщения)
Время публикации: 07:40 EST
Источник данных: briefing
Комментарий: публиковать два сообщения - одно, так как сейчас, другое - список акций в алфавитном порядке с временем пресс-конференции.

"""
import datetime
from config import urls
from utils.create_soup import create_soup


def main():
    print('**** Conference calls ****')
    output = 'Conference Calls:\n\n'
    bmo = []
    url = urls.url_tickerEarn

    try:
        with open('tmp/bmo_list.txt', 'r') as file: # берем с файла список тикеров с отчетами bmo
            bmo = file.read().split(',')
            
    except FileNotFoundError:
        print('!! file not found !!')
        return
    
    if not bmo:
        return
    
    data = {}
    for ticker in bmo:
        try:
            soup = create_soup(url, {'ticker': ticker.strip(), 'page': 'EARNINGS', 'range': 60})
        except Exception:
            print('!!! err while getting soup !!!', ticker)
            continue
        
        for div in soup.find_all('div', attrs={"class": "margin-left"}):
            if 'Earnings Conference Call:' in str(div):
                print(div.text)
                cc_split = div.text.split(' on ')
                row_cc_time = cc_split[1].split()
                cc_date = datetime.datetime.strptime(f'{row_cc_time[0]}-{row_cc_time[1]}-{row_cc_time[2]}', '%b-%d-%Y')

                cc_time = row_cc_time[-1]
                if not cc_date == datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    continue

                if not cc_date in data:
                    data[cc_date] = [ticker]
                else:
                    data[cc_date].append(ticker)

    data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    for time in data:
        if not data[time]:
            continue

        tmp = f'{time}: {", ".join(data[time])}\n'
        output += tmp

    print('-- done conference calls --')

