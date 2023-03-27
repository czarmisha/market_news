"""
Earnings (список тикеров, компаний, которые публикуют отчеты AMC в предыдущий день или BMO в текущий с актуальными изменениями цен и разбивкой на GapUp-ы и GapDown-ы; пример сообщения) 
Время публикации: 07:00 EST
Источник данных: не уверен, но вроде бы briefing.com (список отчетов) и takion (изменения цены)
Комментарий: нужно посмотреть, как реализован сбор информации для этого сообщения в текущей версии бота

"""
from utils.percent_change import get_current_percent_change
from telegram import bot


def main():
    print('**** Earnings ****')
    output = 'Earnings:\n\n'
    try:
        with open('tmp/bmo_list.txt', 'r') as file: # берем с файла список тикеров с отчетами bmo
            bmo = file.read().split(',')

        with open('tmp/amc_list.txt', 'r') as file: # берем с файла список тикеров с отчетами amc
            amc = file.read().split(',')
            
    except FileNotFoundError:
        print('!! file not found !!')
        return
    
    # для всех тикеров получаем объект вида {'GapUp': {'CSIQ': '+15.9%', 'ONON': '+25.2%'}, 'GapDown': {'HUYA': '-15.1%', 'TME': '-9.1%'}}
    per_change = get_current_percent_change(bmo + amc)

    #красиво печатаем все
    for gap in per_change:
        output += f'_{gap}_: '
        for stock in per_change[gap]:
            output += f'*{stock}* {per_change[gap][stock]}; '
        output += '\n\n'
    
    if amc:
        output += '-----*AMC*-----\n'
    for ticker in amc:
        output += f'{ticker}\n'

    if bmo:
        output += '\n-----*BMO*-----\n'
    for ticker in bmo:
        output += f'{ticker}\n'

    print('-- done earnings --')
    print(output)
    tg_bot = bot.BotHandler()
    tg_bot.send_post(output)
    tg_bot.send_message('-- done earnings --')