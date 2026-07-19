from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from texts import TEXTS, T
from config import WEBAPP_URL


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
    rows.append([btn(T(lang, "btn_my_workplan"), "go:myplan"),
                 btn(T(lang, "btn_my_kpi"),      "go:mykpi")])
    rows.append([btn(T(lang, "btn_content"),  "go:content_menu"),
                 btn(T(lang, "btn_ideas"),    "go:ideas")])
    rows.append([btn(T(lang, "btn_time"), "go:tm_menu"),
                 btn(T(lang, "btn_qr"), "go:qr")])
    if WEBAPP_URL:
        rows.append([InlineKeyboardButton(
            text=T(lang, "btn_miniapp"),
            web_app=WebAppInfo(url=WEBAPP_URL)
        )])
    else:
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
        [btn(T(lang, "btn_workplan"),      "go:wp_menu"),
         btn(T(lang, "btn_kpi"),           "kpi:menu")],
        [btn(T(lang, "btn_content"),       "go:content_menu")],
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


# ─── IDEAS ───────────────────────────────────────────────────────

def ideas_menu_kb(lang, is_admin=False):
    rows = [
        [btn(T(lang, "idea_type_idea"),    "idea:add:idea")],
        [btn(T(lang, "idea_type_problem"), "idea:add:problem")],
        [btn(T(lang, "idea_type_future"),  "idea:add:future")],
        [btn("💡 Mening g'oyalarim" if (lang == "uz" and not is_admin) else
             "💡 Идеи и предложения (мои)" if (lang == "ru" and not is_admin) else
             "📋 Barcha g'oyalar" if lang == "uz" else "📋 Все идеи", "idea:list")],
    ]
    if is_admin:
        rows.append([btn("🆕 Yangilar" if lang == "uz" else "🆕 Новые", "idea:filter:new")])
    rows.append([back_btn(lang, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def idea_view_kb(lang, idea_id, status, is_admin=False):
    rows = []
    if is_admin:
        rows.append([
            btn("✅ Qabul" if lang == "uz" else "✅ Принять",  f"idea:status:{idea_id}:accepted"),
            btn("❌ Rad"   if lang == "uz" else "❌ Отклонить", f"idea:status:{idea_id}:rejected"),
        ])
        rows.append([btn("👀 Ko'rib chiqilmoqda" if lang == "uz" else "👀 На рассмотрении", f"idea:status:{idea_id}:review")])
        rows.append([btn("📝 Izoh" if lang == "uz" else "📝 Комментарий", f"idea:note:{idea_id}")])
    rows.append([back_btn(lang, "ideas")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def ideas_list_kb(lang, ideas, flt="all"):
    TYPE_ICONS = {"idea": "💡", "problem": "⚠️", "future": "🚀"}
    STATUS_ICONS = {"new": "🆕", "review": "👀", "accepted": "✅", "rejected": "❌"}
    rows = []
    for idea in ideas[:15]:
        tip  = TYPE_ICONS.get(idea["type"], "💡")
        st   = STATUS_ICONS.get(idea["status"], "🆕")
        name = (idea.get("full_name") or "?").split()[0]
        label = f"{tip}{st} {idea['text'][:28]}… | {name}"
        rows.append([btn(label, f"idea:view:{idea['id']}")])
    rows.append([back_btn(lang, "ideas")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── WORK PLANS ──────────────────────────────────────────────────

def wp_admin_menu_kb(lang):
    return ik(
        [btn(T(lang, "wp_template_new"),    "wp:new_template")],
        [btn("📋 Shablonlar" if lang=="uz" else "📋 Шаблоны", "wp:templates")],
        [btn("👥 Barcha rejalar" if lang=="uz" else "👥 Все планы", "wp:all_plans")],
        [back_btn(lang, "admin")],
    )

def wp_templates_kb(lang, templates):
    rows = []
    for t in templates:
        period = "🗓" if t["period_type"] == "monthly" else "📆"
        rows.append([btn(f"{period} {t['title']} — {t['position']}", f"wp:tmpl:{t['id']}")])
    rows.append([btn(T(lang, "wp_template_new"), "wp:new_template")])
    rows.append([back_btn(lang, "wp_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def wp_template_view_kb(lang, template_id):
    return ik(
        [btn("👤 Hodimga tayinlash" if lang=="uz" else "👤 Назначить сотруднику", f"wp:assign:{template_id}")],
        [btn("🗑 O'chirish" if lang=="uz" else "🗑 Удалить", f"wp:del_tmpl:{template_id}")],
        [back_btn(lang, "wp_templates")],
    )

def wp_period_kb(lang):
    return ik(
        [btn(T(lang, "wp_period_monthly"), "wp_period:monthly")],
        [btn(T(lang, "wp_period_weekly"),  "wp_period:weekly")],
    )

def wp_plan_kb(lang, plan_id, items, is_admin=False):
    rows = []
    for item in items:
        pct  = round(item["done_count"] / item["target_count"] * 100) if item["target_count"] else 0
        icon = "✅" if pct >= 100 else ("🔄" if pct > 0 else "⬜")
        label = f"{icon} {item['title'][:20]} {item['done_count']}/{item['target_count']}"
        rows.append([btn(label, f"wp:item:{item['id']}")])
    if is_admin:
        rows.append([back_btn(lang, "wp_all_plans")])
    else:
        rows.append([back_btn(lang, "myplan")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def wp_item_kb(lang, item_id, plan_id, is_admin=False):
    rows = [
        [btn("🔢 Natija yangilash" if lang=="uz" else "🔢 Обновить результат", f"wp:update:{item_id}")],
        [btn("💬 Izoh" if lang=="uz" else "💬 Заметка", f"wp:note:{item_id}")],
        [back_btn(lang, f"wp_plan_{plan_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def wp_my_plans_kb(lang, plans):
    rows = []
    for p in plans:
        items_total = p.get("items_total", 0)
        items_done  = p.get("items_done", 0)
        pct = round(items_done / items_total * 100) if items_total else 0
        icon = "✅" if pct >= 100 else ("🔄" if pct > 0 else "📋")
        rows.append([btn(f"{icon} {p['title']} {p['month']}/{p['year']} — {pct}%", f"wp:plan:{p['id']}")])
    rows.append([back_btn(lang, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def wp_all_plans_kb(lang, plans):
    rows = []
    for p in plans:
        name = (p.get("assignee_name") or "?").split()[0]
        rows.append([btn(f"👤 {name} — {p['title']} {p['month']}/{p['year']}", f"wp:plan:{p['id']}")])
    rows.append([back_btn(lang, "wp_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── KPI ─────────────────────────────────────────────────────────

def kpi_admin_menu_kb(lang, employees):
    rows = [[btn(f"👤 {e['full_name']}", f"kpi:emp:{e['id']}")] for e in employees]
    rows.append([back_btn(lang, "admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kpi_emp_kb(lang, user_id, months):
    rows = [[btn(m["label"], f"kpi:view:{user_id}:{m['month']}:{m['year']}")] for m in months]
    rows.append([btn("➕ KPI belgilash" if lang=="uz" else "➕ Установить KPI", f"kpi:set:{user_id}")])
    rows.append([back_btn(lang, "kpi_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kpi_view_kb(lang, targets, user_id, month, year, is_admin=False):
    rows = []
    for t in targets:
        pct  = round(t["actual_value"] / t["target_value"] * 100) if t["target_value"] else 0
        icon = "✅" if pct >= 100 else ("🔄" if pct > 0 else "⬜")
        rows.append([btn(f"{icon} {t['metric_name']}: {t['actual_value']}/{t['target_value']} ({pct}%)",
                         f"kpi:upd:{t['id']}")])
    if is_admin:
        rows.append([btn("➕ Ko'rsatkich qo'shish" if lang=="uz" else "➕ Добавить показатель",
                         f"kpi:set:{user_id}")])
        rows.append([btn("🗑 Tozalash" if lang=="uz" else "🗑 Очистить", f"kpi:clear:{user_id}:{month}:{year}")])
        rows.append([back_btn(lang, "kpi_menu")])
    else:
        rows.append([back_btn(lang, "mykpi")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kpi_my_months_kb(lang, months):
    rows = [[btn(m["label"], f"kpi:myview:{m['month']}:{m['year']}")] for m in months]
    rows.append([back_btn(lang, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── CONTENT CALENDAR ────────────────────────────────────────────

PLATFORMS = [
    ("📸 Instagram", "instagram"),
    ("✈️ Telegram", "telegram"),
    ("🎵 TikTok",   "tiktok"),
    ("👥 Facebook", "facebook"),
    ("▶️ YouTube",  "youtube"),
]
CONTENT_TYPES = [
    ("🖼 Post",       "post"),
    ("📖 Story",      "story"),
    ("🎬 Reels/Video","reels"),
    ("🎠 Carousel",   "carousel"),
    ("📹 Video",      "video"),
]

def content_menu_kb(lang, is_admin=False):
    rows = [
        [btn("➕ Kontent qo'shish" if lang=="uz" else "➕ Добавить контент", "content:add")],
        [btn("📅 Bu hafta" if lang=="uz" else "📅 Эта неделя", "content:week:0")],
        [btn("📊 Statistika" if lang=="uz" else "📊 Статистика", "content:stats")],
    ]
    if is_admin:
        rows.append([btn("👥 Barchasi" if lang=="uz" else "👥 Все", "content:all")])
    rows.append([back_btn(lang, "main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def content_platform_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(label, f"cplt:{val}")] for label, val in PLATFORMS]
    )

def content_type_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[btn(label, f"ctype:{val}")] for label, val in CONTENT_TYPES]
    )

def content_entry_kb(lang, entry_id, status, back_week=0):
    rows = []
    if status != "done":
        rows.append([btn("✅ Bajarildi" if lang=="uz" else "✅ Выполнено", f"content:done:{entry_id}")])
    if status != "failed":
        rows.append([btn("❌ Bajarilmadi" if lang=="uz" else "❌ Не выполнено", f"content:fail:{entry_id}")])
    rows.append([btn("🗑 O'chirish" if lang=="uz" else "🗑 Удалить", f"content:del:{entry_id}")])
    rows.append([back_btn(lang, f"content_week_{back_week}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def content_week_nav_kb(lang, week_offset, entries_count):
    nav = []
    if week_offset < 0:
        nav.append(btn("▶️ Keyingi" if lang=="uz" else "▶️ Далее", f"content:week:{week_offset+1}"))
    nav.append(btn("◀️ Oldingi" if lang=="uz" else "◀️ Назад", f"content:week:{week_offset-1}"))
    rows = []
    if nav:
        rows.append(nav)
    rows.append([btn("➕ Qo'shish" if lang=="uz" else "➕ Добавить", "content:add")])
    rows.append([back_btn(lang, "content_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
