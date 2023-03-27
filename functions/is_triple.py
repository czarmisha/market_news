"""
проверяет есть ли сегодня трипл или квадрупл
"""
import datetime
from telegram import bot


tg_bot = bot.BotHandler()


def is_triple_quadruple():
    print(' *** is triple quadruple ***')
    today = datetime.datetime.now()
    if today.weekday() == 4 and 15 <= today.day <= 21:
        ret_str = "*НАПОМИНАНИЕ*\n\nСегодня %s MOC Witching!"
        if today.month in [3, 6, 9 ,12]:
            tg_bot.send_post("*НАПОМИНАНИЕ*\n\nСегодня Quadruple MOC Witching!")
        else:
           tg_bot.send_post("*НАПОМИНАНИЕ*\n\nСегодня Triple MOC Witching!")
    
    print(' --- done is triple quadruple ---')
    
