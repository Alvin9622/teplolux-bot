import datetime
from texts import T, status_txt, priority_txt, reminder_txt, TEXTS


def fmt_date(iso):
    if not iso:
        return "—"
    try:
        return datetime.date.fromisoformat(iso[:10]).strftime("%d.%m.%Y")
    except Exception:
        return iso


def days_left_str(deadline_iso, lang):
    if not deadline_iso:
        return ""
    try:
        d     = datetime.date.fromisoformat(deadline_iso[:10])
        delta = (d - datetime.date.today()).days
        if delta < 0:
            return f" 🔴 {abs(delta)} kun kech" if lang=="uz" else f" 🔴 {abs(delta)} д. просрочено"
        elif delta == 0:
            return " 🔥 BUGUN!" if lang=="uz" else " 🔥 СЕГОДНЯ!"
        elif delta == 1:
            return " 🚨 Ertaga!" if lang=="uz" else " 🚨 Завтра!"
        elif delta <= 3:
            return f" ⏰ {delta} kun" if lang=="uz" else f" ⏰ {delta} дн."
        return ""
    except Exception:
        return ""


def progress_bar(pct, width=10):
    pct    = max(0, min(100, int(pct or 0)))
    filled = round(pct/100*width)
    return f"[{'█'*filled}{'░'*(width-filled)}] {pct}%"


def task_card(task, lang, assignee_name=None, file_count=0, comment_count=0):
    icon  = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(task["status"],"📌")
    picon = {"high":"🔴","medium":"🟡","low":"🟢"}.get(task["priority"],"⚪")
    pct   = task.get("progress_pct") or 0
    lines = [
        f"📌 <b>{task['title']}</b>",
        f"{'—'*24}",
    ]
    if task.get("description"):
        lines += [f"📄 {task['description']}", ""]
    lines += [
        f"📁 {task.get('category') or '—'}",
        f"{icon} <b>Holat:</b> {status_txt(lang, task['status'])}",
        f"{picon} <b>Ustuvorlik:</b> {priority_txt(lang, task['priority'])}",
        f"📅 <b>Muddat:</b> {fmt_date(task.get('deadline'))}",
    ]
    dl = days_left_str(task.get("deadline"), lang)
    if dl and task["status"] not in ("done","cancelled"):
        lines.append(f"⏱{dl.strip()}")
    if assignee_name:
        lines.append(f"👤 <b>Mas'ul:</b> {assignee_name}")
    confirmed = task.get("confirmed_at")
    if confirmed:
        lines.append("✅ <b>Tasdiqlangan</b>")
    else:
        lines.append("⏳ <b>Tasdiqlanmagan</b>")
    lines += ["", f"📊 <b>Bajarildi:</b>", progress_bar(pct)]
    if task["status"] == "cancelled" and task.get("cancel_reason"):
        lines += ["", f"💬 <b>Sabab:</b> {task['cancel_reason']}"]
    if task.get("done_at"):
        lines.append(f"✅ <b>Yakunlandi:</b> {fmt_date(task['done_at'])}")
    extras = []
    if file_count > 0:
        extras.append(f"📎{file_count}")
    if comment_count > 0:
        extras.append(f"💬{comment_count}")
    if extras:
        lines.append(" | ".join(extras))
    lines.append(f"\n🆔 #{task['id']}")
    return "\n".join(lines)


def monthly_stats_text(status_stats, user_stats, plans, month, year, lang):
    months    = TEXTS[lang]["months"]
    month_name = months[month-1]
    totals    = {r["status"]: r["cnt"] for r in status_stats}
    total_all = sum(totals.values())
    done_cnt  = totals.get("done", 0)
    in_prog   = totals.get("in_progress", 0)
    new_cnt   = totals.get("new", 0)
    canc      = totals.get("cancelled", 0)
    pct_done  = round(done_cnt/total_all*100) if total_all else 0

    lines = [
        f"📊 <b>Oylik statistika — {month_name} {year}</b>",
        f"{'—'*26}", "",
        f"📋 Jami: <b>{total_all}</b>",
        f"✅ Bajarildi: <b>{done_cnt}</b>",
        f"🔄 Jarayonda: <b>{in_prog}</b>",
        f"🆕 Yangi: <b>{new_cnt}</b>",
        f"❌ Bekor: <b>{canc}</b>", "",
        f"🎯 <b>Bajarilish: {pct_done}%</b>",
        progress_bar(pct_done), "",
    ]
    if plans:
        lines.append("📅 <b>Rejalar:</b>")
        for p in plans:
            pp = round(p["done_count"]/p["target_count"]*100) if p["target_count"] else 0
            lines.append(f"  • {p['title']}: {p['done_count']}/{p['target_count']} ({pp}%)")
        lines.append("")
    lines.append("👥 <b>Hodimlar reytingi:</b>")
    medals = ["🥇","🥈","🥉"]
    for i, e in enumerate(user_stats):
        total = e.get("total") or 0
        done  = e.get("done") or 0
        over  = e.get("overdue") or 0
        pct   = round(done/total*100) if total else 0
        medal = medals[i] if i < 3 else f"{i+1}."
        pos   = f" ({e['position']})" if e.get("position") else ""
        line  = f"{medal} <b>{e['full_name']}</b>{pos}: {done}/{total} ({pct}%)"
        if over:
            line += f" ⚠️{over}"
        lines.append(line)
    return "\n".join(lines)


def weekly_stats_text(user_stats, from_date, to_date, lang):
    from_fmt = fmt_date(from_date)
    to_fmt   = fmt_date(to_date)
    lines = [
        f"📊 <b>Haftalik hisobot</b>",
        f"📅 {from_fmt} — {to_fmt}",
        f"{'—'*26}", "",
    ]
    lines.append("👥 <b>Hodimlar:</b>")
    medals = ["🥇","🥈","🥉"]
    for i, e in enumerate(user_stats):
        total = e.get("total") or 0
        done  = e.get("done") or 0
        over  = e.get("overdue") or 0
        pct   = round(done/total*100) if total else 0
        medal = medals[i] if i < 3 else f"{i+1}."
        line  = f"{medal} <b>{e['full_name']}</b>: {done}/{total} ({pct}%)"
        if over:
            line += f" ⚠️{over}"
        lines.append(line)
    return "\n".join(lines)


def employee_monthly_report(user, tasks, month, year, lang):
    months     = TEXTS[lang]["months"]
    month_name = months[month-1]
    total = len(tasks)
    done  = sum(1 for t in tasks if t["status"]=="done")
    canc  = sum(1 for t in tasks if t["status"]=="cancelled")
    prog  = sum(1 for t in tasks if t["status"]=="in_progress")
    over  = sum(1 for t in tasks if t["status"] not in ("done","cancelled")
                and t.get("deadline") and t["deadline"] < datetime.date.today().isoformat())
    pct   = round(done/total*100) if total else 0
    pos   = f"\n💼 {user['position']}" if user.get("position") else ""
    lines = [
        f"📊 <b>{user['full_name']}</b>{pos}",
        f"📅 {month_name} {year} — Oylik hisobot",
        f"{'—'*26}", "",
        f"📋 Jami: {total} | ✅ {done} | 🔄 {prog} | ❌ {canc}",
        f"⚠️ Kechikkan: {over}", "",
        f"🎯 Bajarilish: <b>{pct}%</b>",
        progress_bar(pct), "",
    ]
    if tasks:
        lines.append("<b>Vazifalar:</b>")
        for t in tasks:
            icon = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(t["status"],"📌")
            dl   = fmt_date(t.get("deadline"))
            line = f"{icon} {t['title']} | {dl} | {t.get('progress_pct',0)}%"
            if t["status"]=="cancelled" and t.get("cancel_reason"):
                line += f"\n   💬 {t['cancel_reason']}"
            lines.append(f"  • {line}")
    return "\n".join(lines)


def leaderboard_text(emp_list, lang):
    medals = ["🥇", "🥈", "🥉"]
    lines = [
        "🏆 <b>Xodimlar reytingi (Jami)</b>" if lang == "uz" else "🏆 <b>Рейтинг сотрудников (Всего)</b>",
        "─" * 26, ""
    ]
    for i, e in enumerate(emp_list):
        total    = e.get("total") or 0
        done     = e.get("done") or 0
        over     = e.get("overdue") or 0
        on_time  = e.get("done_on_time") or 0
        pct      = round(done / total * 100) if total else 0
        medal    = medals[i] if i < 3 else f"{i+1}."
        pos      = f"\n   💼 {e['position']}" if e.get("position") else ""
        warn     = f" ⚠️{over}" if over else ""
        on_time_txt = f" ⏱{on_time}" if on_time else ""
        lines.append(
            f"{medal} <b>{e['full_name']}</b>{pos}\n"
            f"   ✅{done}/{total} ({pct}%){warn}{on_time_txt}\n"
            f"   {progress_bar(pct, 8)}"
        )
        lines.append("")
    return "\n".join(lines)


def overdue_tasks_text(tasks, lang):
    lines = [
        f"🔴 <b>Kechikkan vazifalar — {len(tasks)} ta</b>" if lang == "uz"
        else f"🔴 <b>Просроченные задачи — {len(tasks)} шт.</b>",
        "─" * 26, ""
    ]
    for t in tasks:
        d = datetime.date.fromisoformat(t["deadline"][:10])
        days_late = (datetime.date.today() - d).days
        aname = t.get("assignee_name") or "—"
        pos   = f" ({t['assignee_position']})" if t.get("assignee_position") else ""
        lines.append(
            f"📋 <b>{t['title']}</b>\n"
            f"👤 {aname}{pos}\n"
            f"📅 {fmt_date(t['deadline'])} | 🔴 {days_late} kun kech\n"
            f"📊 {t.get('progress_pct', 0)}% | 🆔 #{t['id']}"
        )
        lines.append("")
    return "\n".join(lines)


def emp_tasks_detail(emp, tasks, lang):
    total = len(tasks)
    done  = sum(1 for t in tasks if t["status"]=="done")
    over  = sum(1 for t in tasks if t["status"] not in ("done","cancelled")
                and t.get("deadline") and t["deadline"] < datetime.date.today().isoformat())
    pct   = round(done/total*100) if total else 0
    pos   = f"\n💼 {emp['position']}" if emp.get("position") else ""
    lines = [
        f"👤 <b>{emp['full_name']}</b>{pos}",
        f"📊 Jami: {total} | ✅ {done} ({pct}%) | ⚠️ {over}",
        progress_bar(pct),
        f"{'—'*24}", "",
    ]
    if not tasks:
        lines.append("📭 Vazifa yo'q.")
    else:
        for t in tasks:
            icon    = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(t["status"],"📌")
            dl      = fmt_date(t.get("deadline"))
            dl_warn = days_left_str(t.get("deadline"), lang) if t["status"] not in ("done","cancelled") else ""
            line    = f"{icon} <b>{t['title']}</b>\n   📅{dl}{dl_warn} | 📊{t.get('progress_pct',0)}%"
            if t["status"]=="cancelled" and t.get("cancel_reason"):
                line += f"\n   💬{t['cancel_reason']}"
            lines.append(line)
            lines.append("")
    return "\n".join(lines)
