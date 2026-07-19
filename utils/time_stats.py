"""Vaqt boshqaruvi hisobotlari va darajalar."""
import datetime

import database as db

LEVELS = [
    (0,    "🌱 Yangi boshlovchi"),
    (100,  "🌿 O'suvchi"),
    (500,  "🌳 Tajribali"),
    (1500, "⭐ Usta"),
    (5000, "🏆 Legenda"),
]


def level_for(points: int) -> str:
    name = LEVELS[0][1]
    for threshold, lvl in LEVELS:
        if points >= threshold:
            name = lvl
    return name


def bar(value: int, total: int, width: int = 10) -> str:
    if total == 0:
        return "▱" * width
    filled = round(value / total * width)
    return "▰" * filled + "▱" * (width - filled)


async def build_week_report(user_id: int) -> str:
    start = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    by_cat = await db.time_by_category_since(user_id, start)
    total = sum(s for _, s in by_cat)
    pomos = await db.count_pomodoros_since(user_id, start)
    plan_rate = await db.plan_completion_since(user_id, start)

    lines = ["📊 <b>Haftalik statistika</b> (so'nggi 7 kun)\n"]
    if total:
        th, tm = divmod(total // 60, 60)
        lines.append(f"⏱ Jami hisoblangan vaqt: <b>{th} soat {tm} daq</b>\n")
        for cat, sec in sorted(by_cat, key=lambda x: -x[1]):
            m = sec // 60
            h, mm = divmod(m, 60)
            dur = f"{h}s {mm}d" if h else f"{mm}d"
            lines.append(f"{cat[:8]:8} {bar(sec, total)} {dur}")
    else:
        lines.append("⏱ Bu hafta vaqt hisoblanmagan.")
    lines.append(f"\n🍅 Pomodorolar: <b>{pomos}</b>")
    lines.append(f"📋 Reja bajarilishi: <b>{plan_rate}%</b>")
    return "\n".join(lines)


async def build_streak_card(user_id: int) -> str:
    s = await db.get_focus_stats(user_id)
    total_h = s["total_focus_minutes"] // 60
    return (
        "🔥 <b>Sizning natijalaringiz</b>\n\n"
        f"🔥 Joriy streak: <b>{s['current_streak']} kun</b>\n"
        f"🏅 Eng uzun streak: {s['longest_streak']} kun\n"
        f"⏱ Jami fokus vaqti: {total_h} soat\n"
        f"🍅 Jami pomodorolar: {s['total_pomodoros']}\n"
        f"⭐ Fokus ballari: <b>{s['focus_points']}</b>\n"
        f"🎖 Daraja: {level_for(s['focus_points'])}\n\n"
        "<i>Har kuni kamida 1 pomodoro yoki 1 reja bandini bajarib, "
        "streakni uzmang!</i>"
    )


async def build_week_chart(user_id: int):
    """Haftalik vaqt taqsimotini PNG bytes qilib qaytaradi (matplotlib yo'q bo'lsa None)."""
    try:
        import io
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    start = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
    by_cat = await db.time_by_category_since(user_id, start)
    if not by_cat:
        return None
    data = sorted(by_cat, key=lambda x: x[1])
    cats  = [c for c, _ in data]
    hours = [round(s / 3600, 1) for _, s in data]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(cats, hours, color="#2E86DE")
    ax.set_xlabel("Soat")
    ax.set_title("Haftalik vaqt taqsimoti (7 kun)")
    for bar, h in zip(bars, hours):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{h}s", va="center", fontsize=9)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
