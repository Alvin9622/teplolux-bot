"""Chuqur analitika — peak soatlar + haftalik trend grafigi."""
import datetime
import logging

import database as db

logger = logging.getLogger(__name__)


async def build_analytics_chart(user_id):
    """2 grafik (peak soatlar + 8 haftalik trend) PNG bytes (matplotlib yo'q bo'lsa None)."""
    try:
        import io
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    since8  = (datetime.datetime.now() - datetime.timedelta(weeks=8)).strftime("%Y-%m-%d")
    since30 = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    by_hour = await db.productivity_by_hour(user_id, since30)
    weekly  = await db.weekly_totals(user_id, since8)
    if not by_hour and not weekly:
        return None

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7))

    hours = list(range(6, 22))
    vals  = [round(by_hour.get(h, 0) / 3600, 1) for h in hours]
    ax1.bar([f"{h}:00" for h in hours], vals, color="#2E86DE")
    ax1.set_title("Qaysi soatlarda samarali (30 kun, soat)")
    ax1.tick_params(axis="x", rotation=60, labelsize=7)

    labels = [w for w, _ in weekly]
    wvals  = [round(s / 3600, 1) for _, s in weekly]
    if labels:
        ax2.plot(labels, wvals, marker="o", color="#27AE60")
    ax2.set_title("Haftalik jami vaqt trendi (8 hafta, soat)")
    ax2.tick_params(axis="x", rotation=45, labelsize=7)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
