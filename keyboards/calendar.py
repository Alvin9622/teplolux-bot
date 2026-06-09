import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def calendar_kb(year: int = None, month: int = None) -> InlineKeyboardMarkup:
    now = datetime.date.today()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    months_uz = ["Yan","Fev","Mar","Apr","May","Iyun",
                 "Iyul","Avg","Sen","Okt","Noy","Dek"]

    rows = []

    # Header: prev month | Month Year | next month
    rows.append([
        InlineKeyboardButton(text="◀️", callback_data=f"cal:prev:{year}:{month}"),
        InlineKeyboardButton(text=f"{months_uz[month-1]} {year}", callback_data="cal:ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal:next:{year}:{month}"),
    ])

    # Day names
    rows.append([
        InlineKeyboardButton(text=d, callback_data="cal:ignore")
        for d in ["Du","Se","Ch","Pa","Ju","Sh","Ya"]
    ])

    # Calendar days
    import calendar
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="cal:ignore"))
            else:
                date = datetime.date(year, month, day)
                # Mark past dates
                if date < now:
                    row.append(InlineKeyboardButton(text=f"·{day}·", callback_data="cal:ignore"))
                elif date == now:
                    row.append(InlineKeyboardButton(text=f"[{day}]", callback_data=f"cal:day:{year}:{month}:{day}"))
                else:
                    row.append(InlineKeyboardButton(text=str(day), callback_data=f"cal:day:{year}:{month}:{day}"))
        rows.append(row)

    # Quick buttons
    rows.append([
        InlineKeyboardButton(text="📅 Bugun", callback_data=f"cal:day:{now.year}:{now.month}:{now.day}"),
        InlineKeyboardButton(text="📅 +7 kun", callback_data=f"cal:day:{(now+datetime.timedelta(7)).year}:{(now+datetime.timedelta(7)).month}:{(now+datetime.timedelta(7)).day}"),
        InlineKeyboardButton(text="📅 +30 kun", callback_data=f"cal:day:{(now+datetime.timedelta(30)).year}:{(now+datetime.timedelta(30)).month}:{(now+datetime.timedelta(30)).day}"),
    ])

    rows.append([InlineKeyboardButton(text="❌ Bekor /bekor", callback_data="cal:cancel")])

    return InlineKeyboardMarkup(inline_keyboard=rows)
