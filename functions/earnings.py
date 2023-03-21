"""
Earnings (список тикеров, компаний, которые публикуют отчеты AMC в предыдущий день или BMO в текущий с актуальными изменениями цен и разбивкой на GapUp-ы и GapDown-ы; пример сообщения) 
Время публикации: 07:00 EST
Источник данных: не уверен, но вроде бы briefing.com (список отчетов) и takion (изменения цены)
Комментарий: нужно посмотреть, как реализован сбор информации для этого сообщения в текущей версии бота

"""
from utils.briefing import BriefingParser
from config import urls

def main():
    parser = BriefingParser(urls.url_calendars)
    soup = parser.soup
