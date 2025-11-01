import datetime as dt


def clean_date(date_str: str) -> dt.date:
    format_str = "%m/%d/%Y" if "/" in date_str else "%d %b %y"
    return dt.datetime.strptime(date_str, format_str).date()
