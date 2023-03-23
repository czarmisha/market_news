"""
Research Calls (Briefing) (upgrades, downgrades, target changes и initiating, которые известны на текущее время;)
"""
import datetime

from utils.briefing import BriefingParser
from config import urls
from telegram import bot

# TODO comment
def main():
    """
    ищем research calls на briefing
    """
    print('**** Research calls ****')
    # это статус. так как с брифинга берем 3 разных research calls.
    # если call_1=True значит его уже нашли, отправили в канал и записали в файл tmp/r_calls_progress.txt на случай если программа перезапустилась и все переменные обнуляться
    call_1, call_2, call_3 = False, False, False
    call_number = None # номер кола I II или III

    with open('tmp/r_calls_progress.txt') as file: # читаем с файла прогресс за сегодня
        progress = file.read().split(',')

    if not call_1 and not 'call_1' in progress: # если мы еще не нашли и не отправили 1й research call
        call_1 = True
        call_number = ''
    elif not call_2 and not 'call_2' in progress: # если мы еще не нашли и не отправили 2й research call
        call_1 = True
        call_2 = True
        call_number = 'II'
    elif not call_3 and not 'call_3' in progress: # если мы еще не нашли и не отправили 3й research call
        call_2 = True
        call_3 = True
        call_number = 'III'
    
    if call_number is None:
        print('!!! error call_number !!!')
        return 

    output = f'Research Calls {call_number}'.strip() # генерируем заголовок типа Research Calls II
    
    parser = BriefingParser(urls.url_r_calls) # переходим на страницу с колами
    soup = parser.soup # получаем html
    rows = soup.find_all('tr', class_='inplayRow') # получаем все строки
    today = datetime.datetime.now().strftime('%d-%b-%y')

    for row in rows:
        row_date = row.find('span', attrs={'id': 'ArticleTime'}).text.split(' ')[0] # дата(публикации новости) в конкретной строке
        if not row_date == today: # если она опубликована не сегодня то она нам не интересна
            return
        
        row_title = row.find('td', attrs={'class': 'articleColumn'}).find('div', attrs={'class': 'lip-title'}).text # заголовок новости
        if not row_title == output: # если заголовок не равен нашему заголовку например Research Calls II == Research Calls II
            continue
        output += f'*{output}*\n'

        row_text = row.find('td', attrs={'class': 'articleColumn'}).find('div', attrs={'class': 'lip-article'}).find('ul') # весь текст из тела новости лежит в таких элементах
        tmp = ''
        for li in row_text.find_all('li'): # идем по всем элементам li
            if li.text.split(':')[0] in ['Upgrades', 'Downgrades', 'Others']: # если вначале текста есть слова 'Upgrades', 'Downgrades', 'Others'
                tmp += f"\n_{li.text.split(':')[0]}_\n" # тогда записываем как подзаголовок типа Upgrades:
                continue
            
            tmp += f"{li.text.split(':')[0]}\n" # записываем все что после заголовка в следующих строках
        
        with open('tmp/r_calls_progress.txt', 'a') as file: # записываем прогресс что текущий кол мы нашли
            to_write = 'call_1'
            if call_number == 'II':
                to_write = 'call_2'
            elif call_number == 'III':
                to_write = 'call_3'
            file.write(to_write + ',')
        
        output += tmp + '\n'
        break

    print(f'-- done research calls {call_number} (briefing) --')
    print(output)
    tg_bot = bot.BotHandler()
    tg_bot.send_post(output)
    tg_bot.send_message(f'-- done research calls {call_number} (briefing) --')

