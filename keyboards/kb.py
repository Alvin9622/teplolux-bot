from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import TEXTS, T


def ik(*rows):
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

def btn(text, data):
    return InlineKeyboardButton(text=text, callback_data=data)

def back_btn(lang, to="main"):
    return btn(T(lang, "back"), "go:" + to)

def lang_kb():
    return ik([btn("🇺🇿 O'zbek", "lang:uz"), btn("🇷🇺 Русский", "lang:ru")])

def main_kb(lang, is_admin=False):
    rows = []
    if is_admin:
        rows.append([btn(T(lang, "btn_admin"), "go:admin")])
    rows.append([btn(T(lang, "btn_my_tasks"), "go:mytasks")])
    rows.append([btn(T(lang, "btn_my_stats"), "go:mystats")])
    rows.append([btn(T(lang, "btn_dashboard"), "go:dashboard")])
    rows.append([btn(T(lang, "btn_miniapp"), "miniapp:info")])
    rows.append([btn("📖 Yo'riqnoma" if lang == "uz" else "📖 Руководство", "go:help"),
                 btn(T(lang, "btn_lang"), "go:lang")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_kb(lang):
    return ik(
        [btn(T(lang, "btn_add_task"),      "admin:add_task")],
        [btn(T(lang, "btn_add_plan"),      "admin:add_plan")],
        [btn(T(lang, "btn_all_tasks"),     "admin:tasks:all:0"),
         btn(T(lang, "btn_by_employee"),   "admin:by_emp")],
        [btn(T(lang, "btn_all_plans"),     "admin:plans")],
        [btn(T(lang, "btn_stats"),         "admin:stats"),
         btn(T(lang, "btn_leaderboard"),   "admin:leaderboard")],
        [btn(T(lang, "btn_overdue"),       "admin:overdue"),
         btn(T(lang, "btn_unconfirmed"),  "admin:unconfirmed")],
        [btn(T(lang, "btn_users"),         "admin:users")],
        [btn(T(lang, "btn_send_report"),   "admin:send_report"),
         btn(T(lang, "btn_export_excel"),  "admin:export:current")],
        [btn("🗓 Majlislar",               "admin:meetings")],
        [btn(T(lang, "btn_roadmap"),       "rm:menu")],
        [btn(T(lang, "btn_expenses"),      "admin:expenses")],
        [btn(T(lang, "btn_budget"),        "budget:menu"),
         btn(T(lang, "btn_activity"),      "activity:log:0")],
        [back_btn(lang, "main")],
    )

def task_filter_kb(lang):
    return ik(
        [btn("📋 Barchasi",   "admin:tasks:all:0"),
         btn("🆕 Yangi",      "admin:tasks:new:0")],
        [btn("🔄 Jarayonda",  "admin:tasks:in_progress:0"),
         btn("👀 Tekshiruvda","admin:tasks:review:0")],
        [btn("✅ Bajarildi",  "admin:tasks:done:0"),
         btn("❌ Bekor",      "admin:tasks:cancelled:0")],
        [back_btn(lang, "admin")],
    )

def tasks_list_kb(lang, tasks, page=0, flt="all", is_admin=False, back_to="admin"):
    PAGE  = 6
    start = page * PAGE
    chunk = tasks[start:start+PAGE]
    rows  = []
    for t in chunk:
        icon  = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(t["status"],"📌")
        dl    = (t.get("deadline") or "")[-5:].replace("-",".")
        label = f"{icon} {t['title'][:22]} {dl}"
        rows.append([btn(label, f"task:view:{t['id']}")])
    nav = []
    if page > 0:
        nav.append(btn("◀️", f"admin:tasks:{flt}:{page-1}"))
    if start + PAGE < len(tasks):
        nav.append(btn("▶️", f"admin:tasks:{flt}:{page+1}"))
    if nav:
        rows.append(nav)
    if is_admin:
        rows.append([btn("🔽 Filter", "admin:task_filter")])
        rows.append([back_btn(lang, back_to)])
    else:
        rows.append([back_btn(lang, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def task_actions_kb(lang, task_id, is_mine=True, is_admin=False, back_to="mytasks"):
    rows = []
    if is_mine:
        rows.append([btn("🔄 Holatni yangilash",  f"task:status:{task_id}")])
        rows.append([btn("📊 Foizni yangilash",   f"task:progress:{task_id}")])
        rows.append([btn("📎 Fayl yuborish",      f"task:upload:{task_id}")])
    if is_mine or is_admin:
        rows.append([btn("💬 Izoh qoldirish",     f"task:comment:{task_id}")])
    rows.append([btn("🗂 Fayllarni ko'rish",     f"task:files:{task_id}"),
                 btn("💬 Izohlar",               f"task:comments:{task_id}")])
    if is_admin:
        rows.append([btn("✏️ Tahrirlash",         f"task:edit:{task_id}")])
        rows.append([btn("🗑 O'chirish",          f"task:delete:{task_id}")])
    rows.append([back_btn(lang, back_to)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def task_edit_kb(lang, task_id):
    return ik(
        [btn("📝 Nom",       f"edit:title:{task_id}")],
        [btn("📄 Tavsif",    f"edit:desc:{task_id}")],
        [btn("📁 Kategoriya",f"edit:category:{task_id}")],
        [btn("📅 Muddat",    f"edit:deadline:{task_id}")],
        [btn("⚡ Ustuvorlik",f"edit:priority:{task_id}")],
        [btn("🔔 Eslatma",   f"edit:reminder:{task_id}")],
        [back_btn(lang, f"task_view_{task_id}")],
    )

def status_kb(lang, task_id):
    return ik(
        [btn(T(lang, "status_in_progress"), f"setstatus:{task_id}:in_progress")],
        [btn(T(lang, "status_review"),      f"setstatus:{task_id}:review")],
        [btn(T(lang, "status_done"),        f"setstatus:{task_id}:done")],
        [btn(T(lang, "status_cancelled"),   f"setstatus:{task_id}:cancelled")],
        [back_btn(lang, f"task_view_{task_id}")],
    )

def priority_kb(lang):
    return ik(
        [btn(T(lang, "priority_high"),   "priority:high")],
        [btn(T(lang, "priority_medium"), "priority:medium")],
        [btn(T(lang, "priority_low"),    "priority:low")],
    )

def category_kb(lang):
    cats = TEXTS[lang]["categories"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(c, f"category:{i}")] for i, c in enumerate(cats)]
    )

def assignee_kb(employees):
    rows = [[btn(
        f"👤 {e['full_name']}" + (f" — {e['position']}" if e.get("position") else ""),
        f"assignee:{e['id']}"
    )] for e in employees]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def reminder_kb(lang):
    opts = TEXTS[lang]["reminders"]
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(label, f"reminder:{days}")] for days, label in opts.items()]
    )

def month_kb(lang):
    months = TEXTS[lang]["months"]
    rows = []
    for i in range(0, 12, 3):
        row = []
        for j in range(3):
            if i + j < 12:
                row.append(btn(months[i+j], f"month:{i+j+1}"))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def employees_list_kb(lang, employees, back_to="admin"):
    rows = []
    for e in employees:
        icon = "👑" if e["role"] == "admin" else "👤"
        pos  = f" — {e['position']}" if e.get("position") else ""
        rows.append([btn(f"{icon} {e['full_name']}{pos}", f"user:manage:{e['id']}")])
    rows.append([btn("➕ Hodim qo'shish" if lang=="uz" else "➕ Добавить", "admin:add_user")])
    rows.append([back_btn(lang, back_to)])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def user_manage_kb(lang, user_id, role, back_to="admin"):
    toggle_role  = "employee" if role == "admin" else "admin"
    toggle_label = ("👤 Adminlikdan chiqarish" if role=="admin" else "👑 Admin qilish") if lang=="uz" else \
                   ("👤 Убрать из админов"     if role=="admin" else "👑 Назначить админом")
    return ik(
        [btn(toggle_label,                                             f"user:role:{user_id}:{toggle_role}")],
        [btn("📋 Vazifalarini ko'rish" if lang=="uz" else "📋 Задачи", f"admin:emp_tasks:{user_id}:0")],
        [btn("🚫 Bloklash" if lang=="uz" else "🚫 Заблокировать",     f"user:block:{user_id}")],
        [back_btn(lang, back_to)],
    )

def by_employee_kb(lang, emp_list):
    rows = []
    for e in emp_list:
        total = e.get("total") or 0
        done  = e.get("done") or 0
        over  = e.get("overdue") or 0
        pct   = round(done/total*100) if total else 0
        warn  = f" ⚠️{over}" if over else ""
        label = f"👤 {e['full_name']} | {done}/{total} ({pct}%){warn}"
        rows.append([btn(label, f"admin:emp_tasks:{e['id']}:0")])
    rows.append([back_btn(lang, "admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def stats_months_kb(lang):
    import datetime as dt
    now    = dt.datetime.now()
    months = TEXTS[lang]["months"]
    rows   = []
    for i in range(5, -1, -1):
        d = (now.replace(day=1) - dt.timedelta(days=i*28)).replace(day=1)
        rows.append([btn(f"{months[d.month-1]} {d.year}", f"stats:{d.month}:{d.year}")])
    rows.append([back_btn(lang, "admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def report_months_kb(lang):
    import datetime as dt
    now    = dt.datetime.now()
    months = TEXTS[lang]["months"]
    rows   = []
    for i in range(3, -1, -1):
        d = (now.replace(day=1) - dt.timedelta(days=i*28)).replace(day=1)
        rows.append([btn(f"{months[d.month-1]} {d.year}", f"report:{d.month}:{d.year}")])
    rows.append([back_btn(lang, "admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def back_kb(lang, to="main"):
    return ik([back_btn(lang, to)])

def new_user_role_kb(lang):
    return ik(
        [btn("👤 Oddiy hodim" if lang=="uz" else "👤 Сотрудник", "newrole:employee")],
        [btn("👑 Admin", "newrole:admin")],
    )

def new_user_lang_kb():
    return ik(
        [btn("🇺🇿 O'zbek", "newlang:uz"),
         btn("🇷🇺 Русский", "newlang:ru")],
    )

def plan_list_kb(lang, plans):
    rows = []
    for p in plans:
        pct = round(p["done_count"]/p["target_count"]*100) if p["target_count"] else 0
        rows.append([btn(f"📌 {p['title'][:25]} ({pct}%)", f"plan:edit:{p['id']}")])
    rows.append([back_btn(lang, "admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── EXPENSES ────────────────────────────────────────────────────

def expense_menu_kb(lang, is_admin=False):
    rows = [
        [btn(T(lang, "expense_add"), "exp:add")],
        [btn(T(lang, "expense_my"),  "exp:my")],
    ]
    if is_admin:
        rows.append([btn(T(lang, "expense_pending_list"), "exp:pending")])
        rows.append([btn(T(lang, "expense_all"),          "exp:all")])
        rows.append([btn(T(lang, "btn_exp_stats"),        "exp:stats")])
    rows.append([back_btn(lang, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def expense_view_kb(lang, expense_id, status, is_admin=False):
    rows = []
    if is_admin and status == "pending":
        rows.append([
            btn(T(lang, "btn_approve"),  f"exp:approve:{expense_id}"),
            btn(T(lang, "btn_reject"),   f"exp:reject:{expense_id}"),
        ])
        rows.append([btn(T(lang, "btn_postpone"), f"exp:postpone:{expense_id}")])
    if is_admin and status == "approved":
        rows.append([btn(T(lang, "btn_mark_paid"), f"exp:paid:{expense_id}")])
    rows.append([back_btn(lang, "expenses")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def currency_kb():
    return ik(
        [btn("💵 USD", "expcur:USD"), btn("🇺🇿 UZS", "expcur:UZS")],
        [btn("🇷🇺 RUB", "expcur:RUB")],
    )


# ─── ROAD MAP keyboards ───────────────────────────────────────────

def roadmap_menu_kb(lang):
    return ik(
        [btn(T(lang, "roadmap_phase_1_3"),   "rm:phase:1-3")],
        [btn(T(lang, "roadmap_phase_4_6"),   "rm:phase:4-6")],
        [btn(T(lang, "roadmap_phase_7_9"),   "rm:phase:7-9")],
        [btn(T(lang, "roadmap_phase_10_18"), "rm:phase:10-18")],
        [btn(T(lang, "roadmap_add"),         "rm:add")],
        [back_btn(lang, "admin")],
    )

def roadmap_phase_kb(lang, tasks, phase):
    rows = []
    for t in tasks:
        icon = "✅" if t["status"] == "done" else "⬜"
        rows.append([btn(f"{icon} {t['title'][:40]}", f"rm:task:{t['id']}")])
    rows.append([btn(T(lang, "roadmap_add"), f"rm:add:{phase}")])
    rows.append([back_btn(lang, "rm_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def roadmap_task_kb(lang, task):
    tid   = task["id"]
    phase = task["phase"]
    toggle = T(lang, "roadmap_mark_pending") if task["status"] == "done" else T(lang, "roadmap_mark_done")
    return ik(
        [btn(toggle,                         f"rm:done:{tid}")],
        [btn(T(lang, "roadmap_edit_title"),  f"rm:edit:title:{tid}"),
         btn(T(lang, "roadmap_edit_notes"),  f"rm:edit:notes:{tid}")],
        [btn(T(lang, "roadmap_yes_del"),     f"rm:del:{tid}")],
        [back_btn(lang, f"rm_phase_{phase}")],
    )

def roadmap_phase_select_kb(lang):
    return ik(
        [btn(T(lang, "roadmap_phase_1_3"),   "rm:newphase:1-3")],
        [btn(T(lang, "roadmap_phase_4_6"),   "rm:newphase:4-6")],
        [btn(T(lang, "roadmap_phase_7_9"),   "rm:newphase:7-9")],
        [btn(T(lang, "roadmap_phase_10_18"), "rm:newphase:10-18")],
        [back_btn(lang, "rm_menu")],
    )


# ─── ROAD MAP (extended) ─────────────────────────────────────────

def roadmap_task_ext_kb(lang, task):
    tid   = task["id"]
    phase = task["phase"]
    toggle = T(lang, "roadmap_mark_pending") if task["status"] == "done" else T(lang, "roadmap_mark_done")
    return ik(
        [btn(toggle,                               f"rm:done:{tid}")],
        [btn(T(lang, "roadmap_edit_title"),        f"rm:edit:title:{tid}"),
         btn(T(lang, "roadmap_edit_notes"),        f"rm:edit:notes:{tid}")],
        [btn(T(lang, "roadmap_edit_deadline"),     f"rm:edit:deadline:{tid}"),
         btn(T(lang, "roadmap_edit_assignee"),     f"rm:edit:assignee:{tid}")],
        [btn(T(lang, "roadmap_yes_del"),           f"rm:del:{tid}")],
        [back_btn(lang, f"rm_phase_{phase}")],
    )


# ─── BUDGET ──────────────────────────────────────────────────────

def budget_menu_kb(lang):
    return ik(
        [btn(T(lang, "budget_set"), "budget:set")],
        [back_btn(lang, "admin")],
    )


# ─── ACTIVITY LOG ────────────────────────────────────────────────

def activity_log_kb(lang, offset, has_more):
    rows = []
    nav = []
    if offset > 0:
        nav.append(btn("◀️", f"activity:log:{max(0, offset-20)}"))
    if has_more:
        nav.append(btn("▶️", f"activity:log:{offset+20}"))
    if nav:
        rows.append(nav)
    rows.append([back_btn(lang, "admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── DASHBOARD ───────────────────────────────────────────────────

def dashboard_kb(lang):
    return ik(
        [btn(T(lang, "dashboard_refresh"), "dashboard:refresh")],
        [back_btn(lang, "main")],
    )
