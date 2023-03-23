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
    print('**** starting indxch ****')

    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # сегодня в формате Datetime без часов минут и тд

    parser = BriefingParser(urls.url_indxch) # парсим url
    soup = parser.soup # получаем html

    posts = soup.find_all('div', attrs={"class": "lip-briefing-wrap"}) # все контейнеры с текстом новости
    posts_dt = soup.find_all('div', attrs={"class": "yui-dt-col-ArticleDT yui-dt-col-0 yui-dt-liner"}) # все контейнеры с датой публикации новости
    counter = 5 # счетчик сколько последних постов мы смотрим

    while counter >= 0:
        data_in_text = None # дата в тексте (изначально мы ее еще не нашли поэтому None)
        post_date = posts_dt[counter].find('span', attrs={"class": "lip-ArticleDT"}).text.split(' ')
        post_date = datetime.datetime.strptime(post_date[0], "%d-%b-%y") # дата публикации новости в формате 15-Mar-23 преобразуем в Datetime
        year = post_date.strftime("%Y") # год публикации

        body = posts[counter] # весь текст новости
        post_title = body.find('div', attrs={"class": "lip-title"}).text + ' ' # заголовок новости
        post_text = body.find('div',
                                 attrs={"class": "lip-article custom-style-big-width custom-style-hide"}) # текст новости

        full_text = post_title + '/// ' + post_text.text
        full_text = clean_text(full_text) # это весь текст в формате заголовок/// текст новости. его чистим от некоторых символов лишних и оставляем пробелы для удобства поиска по словам

        words = full_text.split(" ") # весь текст разбил на слова
        for i in range(len(words)):
            # пока нет даты внутри новости(дата изменения индекса) или
            # пока дата предыдущего торгового дня внутри новости не равно сегодняшней дате
            if data_in_text is None or not prev_data_in_text_dt == today:
                for m in range(len(month)):  # бегаем по индексам списка месяцев
                    # всего есть 2 формата даты внутри новости: January 5 или Jan 5
                    if words[i] == month[m]: # если среди слов встретили месяц - тут формат January 5
                        try:
                            day_x = int(words[i + 1]) # по идее после месяца идет число даты
                        except ValueError:
                            continue

                        year_in_text = year # год замены индексов (по умолчанию делаем равным году публикации новости)
                        # тут проверка на вот такой случай:
                        # если дата публикации новости 28 декабря 2022 года, а сами замены, например, 5 января, то 5 января это явно же 2023 год уже будет
                        # года в тексте нет, есть только числу и месяц. Если такая ситуация случилась мы берем года публикации поста + 1 (2022 + 1 = 2023)
                        if m + 1 < post_date.month: 
                            year_in_text = f'{int(year) + 1}'
                        data_in_text = words[i] + "//" + str(day_x) + '//' + year_in_text # дата в тексте(дата замены) в формате месяц//число//текущий год - строка
                        data_in_text_dt = datetime.datetime.strptime(data_in_text, "%B//%d//%Y") # дата в тексте(дата замены) в формате месяц//число//текущий год - ДАТА
                        delta = 3 if data_in_text_dt.weekday() == 0 else 1 # если понедельник дата публикации то отнимает 3 дня иначе 1 день чтобы найти предыдущий день
                        prev_data_in_text_dt = data_in_text_dt - datetime.timedelta(days=delta) # предыдущий день  Datetime
                        break

                    elif words[i] == mon[m]: # если среди слов встретили месяц - тут формат Jan 5
                        try:
                            day_x = int(words[i + 1]) # по идее после месяца идет число даты
                        except ValueError:
                            continue
                        
                        year_in_text = year # год замены индексов (по умолчанию делаем равным году публикации новости)
                        # тут проверка на вот такой случай:
                        # если дата публикации новости 28 декабря 2022 года, а сами замены, например, 5 января, то 5 января это явно же 2023 год уже будет
                        # года в тексте нет, есть только числу и месяц. Если такая ситуация случилась мы берем года публикации поста + 1 (2022 + 1 = 2023)
                        if m + 1 < post_date.month:
                            year_in_text = f'{int(year) + 1}'
                        data_in_text = words[i] + "//" + str(day_x) + '//' + year_in_text # дата в тексте(дата замены) в формате месяц//число//текущий год - строка
                        data_in_text_dt = datetime.datetime.strptime(data_in_text, "%b//%d//%Y") # дата в тексте(дата замены) в формате месяц//число//текущий год - ДАТА
                        delta = 3 if data_in_text_dt.weekday() == 0 else 1 # если понедельник дата публикации то отнимает 3 дня иначе 1 день чтобы найти предыдущий день
                        prev_data_in_text_dt = data_in_text_dt - datetime.timedelta(days=delta) # предыдущий день  Datetime
                        break
            else:
                break

        try:
            data_in_text = data_in_text.replace('//', ' ')
        except Exception:
            pass

        all_text = post_text.find_all('li')
        if data_in_text is not None: # если есть дата изменения индексов
            out = f'*Изменения в индексах ({data_in_text})*'
            if all_text is not None: # если есть текст новости
                for i in range(len(all_text)):
                    out += '\n\n' + all_text[i].text
            else:
                out += '\n\n' + post_title

            # если дата изменения индексов ЗАВТРА то отправляем
            if prev_data_in_text_dt == today: 
                tg_bot.send_post(out)
                print('** indxch done **')

        counter -= 1

    print("Index change checked!")
