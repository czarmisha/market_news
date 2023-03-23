import schedule
import time
from telegram import bot
from functions.indexes import main as indexes
from functions.earnings import main as earnings
from functions.week_earnings import main as week_earnings
from functions.earnings_moves import main as earnings_moves
from functions.conf_calls import main as conf_calls
from functions.ipo import main as ipo
from functions.lockups import main as lockups
from functions.indxch import main as indxch
from functions.calls_mbeat import main as calls_mbeat
from functions.calls_brief import main as calls_brief

import config.execution_time as cfg_time


def clean_file():
    """просто файл отслеживаться какой из 3х калов уже были отправлены во избежании повторений"""
    print('** cleaning file **')
    with open('tmp/r_calls_progress.txt', 'w') as file: 
        file.write('') # обнуляем файл

def main():
    # indexes()
    # ipo()
    # lockups()
    calls_brief()
    calls_brief()
    calls_brief()
    # earnings()
    # earnings_moves()
    # indxch()
    print('****** PROGRAM STARTING ******')
    tg_bot = bot.BotHandler()
    tg_bot.send_message('*Program starting*')

    # планируем запуск функции indexes каждый день в 05:00
    schedule.every().day.at("05:00").do(indexes)
    # планируем запуск функции week_earnings каждый понедельник в 05:30
    schedule.every().monday.at("05:30").do(week_earnings)
    # планируем запуск функции earnings_moves каждый день в 06:00
    schedule.every().day.at("06:00").do(earnings_moves)
    schedule.every().day.at("06:50").do(clean_file)
    # планируем запуск функции earnings каждый день в 07:00
    schedule.every().day.at("07:00").do(earnings)
    # планируем запуск функции conf_calls каждый день в 07:40
    schedule.every().day.at("07:40").do(conf_calls)
    # планируем запуск функции calls_mbeat каждый день в 08:05
    schedule.every().day.at("08:05").do(calls_mbeat)
    # планируем запуск функции ipo каждую неделю в 13:00
    schedule.every().friday.at("13:00").do(ipo)
    # планируем запуск функции lockups каждый день в 09:01
    schedule.every().day.at("09:01").do(lockups)
    # планируем запуск функции calls_mbeat каждый день в 09:05
    schedule.every().day.at("09:05").do(calls_mbeat)
    # планируем запуск функции indxch каждый день в 13:00
    schedule.every().day.at("13:00").do(indxch)

    #TODO quadruple triple etc every friday

    # research calls. 
    for check_time in cfg_time.research_calls_briefing:
        schedule.every().day.at(check_time).do(calls_brief)


    while True:
        # запускаем планировщик
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    try:
        #TODO можно создать отдельный потом для hot stocks 
        main()
    except KeyboardInterrupt:
        exit()