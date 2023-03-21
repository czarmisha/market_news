"""
Research Calls (Briefing) (upgrades, downgrades, target changes и initiating, которые известны на текущее время;)
"""
import datetime

from utils.briefing import BriefingParser
from config import urls

# TODO comment
def main():
    print('**** Research calls ****')
    call_1, call_2, call_3 = False, False, False
    call_number = None

    with open('tmp/r_calls_progress.txt') as file:
        progress = file.read().split(',')

    if not call_1 and not 'call_1' in progress:
        call_1 = True
        call_number = ''
    elif not call_2 and not 'call_2' in progress:
        call_1 = True
        call_2 = True
        call_number = 'II'
    elif not call_3 and not 'call_3' in progress:
        call_2 = True
        call_3 = True
        call_number = 'III'
    
    if call_number is None:
        print('!!! error call_number !!!')
        return 

    output = f'*Research Calls {call_number}*'.strip() + '\n\n'
    
    parser = BriefingParser(urls.url_r_calls)
    soup = parser.soup
    rows = soup.find_all('tr', class_='inplayRow')
    today = datetime.datetime.now().strftime('%d-%b-%y')

    for row in rows:
        row_date = row.find('span', attrs={'id': 'ArticleTime'}).text.split(' ')[0]
        if not row_date == today:
            return
        
        row_title = row.find('td', attrs={'class': 'articleColumn'}).find('div', attrs={'class': 'lip-title'}).text
        if not row_title == output:
            continue
        output += '\n'

        row_text = row.find('td', attrs={'class': 'articleColumn'}).find('div', attrs={'class': 'lip-article'}).find('ul')
        tmp = ''
        for li in row_text.find_all('li'):
            if li.text.split(':')[0] in ['Upgrades', 'Downgrades', 'Others']:
                tmp += f"\n_{li.text.split(':')[0]}_\n"
                continue
            
            tmp += f"{li.text.split(':')[0]}\n"
        
        with open('tmp/r_calls_progress.txt', 'a') as file:
            to_write = 'call_1'
            if call_number == 'II':
                to_write = 'call_2'
            elif call_number == 'III':
                to_write = 'call_3'

            file.write(to_write + ',')
        
        output += tmp + '\n'
        break

    print(output) # TODO send to telegram

