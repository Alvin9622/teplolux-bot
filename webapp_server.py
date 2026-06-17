"""
Teplolux Mini App — aiohttp web server.
Port: 8080 (Railway da PORT env var orqali)
"""
import hashlib
import hmac
import json
import logging
import os
import urllib.parse

from aiohttp import web

import database as db
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", "8080"))


def _verify_telegram_init_data(init_data: str) -> dict | None:
    """Telegram WebApp initData ni tekshiradi va user dict qaytaradi."""
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop("hash", "")
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed   = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(computed, received_hash):
            return None
        user_json = parsed.get("user", "{}")
        return json.loads(user_json)
    except Exception:
        return None


def _cors(response: web.Response) -> web.Response:
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Init-Data"
    return response


def json_resp(data, status=200):
    return _cors(web.Response(
        text=json.dumps(data, ensure_ascii=False),
        content_type="application/json",
        status=status
    ))


async def _get_tg_user(request: web.Request):
    init_data = request.headers.get("X-Init-Data", "")
    if not init_data:
        return None
    return _verify_telegram_init_data(init_data)


# ─── API ENDPOINTS ───────────────────────────────────────────────

async def api_dashboard(request: web.Request):
    tg_user = await _get_tg_user(request)
    if not tg_user:
        return json_resp({"error": "unauthorized"}, 401)
    tg_id = tg_user.get("id")
    user  = await db.get_user(tg_id)
    if not user:
        return json_resp({"error": "not_registered"}, 403)
    is_admin = user["role"] == "admin"
    if is_admin:
        data = await db.get_dashboard_data_admin()
        return json_resp({"role": "admin", **data})
    else:
        data = await db.get_dashboard_data_employee(user["id"])
        return json_resp({"role": "employee", **data})


async def api_roadmap(request: web.Request):
    tg_user = await _get_tg_user(request)
    if not tg_user:
        return json_resp({"error": "unauthorized"}, 401)
    tasks = await db.get_roadmap_tasks()
    by_phase = {}
    for t in tasks:
        p = t["phase"]
        by_phase.setdefault(p, []).append({
            "id":     t["id"],
            "title":  t["title"],
            "status": t["status"],
            "notes":  t.get("notes") or "",
            "deadline":      t.get("deadline") or "",
            "assignee_name": t.get("assignee_name") or "",
        })
    return json_resp({"phases": by_phase})


async def api_expenses(request: web.Request):
    tg_user = await _get_tg_user(request)
    if not tg_user:
        return json_resp({"error": "unauthorized"}, 401)
    user = await db.get_user(tg_user.get("id"))
    if not user:
        return json_resp({"error": "not_registered"}, 403)
    is_admin = user["role"] == "admin"
    if is_admin:
        expenses = await db.get_expenses()
    else:
        expenses = await db.get_expenses(created_by=user["id"])
    result = [{
        "id":       e["id"],
        "name":     e["name"],
        "amount":   e["amount"],
        "currency": e["currency"],
        "status":   e["status"],
        "deadline": e.get("deadline") or "",
        "note":     e.get("note") or "",
        "created_at": (e.get("created_at") or "")[:10],
    } for e in expenses]
    return json_resp({"expenses": result})


async def api_tasks(request: web.Request):
    tg_user = await _get_tg_user(request)
    if not tg_user:
        return json_resp({"error": "unauthorized"}, 401)
    user = await db.get_user(tg_user.get("id"))
    if not user:
        return json_resp({"error": "not_registered"}, 403)
    is_admin = user["role"] == "admin"
    if is_admin:
        tasks = await db.get_all_tasks_with_assignee()
    else:
        tasks = await db.get_tasks_for_user(user["id"])
    result = [{
        "id":       t["id"],
        "title":    t["title"],
        "status":   t["status"],
        "priority": t.get("priority") or "medium",
        "deadline": t.get("deadline") or "",
        "progress": t.get("progress_pct") or 0,
        "assignee": t.get("assignee_name") or "",
        "category": t.get("category") or "",
    } for t in tasks]
    return json_resp({"tasks": result})


async def options_handler(request: web.Request):
    return _cors(web.Response(status=204))


# ─── STATIC HTML ─────────────────────────────────────────────────

async def index(request: web.Request):
    html_path = os.path.join(os.path.dirname(__file__), "webapp", "index.html")
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    return web.Response(text=content, content_type="text/html")


async def static_file(request: web.Request):
    fname = request.match_info["filename"]
    fpath = os.path.join(os.path.dirname(__file__), "webapp", fname)
    if not os.path.exists(fpath):
        return web.Response(status=404)
    content_types = {
        ".js":  "application/javascript",
        ".css": "text/css",
        ".png": "image/png",
        ".ico": "image/x-icon",
    }
    ext  = os.path.splitext(fname)[1]
    ct   = content_types.get(ext, "application/octet-stream")
    with open(fpath, "rb") as f:
        return web.Response(body=f.read(), content_type=ct)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/",                   index)
    app.router.add_get("/static/{filename}",  static_file)
    app.router.add_get("/api/dashboard",      api_dashboard)
    app.router.add_get("/api/roadmap",        api_roadmap)
    app.router.add_get("/api/expenses",       api_expenses)
    app.router.add_get("/api/tasks",          api_tasks)
    app.router.add_get("/api/budget",         api_budget)
    app.router.add_get("/api/stats",          api_stats)
    app.router.add_route("OPTIONS", "/{path:.*}", options_handler)
    return app


async def start_webapp():
    app  = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("Mini App server started on port %d", PORT)
    return runner


async def api_budget(request: web.Request):
    tg_user = await _get_tg_user(request)
    if not tg_user:
        return json_resp({"error": "unauthorized"}, 401)
    user = await db.get_user(tg_user.get("id"))
    if not user or user["role"] != "admin":
        return json_resp({"error": "forbidden"}, 403)
    import datetime as dt
    now = dt.datetime.now()
    result = []
    for i in range(6):
        m = (now.month - i - 1) % 12 + 1
        y = now.year if (now.month - i) > 0 else now.year - 1
        budget = await db.get_budget(m, y)
        totals = {}
        for cur in ("USD", "UZS", "RUB"):
            totals[cur] = await db.get_monthly_expense_total(m, y, cur)
        result.append({
            "month": m, "year": y,
            "limits": {
                "USD": budget["limit_usd"] if budget else 0,
                "UZS": budget["limit_uzs"] if budget else 0,
                "RUB": budget["limit_rub"] if budget else 0,
            },
            "spent": totals,
        })
    return json_resp({"months": result})


async def api_stats(request: web.Request):
    tg_user = await _get_tg_user(request)
    if not tg_user:
        return json_resp({"error": "unauthorized"}, 401)
    user = await db.get_user(tg_user.get("id"))
    if not user:
        return json_resp({"error": "not_registered"}, 403)
    import datetime as dt
    now = dt.datetime.now()
    stats = await db.get_expense_stats(now.month, now.year)
    leaderboard = await db.get_all_time_leaderboard()
    top = [{
        "name":     u["full_name"].split()[0],
        "done":     u["done"] or 0,
        "total":    u["total"] or 0,
        "overdue":  u["overdue"] or 0,
    } for u in leaderboard[:7]]
    return json_resp({
        "expense_stats": stats,
        "leaderboard": top,
    })
