"""
Изменения в индексах (данные по запланированных изменениях индексов; пример сообщения)
Время публикации: 13:00 EST
Источник данных: не уверен, но вроде бы  briefing.
"""
"""
год брать из даты
дата в новости должна быть больше сегодняшней. 
если дата новости 22год декабрь, а в новости дата январь 5, то нужно проверить месяц в новости если меньше то год + 1
формат даты в основном  Thursday, December 22  February 6

искать совпадения во всем тексте новости по:
effective prior to the opening of trading on
prior to the open on
post close on
"""
import datetime
from telegram import bot
from utils.briefing import BriefingParser
import config.credentials as cfg
import config.urls as urls

tg_bot = bot.BotHandler()

month = [datetime.datetime.strptime(f'2022-{i}-1', '%Y-%m-%d').strftime('%B') for i in range(1, 13)]
mon = [datetime.datetime.strptime(f'2022-{i}-1', '%Y-%m-%d').strftime('%b') for i in range(1, 13)]
week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

#TODO нужно проверять года если дата новости 22год декабрь, а в новости дата январь 5, то нужно проверить месяц в новости если меньше то год + 1
def main():
    now = datetime.datetime.now() # datetime
    today = now.strftime("%Y-%m-%d") 
    today = datetime.datetime.strptime(today, "%Y-%m-%d") 
    week_now = now.strftime("%A")
    year_now = now.strftime("%Y")

    parser = BriefingParser(urls.url_indxch)
    soup = parser.soup

    posts = soup.find_all('div', attrs={"class": "lip-briefing-wrap"}) # все контейнеры с новостью
    posts_dt = soup.find_all('div', attrs={"class": "yui-dt-col-ArticleDT yui-dt-col-0 yui-dt-liner"}) # все контейнеры с датой публикации новости
    counter = 5 # походу берем 5 последних публикаций новостей?

    while counter >= 0:
        data_in_text = None
        week_day = None

        post_date = posts_dt[counter].find('span', attrs={"class": "lip-ArticleDT"}).text
        post_date = post_date.split(' ')
        post_date = datetime.datetime.strptime(post_date[0], "%d-%b-%y") # дата публикации новости 15-Mar-23

        body = posts[counter] # новость
        post_title = body.find('div', attrs={"class": "lip-title"}).text + ' ' # заголовок новости
        post_text = body.find('div',
                                 attrs={"class": "lip-article custom-style-big-width custom-style-hide"}) # текст новости

        full_text = post_title + '/// ' + post_text.text
        full_text = full_text.replace(',', '')
        full_text = full_text.replace('.', '')
        full_text = full_text.replace('\xa0', ' ') # \xa0 можно сказать это пробел тот же самый
        full_text = full_text.replace('  ', ' ')
        full_text = full_text.replace('   ', ' ')

        words = full_text.split(" ") # весь текст разбил на слова ##########
        for i in range(len(words)):
            if data_in_text is None: # 1й проход None 
                for m in range(len(month)):
                    if words[i] == month[m]: # если среди слов встретили месяц    тут формат January 5
                        try:
                            day_x = int(words[i + 1]) # по идее после месяца идет число даты
                        except ValueError:
                            continue
                        
                        if m + 1 > post_date.month:
                            year_now = f'{int(year_now) + 1}'
                        data_in_text = words[i] + "//" + str(day_x) + '//' + year_now # месяц//число//текущий год строка
                        data_in_text_dt = datetime.datetime.strptime(data_in_text, "%B//%d//%Y") # месяц//число//текущий год ДАТА
                        prev_data_in_text_dt = data_in_text_dt - datetime.timedelta(days=1) # предыдущий день  дата ???
                        break

                    elif words[i] == mon[m]: # тут формат Jan 5
                        try:
                            day_x = int(words[i + 1]) # по идее после месяца идет число даты
                        except ValueError:
                            continue

                        if m + 1 > post_date.month:
                            year_now = f'{int(year_now) + 1}'
                        data_in_text = words[i] + "//" + str(day_x) + '//' + year_now  # месяц укороченный//число//текущий год строка
                        data_in_text_dt = datetime.datetime.strptime(data_in_text, "%b//%d//%Y") # месяц укороченный//число//текущий год ДАТА
                        prev_data_in_text_dt = data_in_text_dt - datetime.timedelta(days=1) # предыдущий день  дата ???
                        break
            else:
                break

        for i in range(len(words)):
            if week_day is None: # первый раз None
                for d in week:
                    if words[i] == d:
                        week_day = words[i]
            else:
                break

        try:
            data_in_text = data_in_text.replace('//', ' ')
        except Exception:
            pass

        all_text = post_text.find_all('li')
        out = '*Изменения в индексах (%s)*' % data_in_text
        if all_text is not None:
            for i in range(len(all_text)):

                out += '\n\n' + all_text[i].text
        else:
            out += '\n\n' + post_title

        today_chek = now.strftime("%d-%b-%y")
        today_chek = datetime.datetime.strptime(today_chek, "%d-%b-%y")
        if now.weekday() == 0:
            yesterday_chek = now - datetime.timedelta(days=3)
        else:
            yesterday_chek = now - datetime.timedelta(days=1)
        yesterday_chek = yesterday_chek.strftime("%d-%b-%y")
        yesterday_chek = datetime.datetime.strptime(yesterday_chek, "%d-%b-%y")

        # if post_date == today_chek or post_date == yesterday_chek:
        #     tg_bot.send_post(cfg.CHANNEL_CHAT_ID, out)
        #     tg_bot.send_message("Index change occurred. Look at the channel!")

        if week_day is not None:
            for n in range(len(week)):
                if week_day == week[n] and week_now == week[n - 1]:
                    if today < data_in_text_dt:
                        tg_bot.send_post(cfg.CHANNEL_CHAT_ID, out)
                        tg_bot.send_message("Index change occurred. Look at the channel!")
                else:
                    pass
        elif prev_data_in_text_dt == today:
            tg_bot.send_post(cfg.CHANNEL_CHAT_ID, out)
            tg_bot.send_message("Index change occurred. Look at the channel!")
        counter -= 1

    tg_bot.send_message("Index change checked!")
