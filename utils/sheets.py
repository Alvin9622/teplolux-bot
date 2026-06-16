"""
Google Sheets integration.
Har bir vazifa, izoh, faollik real-vaqtda Google Sheetsga yuboriladi.

Kerakli env vars:
  GOOGLE_CREDENTIALS_JSON  — service account JSON (butun matn yoki base64)
  GOOGLE_SHEET_ID          — spreadsheet ID (URL dagi uzun matn)
"""

import asyncio
import base64
import datetime
import json
import logging
import os
from functools import wraps

logger = logging.getLogger(__name__)

_gc    = None   # gspread client
_sheet = None   # Spreadsheet object

SHEET_TASKS    = "Vazifalar"
SHEET_COMMENTS = "Izohlar"
SHEET_ACTIVITY = "Faollik"

STATUS_UZ  = {
    "new": "🆕 Yangi", "in_progress": "🔄 Jarayonda",
    "done": "✅ Bajarildi", "cancelled": "❌ Bekor", "review": "👀 Tekshiruvda"
}
PRIORITY_UZ = {"high": "🔴 Yuqori", "medium": "🟡 O'rta", "low": "🟢 Past"}

TASK_HEADERS = [
    "ID", "Nomi", "Mas'ul", "Lavozim", "Kategoriya",
    "Holat", "Ustuvorlik", "Muddat", "Bajarildi %",
    "Tasdiqlangan", "Yaratildi", "Yangilandi", "Yaratgan"
]
COMMENT_HEADERS = [
    "ID", "Vazifa ID", "Vazifa nomi", "Muallif", "Matn", "Sana"
]
ACTIVITY_HEADERS = [
    "Sana va vaqt", "Amal", "Vazifa ID", "Vazifa nomi",
    "Foydalanuvchi", "Eski qiymat", "Yangi qiymat"
]


def _fmt(iso):
    if not iso:
        return ""
    try:
        return datetime.date.fromisoformat(iso[:10]).strftime("%d.%m.%Y")
    except Exception:
        return str(iso)


def _now():
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M")


def _init_client():
    global _gc
    if _gc:
        return _gc
    cred_raw = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    if not cred_raw:
        logger.warning("GOOGLE_CREDENTIALS_JSON not set — Google Sheets disabled")
        return None
    try:
        # Base64 yoki raw JSON
        try:
            cred_data = json.loads(cred_raw)
        except json.JSONDecodeError:
            cred_data = json.loads(base64.b64decode(cred_raw).decode())
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(cred_data, scopes=scopes)
        _gc = gspread.authorize(creds)
        logger.info("Google Sheets client initialized ✅")
        return _gc
    except Exception as e:
        logger.error("Google Sheets init error: %s", e)
        return None


def _get_spreadsheet():
    global _sheet
    if _sheet:
        return _sheet
    gc = _init_client()
    if not gc:
        return None
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    if not sheet_id:
        logger.warning("GOOGLE_SHEET_ID not set — Google Sheets disabled")
        return None
    try:
        _sheet = gc.open_by_key(sheet_id)
        _ensure_worksheets(_sheet)
        logger.info("Google Spreadsheet opened: %s", _sheet.title)
        return _sheet
    except Exception as e:
        logger.error("Open spreadsheet error: %s", e)
        _sheet = None
        return None


def _ensure_worksheets(ss):
    existing = [ws.title for ws in ss.worksheets()]
    for title, headers in [
        (SHEET_TASKS,    TASK_HEADERS),
        (SHEET_COMMENTS, COMMENT_HEADERS),
        (SHEET_ACTIVITY, ACTIVITY_HEADERS),
    ]:
        if title not in existing:
            ws = ss.add_worksheet(title=title, rows=1000, cols=len(headers))
            ws.append_row(headers, value_input_option="USER_ENTERED")
            # Header formatting
            try:
                ws.format("A1:Z1", {
                    "backgroundColor": {"red": 0.122, "green": 0.306, "blue": 0.475},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                })
            except Exception:
                pass
        else:
            # Header yo'q bo'lsa qo'sh
            ws = ss.worksheet(title)
            first = ws.row_values(1)
            if not first:
                ws.insert_row(headers, 1, value_input_option="USER_ENTERED")


def _find_task_row(ws, task_id):
    """Vazifa ID bo'yicha qator raqamini topadi."""
    try:
        col_a = ws.col_values(1)  # ID ustuni
        for i, val in enumerate(col_a[1:], start=2):  # 1-qator header
            if str(val) == str(task_id):
                return i
    except Exception:
        pass
    return None


def sheets_safe(fn):
    """Sheets xatolarini log qilib, botni to'xtatmaydi."""
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            await asyncio.get_event_loop().run_in_executor(None, lambda: fn(*args, **kwargs))
        except Exception as e:
            logger.error("Sheets %s error: %s", fn.__name__, e)
    return wrapper


# ─── PUBLIC API ─────────────────────────────────────────────────

async def sync_task(task: dict, assignee: dict = None, creator: dict = None):
    """Vazifani Sheets ga qo'shadi yoki yangilaydi."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: _sync_task_sync(task, assignee, creator))


def _sync_task_sync(task, assignee, creator):
    ss = _get_spreadsheet()
    if not ss:
        return
    try:
        ws = ss.worksheet(SHEET_TASKS)
        row = [
            task["id"],
            task.get("title") or "",
            assignee["full_name"] if assignee else "—",
            assignee.get("position") or "—" if assignee else "—",
            task.get("category") or "—",
            STATUS_UZ.get(task.get("status"), task.get("status") or ""),
            PRIORITY_UZ.get(task.get("priority"), task.get("priority") or ""),
            _fmt(task.get("deadline")),
            task.get("progress_pct") or 0,
            "✅" if task.get("confirmed_at") else "⏳",
            _fmt(task.get("created_at")),
            _fmt(task.get("updated_at")),
            creator["full_name"] if creator else "—",
        ]
        existing_row = _find_task_row(ws, task["id"])
        if existing_row:
            ws.update(f"A{existing_row}:M{existing_row}", [row], value_input_option="USER_ENTERED")
        else:
            ws.append_row(row, value_input_option="USER_ENTERED")
        logger.info("sync_task OK: #%s", task["id"])
    except Exception as e:
        logger.error("sync_task error: %s", e, exc_info=True)


async def add_comment_to_sheet(comment_id: int, task: dict, author: dict, text: str):
    """Yangi izohni Sheets ga qo'shadi."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: _add_comment_sync(comment_id, task, author, text))


def _add_comment_sync(comment_id, task, author, text):
    ss = _get_spreadsheet()
    if not ss:
        return
    try:
        ws = ss.worksheet(SHEET_COMMENTS)
        ws.append_row([
            comment_id,
            task["id"],
            task.get("title") or "",
            author["full_name"] if author else "—",
            text,
            _now(),
        ], value_input_option="USER_ENTERED")
        logger.info("add_comment OK: task #%s", task["id"])
    except Exception as e:
        logger.error("add_comment_to_sheet error: %s", e, exc_info=True)


async def log_activity(action: str, task: dict, user: dict,
                       old_val: str = "", new_val: str = ""):
    """Faollikni (holat, foiz, tasdiqlash) Sheets ga yozadi."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: _log_activity_sync(action, task, user, old_val, new_val))


def _log_activity_sync(action, task, user, old_val, new_val):
    ss = _get_spreadsheet()
    if not ss:
        return
    try:
        ws = ss.worksheet(SHEET_ACTIVITY)
        ws.append_row([
            _now(),
            action,
            task["id"],
            task.get("title") or "",
            user["full_name"] if user else "—",
            old_val,
            new_val,
        ], value_input_option="USER_ENTERED")
        logger.info("log_activity OK: %s task #%s", action, task["id"])
    except Exception as e:
        logger.error("log_activity error: %s", e, exc_info=True)


async def full_sync_all_tasks():
    """Barcha vazifalarni Sheets bilan sinxronlaydi (startup da)."""
    import database as db
    loop = asyncio.get_running_loop()
    # Varoqlarni yaratish (vazifa bo'lmasa ham)
    ss = await loop.run_in_executor(None, _get_spreadsheet)
    if not ss:
        logger.warning("full_sync_all_tasks: spreadsheet unavailable, skipping")
        return
    tasks = await db.get_all_tasks_with_assignee()
    for t in tasks:
        assignee = await db.get_user_by_id(t["assignee_id"]) if t.get("assignee_id") else None
        creator  = await db.get_user_by_id(t["created_by"])  if t.get("created_by")  else None
        await sync_task(t, assignee, creator)
    logger.info("Full Sheets sync done: %d tasks", len(tasks))
