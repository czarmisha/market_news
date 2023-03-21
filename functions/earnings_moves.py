"""
Early earnings moves (GapUp-ы и GapDown-ы по акциям, которые опубликовали отчеты AMC в предыдущий день или публикуют BMO в текущий день; пример сообщения)
Время публикации: 06:00 EST
Источник данных: не уверен, но вроде бы briefing.com (список отчетов) и takion (изменения цены)
Комментарий: нужно посмотреть, как реализован сбор информации для этого сообщения в текущей версии бота

"""
from config import urls
from utils.briefing import BriefingParser
from utils.percent_change import get_percent_change


def get_tickers(soup, table_id):
    tickers = []

    table = soup.find('table', attrs={'id': table_id})
    if not table:
        print('!! earnings table not found !!', table_id)
        return []
    
    rows = table.find_all('tbody')
    if not len(rows) or not rows:
        print('!! earnings table is empty !!', table_id)
        return []

    for row in rows:
        row_columns = row.find_all('td')
        tickers.append(row_columns[5].text)

    return tickers
# TODO comment
def main():
    print('**** Earning movers ****')
    output = 'Early earnings moves:\n\n'
    bmo, amc = [], []

    parser = BriefingParser(urls.url_earn_today)
    soup = parser.soup
    bmo = get_tickers(soup, 'yui-gen7')
    with open('tmp/bmo_list.txt', 'w') as file:
        file.write(','.join(bmo))

    parser.set_new_url(urls.url_earn_yesterday)
    soup = parser.soup
    amc = get_tickers(soup, 'yui-gen9')
    with open('tmp/amc_list.txt', 'w') as file:
        file.write(','.join(amc))
    
    per_change = get_percent_change(bmo + amc)

    for gap in per_change:
        output += f'_{gap}_: '
        for stock in per_change[gap]:
            output += f'*{stock}* {per_change[gap][stock]}; '
        output = '\n\n'

    print(output) # TODO send to telegram


