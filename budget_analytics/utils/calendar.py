import datetime as dt
import holidays as hol
import pandas as pd

from budget_analytics.constants import Calendar


def get_calendar_dates(
    calendar: Calendar, start_date: dt.date, end_date: dt.date
) -> list[dt.date]:
    match calendar:
        case Calendar.EVERYDAY:
            dates = pd.date_range(start=start_date, end=end_date, freq="D").to_list()
            return list(map(lambda d: d.date(), dates))
        case Calendar.GB:
            holidays = hol.country_holidays(country="GB", subdiv="ENG")
        case _:
            raise NotImplementedError("Calendar not implemented")

    # Business Days Ex Holidays
    bdates_base = pd.bdate_range(start=start_date, end=end_date).to_list()
    bdates = []
    for bdate in bdates_base:
        if bdate.date() not in holidays:
            bdates.append(bdate.date())
    return sorted(bdates)
