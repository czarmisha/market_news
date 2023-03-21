"""
Earnings (список тикеров, компаний, которые публикуют отчеты AMC в предыдущий день или BMO в текущий с актуальными изменениями цен и разбивкой на GapUp-ы и GapDown-ы; пример сообщения) 
Время публикации: 07:00 EST
Источник данных: не уверен, но вроде бы briefing.com (список отчетов) и takion (изменения цены)
Комментарий: нужно посмотреть, как реализован сбор информации для этого сообщения в текущей версии бота

"""
from utils.percent_change import get_percent_change
from telegram import bot

# TODO comment
def main():
    print('**** Earnings ****')
    output = 'Earnings:\n\n'

    with open('tmp/bmo_list.txt', 'r') as file:
        bmo = file.read().split(',')

    with open('tmp/amc_list.txt', 'r') as file:
        amc = file.read().split(',')
    
    per_change = get_percent_change(bmo + amc)

    for gap in per_change:
        output += f'_{gap}_: '
        for stock in per_change[gap]:
            output += f'*{stock}* {per_change[gap][stock]}; '
        output += '\n\n'
    
    output += '-----*AMC*-----'
    for ticker in amc:
        output += f'{ticker}\n'

    output += '\n-----*BMO*-----'
    for ticker in bmo:
        output += f'{ticker}\n'

    print('-- done earnings --')
    print(output)
    tg_bot = bot.BotHandler()
    tg_bot.send_post(output)
    tg_bot.send_message('-- done earnings --')