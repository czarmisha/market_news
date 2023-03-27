import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar


def is_holiday(date=None):
    if not date:
        date = datetime.datetime.now().date()
    holidays = USFederalHolidayCalendar().holidays().strftime('%Y-%m-%d').to_list()
    return True if date.strftime('%Y-%m-%d') in holidays else False