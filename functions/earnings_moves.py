"""
Early earnings moves (GapUp-ы и GapDown-ы по акциям, которые опубликовали отчеты AMC в предыдущий день или публикуют BMO в текущий день; пример сообщения)
Время публикации: 06:00 EST
Источник данных: не уверен, но вроде бы briefing.com (список отчетов) и takion (изменения цены)
Комментарий: нужно посмотреть, как реализован сбор информации для этого сообщения в текущей версии бота

"""
from config import urls
from utils.briefing import BriefingParser
from utils.percent_change import get_percent_change
from telegram import bot


def get_tickers(soup, table_id):
    """
    ищет все тикеры в таблице
    """
    tickers = []

    table = soup.find('table', attrs={'id': table_id}) # ищем таблицу с конкретным id 
    if not table:
        print('!! earnings table not found !!', table_id)
        return []
    
    rows = table.find_all('tbody') # это все строки таблицы с отчетами
    if not len(rows) or not rows:
        print('!! earnings table is empty !!', table_id)
        return []

    # идем по каждой строке(по каждому отчету)
    for row in rows:
        row_columns = row.find_all('td') # все колонки конкретной строки/отчета
        tickers.append(row_columns[5].text) # добавляем в общий список акций тикер из текущей строки(он в 6 колонке)

    return tickers


def main():
    """
    функция ищет все отчеты bmo amc, записывает в файлы списки тикеров
    и печатает в разрезе гепов вывод
    """
    print('**** Earning movers ****')
    output = 'Early earnings moves:\n\n'
    bmo, amc = [], []

    parser = BriefingParser(urls.url_earn_today) # открываем страницу c отчетами за сегодня
    soup = parser.soup # получаем html
    bmo = get_tickers(soup, 'yui-gen7') # ищем  все bmo тикеры (они всегда в таблице с id 'yui-gen7')
    with open('tmp/bmo_list.txt', 'w') as file: # записываем в файл
        file.write(','.join(bmo))

    parser.set_new_url(urls.url_earn_yesterday) # открываем  новую страницу со вчерашними отчетами
    soup = parser.soup # получаем html
    amc = get_tickers(soup, 'yui-gen9')  # ищем  все amc тикеры (они всегда в таблице с id 'yui-gen9')
    with open('tmp/amc_list.txt', 'w') as file: # записываем в файл
        file.write(','.join(amc))
    
    # для всех тикеров получаем объект вида {'GapUp': {'CSIQ': '+15.9%', 'ONON': '+25.2%'}, 'GapDown': {'HUYA': '-15.1%', 'TME': '-9.1%'}}
    per_change = get_percent_change(bmo + amc)

    #красиво печатаем все
    for gap in per_change:
        output += f'_{gap}_: '
        for stock in per_change[gap]:
            output += f'*{stock}* {per_change[gap][stock]}; '
        output = '\n\n'

    print('-- done earning moves --')
    print(output)
    tg_bot = bot.BotHandler()
    tg_bot.send_post(output)
    tg_bot.send_message('-- done earning moves --')

