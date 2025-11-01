import datetime as dt
import pandas as pd

from budget_analytics.constants import Calendar, Frequency, HolidayAdjustment
from budget_analytics.utils.calendar import get_calendar_dates


def expand_recurring(
    df: pd.DataFrame, start_date: dt.date, end_date: dt.date
) -> pd.DataFrame:
    if (df["Growth"] != 0).sum() > 0:
        raise NotImplementedError("Growth not implemented.")

    ret = []
    for ind, row in df.iterrows():
        item_start = dt.datetime.strptime(row.Start_Date, "%Y-%m-%d")
        if row.End_Date == row.End_Date:
            item_end = dt.datetime.strptime(row.End_Date, "%Y-%m-%d")
        else:
            item_end = end_date
        calendar = Calendar(row["Calendar"])
        frequency = Frequency(row["Frequency"])
        day_index = int(row["Day_Index"])
        holiday_adjustment = HolidayAdjustment(row["Holiday_Adjustment"])
        match frequency:
            case Frequency.MONTHLY:
                item_start = dt.date(item_start.year, item_start.month, 1)
                if item_end.month != 12:
                    item_end = dt.date(
                        item_end.year, item_end.month + 1, 1
                    ) - dt.timedelta(days=1)
                else:
                    item_end = dt.date(item_end.year + 1, 1, 1) - dt.timedelta(days=1)
                all_dates = get_calendar_dates(calendar, item_start, item_end)
                year, month = item_start.year, item_start.month
                while True:
                    if (year, month) > (item_end.year, item_end.month):
                        break
                    month_dates = [
                        d for d in all_dates if d.year == year and d.month == month
                    ]
                    if len(month_dates) == 0:
                        continue
                    last_day = month_dates[-1].day
                    if day_index < 0:
                        target_day = last_day + 1 + day_index
                    elif day_index > last_day:
                        target_day = last_day
                    else:
                        target_day = day_index
                    match holiday_adjustment:
                        case HolidayAdjustment.NONE:
                            adjusted_date = dt.date(year, month, target_day)
                        case HolidayAdjustment.MOVE_EARLIER:
                            adjusted_date = pd.Series(1, index=all_dates)[
                                : dt.date(year, month, target_day)
                            ].index[-1]
                        case HolidayAdjustment.MOVE_LATER:
                            adjusted_date = pd.Series(1, index=all_dates)[
                                dt.date(year, month, target_day) :
                            ].index[0]
                        case _:
                            raise ValueError("Unknown holiday adjustment")
                    if start_date <= adjusted_date <= end_date:
                        recur_row = pd.Series(
                            {
                                "Description": row.Description,
                                "Amount_GBP": row.Amount_GBP,
                                "Direction": row.Direction,
                                "Date": adjusted_date,
                            }
                        )
                        ret.append(recur_row)
                    if month < 12:
                        month += 1
                    else:
                        year += 1
                        month = 1
            case _:
                raise NotImplementedError("Frequency not implemented")
    if len(ret) == 0:
        return pd.DataFrame(columns=["Description", "Amount_GBP", "Direction", "Date"])
    return pd.concat(ret, axis=1).T.sort_values("Date").reset_index(drop=True)
