"""
Изменения в индексах (данные по запланированных изменениях индексов; пример сообщения)
Время публикации: 13:00 EST
Источник данных: не уверен, но вроде бы  briefing.
"""
import datetime
from telegram import bot
from utils.briefing import BriefingParser
import config.urls as urls


tg_bot = bot.BotHandler()

month = [datetime.datetime.strptime(f'2022-{i}-1', '%Y-%m-%d').strftime('%B') for i in range(1, 13)] # список месяцев формата %B - ['January', 'February', ...]
mon = [datetime.datetime.strptime(f'2022-{i}-1', '%Y-%m-%d').strftime('%b') for i in range(1, 13)] # список месяцев формата %b - ['Jan', 'Feb', ...]


def clean_text(text):
    """ убирает некоторые символы из текста для удобства поиска по словам """
    text = text.replace(',', '')
    text = text.replace('.', ' ')
    text = text.replace('\xa0', ' ') # \xa0 это пробел тот же самый
    text = text.replace('  ', ' ')
    text = text.replace('   ', ' ')
    return text


def main():
    print('**** indxch ****')
    now = datetime.datetime(2023, 1, 4) # datetime
    # now = datetime.datetime.now() # datetime
    today = now.strftime("%Y-%m-%d") 
    today = datetime.datetime.strptime(today, "%Y-%m-%d")
    # year_now = now.strftime("%Y")

    parser = BriefingParser(urls.url_indxch)
    soup = parser.soup

    posts = soup.find_all('div', attrs={"class": "lip-briefing-wrap"}) # все контейнеры с новостью
    posts_dt = soup.find_all('div', attrs={"class": "yui-dt-col-ArticleDT yui-dt-col-0 yui-dt-liner"}) # все контейнеры с датой публикации новости
    counter = 5 # походу берем 5 последних публикаций новостей?

    while counter >= 0:
        data_in_text = None
        post_date = posts_dt[counter].find('span', attrs={"class": "lip-ArticleDT"}).text.split(' ')
        post_date = datetime.datetime.strptime(post_date[0], "%d-%b-%y") # дата публикации новости 15-Mar-23
        year = post_date.strftime("%Y")

        body = posts[counter] # новость
        post_title = body.find('div', attrs={"class": "lip-title"}).text + ' ' # заголовок новости
        post_text = body.find('div',
                                 attrs={"class": "lip-article custom-style-big-width custom-style-hide"}) # текст новости

        full_text = post_title + '/// ' + post_text.text
        full_text = clean_text(full_text)

        words = full_text.split(" ") # весь текст разбил на слова ##########
        for i in range(len(words)):
            if data_in_text is None or not prev_data_in_text_dt == today: # 1й проход None 
                for m in range(len(month)):
                    if words[i] == month[m]: # если среди слов встретили месяц    тут формат January 5
                        try:
                            day_x = int(words[i + 1]) # по идее после месяца идет число даты
                        except ValueError:
                            continue

                        year_in_text = year
                        if m + 1 < post_date.month:
                            year_in_text = f'{int(year) + 1}'
                        data_in_text = words[i] + "//" + str(day_x) + '//' + year_in_text # месяц//число//текущий год строка
                        data_in_text_dt = datetime.datetime.strptime(data_in_text, "%B//%d//%Y") # месяц//число//текущий год ДАТА
                        delta = 3 if data_in_text_dt.weekday() == 0 else 1
                        prev_data_in_text_dt = data_in_text_dt - datetime.timedelta(days=delta) # предыдущий день  дата ???
                        break

                    elif words[i] == mon[m]: # тут формат Jan 5
                        try:
                            day_x = int(words[i + 1]) # по идее после месяца идет число даты
                        except ValueError:
                            continue
                        
                        year_in_text = year
                        if m + 1 < post_date.month:
                            year_in_text = f'{int(year) + 1}'
                        data_in_text = words[i] + "//" + str(day_x) + '//' + year_in_text  # месяц укороченный//число//текущий год строка
                        data_in_text_dt = datetime.datetime.strptime(data_in_text, "%b//%d//%Y") # месяц укороченный//число//текущий год ДАТА
                        delta = 3 if data_in_text_dt.weekday() == 0 else 1
                        prev_data_in_text_dt = data_in_text_dt - datetime.timedelta(days=delta) # предыдущий день  дата ???
                        break
            else:
                break

        try:
            data_in_text = data_in_text.replace('//', ' ')
        except Exception:
            pass

        all_text = post_text.find_all('li')
        if data_in_text is not None:
            out = f'*Изменения в индексах ({data_in_text})*'
            if all_text is not None:
                for i in range(len(all_text)):
                    out += '\n\n' + all_text[i].text
            else:
                out += '\n\n' + post_title

            if prev_data_in_text_dt == today:
                tg_bot.send_post(out)
                print('** indxch done **')

        counter -= 1

    print("Index change checked!")
