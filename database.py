import aiosqlite
import datetime
import os
from config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name   TEXT NOT NULL,
            username    TEXT,
            position    TEXT DEFAULT '',
            role        TEXT DEFAULT 'employee',
            lang        TEXT DEFAULT 'uz',
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            title              TEXT NOT NULL,
            description        TEXT DEFAULT '',
            category           TEXT DEFAULT '',
            assignee_id        INTEGER,
            created_by         INTEGER,
            deadline           TEXT,
            priority           TEXT DEFAULT 'medium',
            status             TEXT DEFAULT 'new',
            cancel_reason      TEXT DEFAULT '',
            progress_pct       INTEGER DEFAULT 0,
            reminder_days      INTEGER DEFAULT 0,
            confirmed_at       TEXT,
            confirm_sent_count INTEGER DEFAULT 0,
            created_at         TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at         TEXT DEFAULT CURRENT_TIMESTAMP,
            done_at            TEXT,
            FOREIGN KEY (assignee_id) REFERENCES users(id),
            FOREIGN KEY (created_by)  REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS task_files (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id    INTEGER,
            user_id    INTEGER,
            file_id    TEXT NOT NULL,
            file_type  TEXT DEFAULT 'document',
            caption    TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS task_comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id    INTEGER,
            user_id    INTEGER,
            text       TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS plans (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            description  TEXT DEFAULT '',
            category     TEXT DEFAULT '',
            month        INTEGER,
            year         INTEGER,
            target_count INTEGER DEFAULT 1,
            done_count   INTEGER DEFAULT 0,
            created_by   INTEGER,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS meetings (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            description  TEXT DEFAULT '',
            decisions    TEXT DEFAULT '',
            meeting_date TEXT,
            created_by   INTEGER,
            created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at   TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS meeting_tasks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            task_id    INTEGER,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id),
            FOREIGN KEY (task_id)    REFERENCES tasks(id)
        );

        CREATE TABLE IF NOT EXISTS task_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id    INTEGER,
            user_id    INTEGER,
            action     TEXT,
            old_value  TEXT,
            new_value  TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reminders_sent (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id  INTEGER,
            type     TEXT,
            sent_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS roadmap_tasks (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            phase         TEXT NOT NULL,
            title         TEXT NOT NULL,
            notes         TEXT DEFAULT '',
            status        TEXT DEFAULT 'pending',
            deadline      TEXT DEFAULT '',
            assignee_name TEXT DEFAULT '',
            created_at    TEXT,
            updated_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            amount        REAL NOT NULL,
            currency      TEXT DEFAULT 'USD',
            deadline      TEXT DEFAULT '',
            note          TEXT DEFAULT '',
            file_id       TEXT DEFAULT '',
            file_type     TEXT DEFAULT '',
            status        TEXT DEFAULT 'pending',
            created_by    INTEGER,
            approved_by   INTEGER,
            reject_reason TEXT DEFAULT '',
            postpone_date TEXT DEFAULT '',
            created_at    TEXT,
            updated_at    TEXT,
            FOREIGN KEY (created_by)  REFERENCES users(id),
            FOREIGN KEY (approved_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS budget_settings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            month      INTEGER NOT NULL,
            year       INTEGER NOT NULL,
            limit_usd  REAL DEFAULT 0,
            limit_uzs  REAL DEFAULT 0,
            limit_rub  REAL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(month, year)
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id   INTEGER NOT NULL,
            action      TEXT NOT NULL,
            actor_id    INTEGER,
            old_value   TEXT DEFAULT '',
            new_value   TEXT DEFAULT '',
            created_at  TEXT
        );
        """)
        await db.commit()

    # ALTER TABLE migrations — safe (ignore if column already exists)
    async with aiosqlite.connect(DB_PATH) as db:
        for stmt in [
            "ALTER TABLE roadmap_tasks ADD COLUMN deadline TEXT DEFAULT ''",
            "ALTER TABLE roadmap_tasks ADD COLUMN assignee_name TEXT DEFAULT ''",
            "ALTER TABLE expenses ADD COLUMN deadline TEXT DEFAULT ''",
            "ALTER TABLE expenses ADD COLUMN note TEXT DEFAULT ''",
            "ALTER TABLE expenses ADD COLUMN file_id TEXT DEFAULT ''",
            "ALTER TABLE expenses ADD COLUMN file_type TEXT DEFAULT ''",
            "ALTER TABLE expenses ADD COLUMN reject_reason TEXT DEFAULT ''",
            "ALTER TABLE expenses ADD COLUMN postpone_date TEXT DEFAULT ''",
        ]:
            try:
                await db.execute(stmt)
                await db.commit()
            except Exception:
                pass


def _row(r):
    return dict(r) if r else None


# ─── USERS ──────────────────────────────────────────────────────

async def get_user(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)) as c:
            return _row(await c.fetchone())

async def get_user_by_id(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id=?", (user_id,)) as c:
            return _row(await c.fetchone())

async def create_user(telegram_id, full_name, username=None, role="employee", lang="uz", position=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id,full_name,username,role,lang,position) VALUES (?,?,?,?,?,?)",
            (telegram_id, full_name, username, role, lang, position)
        )
        await db.commit()

async def update_user_lang(telegram_id, lang):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang=? WHERE telegram_id=?", (lang, telegram_id))
        await db.commit()

async def update_user_position(telegram_id, position):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET position=? WHERE telegram_id=?", (position, telegram_id))
        await db.commit()

async def set_user_role(telegram_id, role):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET role=? WHERE telegram_id=?", (role, telegram_id))
        await db.commit()

async def set_user_active(user_id, active):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_active=? WHERE id=?", (active, user_id))
        await db.commit()

async def get_all_employees():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE is_active=1 ORDER BY full_name") as c:
            return [_row(r) for r in await c.fetchall()]

async def get_all_active_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE is_active=1") as c:
            return [_row(r) for r in await c.fetchall()]


# ─── TASKS ──────────────────────────────────────────────────────

async def create_task(title, description, category, assignee_id,
                      created_by, deadline, priority="medium", reminder_days=0):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO tasks (title,description,category,assignee_id,created_by,"
            "deadline,priority,reminder_days,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (title, description, category, assignee_id, created_by, deadline, priority, reminder_days, now, now)
        )
        await db.commit()
        return c.lastrowid

async def update_task(task_id, title=None, description=None, category=None,
                      deadline=None, priority=None, reminder_days=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        t = _row(await (await db.execute("SELECT * FROM tasks WHERE id=?", (task_id,))).fetchone())
        if not t:
            return
        await db.execute(
            "UPDATE tasks SET title=?,description=?,category=?,deadline=?,priority=?,reminder_days=?,updated_at=? WHERE id=?",
            (
                title or t["title"],
                description if description is not None else t["description"],
                category or t["category"],
                deadline or t["deadline"],
                priority or t["priority"],
                reminder_days if reminder_days is not None else t["reminder_days"],
                now, task_id
            )
        )
        await db.commit()

async def get_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)) as c:
            return _row(await c.fetchone())

async def delete_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM task_files WHERE task_id=?", (task_id,))
        await db.execute("DELETE FROM task_comments WHERE task_id=?", (task_id,))
        await db.execute("DELETE FROM task_logs WHERE task_id=?", (task_id,))
        await db.execute("DELETE FROM meeting_tasks WHERE task_id=?", (task_id,))
        await db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        await db.commit()

async def get_tasks_for_user(user_id, status_filter=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status_filter:
            async with db.execute(
                "SELECT * FROM tasks WHERE assignee_id=? AND status=? ORDER BY deadline",
                (user_id, status_filter)
            ) as c:
                return [_row(r) for r in await c.fetchall()]
        async with db.execute(
            "SELECT * FROM tasks WHERE assignee_id=? AND status NOT IN ('done','cancelled') ORDER BY deadline",
            (user_id,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_all_tasks_with_assignee(status_filter=None, category_filter=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        where = []
        params = []
        if status_filter and status_filter != "all":
            where.append("t.status=?")
            params.append(status_filter)
        if category_filter and category_filter != "all":
            where.append("t.category=?")
            params.append(category_filter)
        w = ("WHERE " + " AND ".join(where)) if where else ""
        async with db.execute(
            f"SELECT t.*,u.full_name as assignee_name,u.position as assignee_position "
            f"FROM tasks t LEFT JOIN users u ON t.assignee_id=u.id {w} ORDER BY t.deadline",
            params
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_tasks_by_assignee_grouped():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT u.id,u.full_name,u.position,"
            "COUNT(t.id) as total,"
            "SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) as done,"
            "SUM(CASE WHEN t.status='in_progress' THEN 1 ELSE 0 END) as in_progress,"
            "SUM(CASE WHEN t.status='new' THEN 1 ELSE 0 END) as new_cnt,"
            "SUM(CASE WHEN t.status='cancelled' THEN 1 ELSE 0 END) as cancelled,"
            "SUM(CASE WHEN t.status NOT IN ('done','cancelled') AND t.deadline < date('now') THEN 1 ELSE 0 END) as overdue "
            "FROM users u LEFT JOIN tasks t ON u.id=t.assignee_id "
            "WHERE u.is_active=1 GROUP BY u.id ORDER BY u.full_name"
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_employee_tasks_detail(assignee_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tasks WHERE assignee_id=? ORDER BY "
            "CASE status WHEN 'in_progress' THEN 1 WHEN 'new' THEN 2 "
            "WHEN 'review' THEN 3 WHEN 'done' THEN 4 ELSE 5 END, deadline",
            (assignee_id,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def update_task_status(task_id, status, cancel_reason=None, user_id=None, old_status=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    done_at = now if status == "done" else None
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET status=?,cancel_reason=COALESCE(?,cancel_reason),"
            "updated_at=?,done_at=COALESCE(?,done_at) WHERE id=?",
            (status, cancel_reason, now, done_at, task_id)
        )
        if user_id:
            await db.execute(
                "INSERT INTO task_logs (task_id,user_id,action,old_value,new_value) VALUES (?,?,'status_changed',?,?)",
                (task_id, user_id, old_status, status)
            )
        await db.commit()

async def update_task_progress(task_id, pct, user_id=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT progress_pct FROM tasks WHERE id=?", (task_id,)) as c:
            row = await c.fetchone()
            old_pct = row[0] if row else 0
        await db.execute("UPDATE tasks SET progress_pct=?,updated_at=? WHERE id=?", (pct, now, task_id))
        if user_id:
            await db.execute(
                "INSERT INTO task_logs (task_id,user_id,action,old_value,new_value) VALUES (?,?,'progress_updated',?,?)",
                (task_id, user_id, str(old_pct), str(pct))
            )
        await db.commit()

async def confirm_task(task_id, user_id=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET confirmed_at=?,status=CASE WHEN status='new' THEN 'in_progress' ELSE status END WHERE id=?",
            (now, task_id)
        )
        if user_id:
            await db.execute(
                "INSERT INTO task_logs (task_id,user_id,action,old_value,new_value) VALUES (?,?,'confirmed','new','in_progress')",
                (task_id, user_id)
            )
        await db.commit()

async def increment_confirm_sent(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET confirm_sent_count=confirm_sent_count+1 WHERE id=?", (task_id,)
        )
        await db.commit()

async def get_unconfirmed_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT t.*,u.full_name,u.telegram_id,u.lang FROM tasks t "
            "JOIN users u ON t.assignee_id=u.id "
            "WHERE t.confirmed_at IS NULL AND t.status NOT IN ('done','cancelled') AND u.is_active=1"
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_unconfirmed_tasks_admin():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT t.*,u.full_name as assignee_name,u.telegram_id,u.lang "
            "FROM tasks t JOIN users u ON t.assignee_id=u.id "
            "WHERE t.confirmed_at IS NULL AND t.status NOT IN ('done','cancelled') ORDER BY t.created_at"
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_tasks_near_deadline(days):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        target = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
        async with db.execute(
            "SELECT t.*,u.full_name,u.telegram_id,u.lang FROM tasks t "
            "JOIN users u ON t.assignee_id=u.id "
            "WHERE t.deadline=? AND t.status NOT IN ('done','cancelled') AND u.is_active=1",
            (target,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_overdue_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        today = datetime.date.today().isoformat()
        async with db.execute(
            "SELECT t.*,u.full_name,u.telegram_id,u.lang FROM tasks t "
            "JOIN users u ON t.assignee_id=u.id "
            "WHERE t.deadline < ? AND t.status NOT IN ('done','cancelled') AND u.is_active=1",
            (today,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_user_tasks_for_digest(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tasks WHERE assignee_id=? AND status NOT IN ('done','cancelled') ORDER BY deadline",
            (user_id,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_tasks_with_custom_reminder():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT t.*,u.full_name,u.telegram_id,u.lang FROM tasks t "
            "JOIN users u ON t.assignee_id=u.id "
            "WHERE t.reminder_days > 0 AND t.status NOT IN ('done','cancelled') AND u.is_active=1"
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_employee_monthly_report(user_id, month, year):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tasks WHERE assignee_id=? AND strftime('%m',created_at)=? AND strftime('%Y',created_at)=? ORDER BY status,deadline",
            (user_id, f"{month:02d}", str(year))
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_weekly_stats(from_date, to_date):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT u.id,u.full_name,u.position,"
            "COUNT(t.id) as total,"
            "SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) as done,"
            "SUM(CASE WHEN t.status='cancelled' THEN 1 ELSE 0 END) as cancelled,"
            "SUM(CASE WHEN t.status NOT IN ('done','cancelled') AND t.deadline < date('now') THEN 1 ELSE 0 END) as overdue "
            "FROM users u LEFT JOIN tasks t ON u.id=t.assignee_id "
            "AND t.created_at >= ? AND t.created_at <= ? "
            "WHERE u.is_active=1 GROUP BY u.id ORDER BY done DESC",
            (from_date, to_date)
        ) as c:
            return [_row(r) for r in await c.fetchall()]


# ─── TASK FILES ─────────────────────────────────────────────────

async def save_task_file(task_id, user_id, file_id, file_type="document", caption=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO task_files (task_id,user_id,file_id,file_type,caption) VALUES (?,?,?,?,?)",
            (task_id, user_id, file_id, file_type, caption)
        )
        await db.commit()

async def get_task_files(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT tf.*,u.full_name FROM task_files tf "
            "LEFT JOIN users u ON tf.user_id=u.id WHERE tf.task_id=? ORDER BY tf.created_at",
            (task_id,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]


# ─── TASK COMMENTS ──────────────────────────────────────────────

async def add_comment(task_id, user_id, text):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO task_comments (task_id,user_id,text) VALUES (?,?,?)",
            (task_id, user_id, text)
        )
        await db.commit()
        return cur.lastrowid

async def get_comments(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT tc.*,u.full_name FROM task_comments tc "
            "LEFT JOIN users u ON tc.user_id=u.id WHERE tc.task_id=? ORDER BY tc.created_at",
            (task_id,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]


# ─── PLANS ──────────────────────────────────────────────────────

async def create_plan(title, description, category, month, year, target_count, created_by):
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO plans (title,description,category,month,year,target_count,created_by) VALUES (?,?,?,?,?,?,?)",
            (title, description, category, month, year, target_count, created_by)
        )
        await db.commit()
        return c.lastrowid

async def get_plans(month=None, year=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if month and year:
            async with db.execute(
                "SELECT * FROM plans WHERE month=? AND year=? ORDER BY category,title", (month, year)
            ) as c:
                return [_row(r) for r in await c.fetchall()]
        async with db.execute("SELECT * FROM plans ORDER BY year,month,category") as c:
            return [_row(r) for r in await c.fetchall()]

async def update_plan_done(plan_id, done_count):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE plans SET done_count=? WHERE id=?", (done_count, plan_id))
        await db.commit()


# ─── MEETINGS ───────────────────────────────────────────────────

async def create_meeting(title, description, meeting_date, created_by, decisions=""):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO meetings (title,description,decisions,meeting_date,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
            (title, description, decisions, meeting_date, created_by, now, now)
        )
        await db.commit()
        return c.lastrowid

async def update_meeting(meeting_id, title=None, description=None, decisions=None, meeting_date=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,)) as c:
            m = _row(await c.fetchone())
        if not m:
            return
        await db.execute(
            "UPDATE meetings SET title=?,description=?,decisions=?,meeting_date=?,updated_at=? WHERE id=?",
            (
                title or m["title"],
                description if description is not None else m["description"],
                decisions if decisions is not None else m["decisions"],
                meeting_date or m["meeting_date"],
                now, meeting_id
            )
        )
        await db.commit()

async def get_meetings(limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT m.*,u.full_name as creator_name FROM meetings m "
            "LEFT JOIN users u ON m.created_by=u.id ORDER BY m.meeting_date DESC LIMIT ?", (limit,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_meeting(meeting_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT m.*,u.full_name as creator_name FROM meetings m "
            "LEFT JOIN users u ON m.created_by=u.id WHERE m.id=?", (meeting_id,)
        ) as c:
            return _row(await c.fetchone())

async def get_meeting_tasks(meeting_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT t.*,u.full_name as assignee_name FROM tasks t "
            "JOIN meeting_tasks mt ON t.id=mt.task_id "
            "LEFT JOIN users u ON t.assignee_id=u.id WHERE mt.meeting_id=?", (meeting_id,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]

async def link_task_to_meeting(meeting_id, task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO meeting_tasks (meeting_id,task_id) VALUES (?,?)", (meeting_id, task_id)
        )
        await db.commit()

async def delete_meeting(meeting_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM meeting_tasks WHERE meeting_id=?", (meeting_id,))
        await db.execute("DELETE FROM meetings WHERE id=?", (meeting_id,))
        await db.commit()


# ─── STATISTICS ─────────────────────────────────────────────────

async def get_monthly_stats(month, year):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        mm, yy = f"{month:02d}", str(year)
        async with db.execute(
            "SELECT status,COUNT(*) as cnt FROM tasks WHERE strftime('%m',created_at)=? AND strftime('%Y',created_at)=? GROUP BY status",
            (mm, yy)
        ) as c:
            status_stats = [_row(r) for r in await c.fetchall()]
        async with db.execute(
            "SELECT u.id,u.full_name,u.telegram_id,u.position,"
            "COUNT(t.id) as total,"
            "SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) as done,"
            "SUM(CASE WHEN t.status='cancelled' THEN 1 ELSE 0 END) as cancelled,"
            "SUM(CASE WHEN t.status NOT IN ('done','cancelled') AND t.deadline < date('now') THEN 1 ELSE 0 END) as overdue,"
            "AVG(t.progress_pct) as avg_progress "
            "FROM users u LEFT JOIN tasks t ON u.id=t.assignee_id "
            "AND strftime('%m',t.created_at)=? AND strftime('%Y',t.created_at)=? "
            "WHERE u.is_active=1 GROUP BY u.id ORDER BY done DESC",
            (mm, yy)
        ) as c:
            user_stats = [_row(r) for r in await c.fetchall()]
        async with db.execute("SELECT * FROM plans WHERE month=? AND year=?", (month, year)) as c:
            plans = [_row(r) for r in await c.fetchall()]
        return status_stats, user_stats, plans


# ─── REMINDERS ──────────────────────────────────────────────────

async def get_all_time_leaderboard():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT u.id,u.full_name,u.position,"
            "COUNT(t.id) as total,"
            "SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) as done,"
            "SUM(CASE WHEN t.status='in_progress' THEN 1 ELSE 0 END) as in_progress,"
            "SUM(CASE WHEN t.status='cancelled' THEN 1 ELSE 0 END) as cancelled,"
            "SUM(CASE WHEN t.status NOT IN ('done','cancelled') AND t.deadline < date('now') THEN 1 ELSE 0 END) as overdue,"
            "AVG(CASE WHEN t.status='done' THEN t.progress_pct ELSE NULL END) as avg_progress,"
            "COUNT(CASE WHEN t.status='done' AND t.done_at <= t.deadline THEN 1 END) as done_on_time "
            "FROM users u LEFT JOIN tasks t ON u.id=t.assignee_id "
            "WHERE u.is_active=1 GROUP BY u.id ORDER BY done DESC, total DESC"
        ) as c:
            return [_row(r) for r in await c.fetchall()]


async def get_overdue_tasks_admin():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        today = datetime.date.today().isoformat()
        async with db.execute(
            "SELECT t.*,u.full_name as assignee_name,u.telegram_id,u.position "
            "FROM tasks t JOIN users u ON t.assignee_id=u.id "
            "WHERE t.deadline < ? AND t.status NOT IN ('done','cancelled') AND u.is_active=1 "
            "ORDER BY t.deadline",
            (today,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]


async def get_all_tasks_for_export(month=None, year=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if month and year:
            async with db.execute(
                "SELECT t.*,u.full_name as assignee_name,u.position as assignee_position,"
                "cb.full_name as creator_name "
                "FROM tasks t "
                "LEFT JOIN users u ON t.assignee_id=u.id "
                "LEFT JOIN users cb ON t.created_by=cb.id "
                "WHERE strftime('%m',t.created_at)=? AND strftime('%Y',t.created_at)=? "
                "ORDER BY t.status,t.deadline",
                (f"{month:02d}", str(year))
            ) as c:
                return [_row(r) for r in await c.fetchall()]
        async with db.execute(
            "SELECT t.*,u.full_name as assignee_name,u.position as assignee_position,"
            "cb.full_name as creator_name "
            "FROM tasks t "
            "LEFT JOIN users u ON t.assignee_id=u.id "
            "LEFT JOIN users cb ON t.created_by=cb.id "
            "ORDER BY t.created_at DESC"
        ) as c:
            return [_row(r) for r in await c.fetchall()]


async def check_reminder_sent(task_id, rtype):
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id FROM reminders_sent WHERE task_id=? AND type=? AND date(sent_at)=?",
            (task_id, rtype, today)
        ) as c:
            return (await c.fetchone()) is not None

async def mark_reminder_sent(task_id, rtype):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO reminders_sent (task_id,type) VALUES (?,?)", (task_id, rtype))
        await db.commit()


# ─── BUDGET ─────────────────────────────────────────────────────

async def get_budget(month, year):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM budget_settings WHERE month=? AND year=?", (month, year)
        ) as c:
            return _row(await c.fetchone())

async def set_budget(month, year, limit_usd, limit_uzs, limit_rub):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO budget_settings (month,year,limit_usd,limit_uzs,limit_rub,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?) "
            "ON CONFLICT(month,year) DO UPDATE SET "
            "limit_usd=excluded.limit_usd, limit_uzs=excluded.limit_uzs, "
            "limit_rub=excluded.limit_rub, updated_at=excluded.updated_at",
            (month, year, limit_usd, limit_uzs, limit_rub, now, now)
        )
        await db.commit()

async def get_monthly_expense_total(month, year, currency):
    async with aiosqlite.connect(DB_PATH) as db:
        mm, yy = f"{month:02d}", str(year)
        async with db.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses "
            "WHERE currency=? AND status IN ('approved','paid') "
            "AND strftime('%m',created_at)=? AND strftime('%Y',created_at)=?",
            (currency, mm, yy)
        ) as c:
            row = await c.fetchone()
            return float(row[0]) if row else 0.0

async def get_expense_stats(month, year):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        mm, yy = f"{month:02d}", str(year)
        async with db.execute(
            "SELECT status, COUNT(*) as cnt FROM expenses "
            "WHERE strftime('%m',created_at)=? AND strftime('%Y',created_at)=? GROUP BY status",
            (mm, yy)
        ) as c:
            status_counts = {r["status"]: r["cnt"] for r in await c.fetchall()}
        currency_totals = {}
        for cur in ("USD", "UZS", "RUB"):
            async with db.execute(
                "SELECT COALESCE(SUM(amount),0) FROM expenses "
                "WHERE currency=? AND status IN ('approved','paid') "
                "AND strftime('%m',created_at)=? AND strftime('%Y',created_at)=?",
                (cur, mm, yy)
            ) as c:
                row = await c.fetchone()
                currency_totals[cur] = float(row[0]) if row else 0.0
        async with db.execute(
            "SELECT name, SUM(amount) as total FROM expenses "
            "WHERE status IN ('approved','paid') "
            "AND strftime('%m',created_at)=? AND strftime('%Y',created_at)=? "
            "GROUP BY name ORDER BY total DESC LIMIT 3",
            (mm, yy)
        ) as c:
            top3 = [_row(r) for r in await c.fetchall()]
        prev_month = month - 1 if month > 1 else 12
        prev_year  = year if month > 1 else year - 1
        pmm, pyy = f"{prev_month:02d}", str(prev_year)
        prev_totals = {}
        for cur in ("USD", "UZS", "RUB"):
            async with db.execute(
                "SELECT COALESCE(SUM(amount),0) FROM expenses "
                "WHERE currency=? AND status IN ('approved','paid') "
                "AND strftime('%m',created_at)=? AND strftime('%Y',created_at)=?",
                (cur, pmm, pyy)
            ) as c:
                row = await c.fetchone()
                prev_totals[cur] = float(row[0]) if row else 0.0
        return {
            "status_counts": status_counts,
            "currency_totals": currency_totals,
            "top3": top3,
            "prev_totals": prev_totals,
            "prev_month": prev_month,
            "prev_year": prev_year,
        }


# ─── ACTIVITY LOG ───────────────────────────────────────────────

async def log_activity_db(entity_type, entity_id, action, actor_id,
                          old_value='', new_value=''):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO activity_log (entity_type,entity_id,action,actor_id,old_value,new_value,created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (entity_type, entity_id, action, actor_id, old_value or '', new_value or '', now)
        )
        await db.commit()

async def get_activity_log(entity_type=None, entity_id=None, limit=50, offset=0):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        where = []
        params = []
        if entity_type:
            where.append("al.entity_type=?")
            params.append(entity_type)
        if entity_id is not None:
            where.append("al.entity_id=?")
            params.append(entity_id)
        w = ("WHERE " + " AND ".join(where)) if where else ""
        params += [limit, offset]
        async with db.execute(
            f"SELECT al.*, u.full_name as actor_name, u.username as actor_username "
            f"FROM activity_log al LEFT JOIN users u ON al.actor_id=u.id "
            f"{w} ORDER BY al.created_at DESC LIMIT ? OFFSET ?",
            params
        ) as c:
            return [_row(r) for r in await c.fetchall()]


# ─── DASHBOARD ──────────────────────────────────────────────────

async def get_dashboard_data_admin():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        today = datetime.date.today().isoformat()
        now   = datetime.datetime.now()

        async with db.execute(
            "SELECT COUNT(*) FROM roadmap_tasks WHERE status='pending'"
        ) as c:
            pending_tasks = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM roadmap_tasks WHERE deadline!='' AND deadline IS NOT NULL "
            "AND deadline < ? AND status!='done'", (today,)
        ) as c:
            overdue_tasks = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM expenses WHERE status='pending'"
        ) as c:
            pending_expenses = (await c.fetchone())[0]

        phase_progress = {}
        for phase in ("1-3", "4-6", "7-9", "10-18"):
            async with db.execute(
                "SELECT COUNT(*) as total, SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) as done "
                "FROM roadmap_tasks WHERE phase=?", (phase,)
            ) as c:
                r = _row(await c.fetchone())
                phase_progress[phase] = {"total": r["total"] or 0, "done": r["done"] or 0}

        return {
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "pending_expenses": pending_expenses,
            "phase_progress": phase_progress,
        }

async def get_dashboard_data_employee(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT status, COUNT(*) as cnt FROM tasks WHERE assignee_id=? GROUP BY status",
            (user_id,)
        ) as c:
            task_counts = {r["status"]: r["cnt"] for r in await c.fetchall()}

        async with db.execute(
            "SELECT status, COUNT(*) as cnt FROM expenses WHERE created_by=? GROUP BY status",
            (user_id,)
        ) as c:
            exp_counts = {r["status"]: r["cnt"] for r in await c.fetchall()}

        return {"task_counts": task_counts, "exp_counts": exp_counts}


async def get_overdue_roadmap_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        today = datetime.date.today().isoformat()
        async with db.execute(
            "SELECT * FROM roadmap_tasks WHERE deadline!='' AND deadline IS NOT NULL "
            "AND deadline < ? AND status!='done' ORDER BY deadline",
            (today,)
        ) as c:
            return [_row(r) for r in await c.fetchall()]


ROADMAP_SEED = [
    ("1-3", "Brend strategiyasini ishlab chiqish"),
    ("1-3", "Korporativ uslub (logo, ranglar, shriftlar)"),
    ("1-3", "Veb-sayt yaratish va optimizatsiya"),
    ("1-3", "Ijtimoiy tarmoqlar sahifalarini sozlash"),
    ("1-3", "Asosiy raqobatchilar tahlili"),
    ("1-3", "Maqsadli auditoriyani aniqlash"),
    ("1-3", "Content strategiyasini ishlab chiqish"),
    ("1-3", "Birinchi reklama kampaniyasini ishga tushirish"),
    ("4-6", "SEO optimizatsiyasi"),
    ("4-6", "Email marketing bazasini yaratish"),
    ("4-6", "Hamkorlik va affiliate dasturlarini boshlash"),
    ("4-6", "Mahsulot katalogini yangilash"),
    ("4-6", "Mijozlar fikrlari (reviews) to'plash"),
    ("4-6", "Telegram kanal va bot orqali marketing"),
    ("4-6", "Oylik hisobot va tahlil tizimini joriy etish"),
    ("4-6", "B2B segment uchun alohida strategiya"),
    ("7-9", "Influencer marketing kampaniyasi"),
    ("7-9", "Video kontent ishlab chiqarish"),
    ("7-9", "Loyalty dasturini ishga tushirish"),
    ("7-9", "CRM tizimini joriy etish"),
    ("7-9", "Raqobatchi monitoring avtomatizatsiyasi"),
    ("7-9", "Mavsumiy aksiyalar kalendari"),
    ("7-9", "PR kampaniyasi va media coverage"),
    ("7-9", "Xalqaro bozorga chiqish tadqiqoti"),
    ("10-18", "Xalqaro bozorga kengayish"),
    ("10-18", "Yangi mahsulot liniyasini launchqilish"),
    ("10-18", "Yirik hamkorlik shartnomalarini tuzish"),
    ("10-18", "Brendni kengaytirish strategiyasi"),
    ("10-18", "Avtomatlashtirilgan marketing tizimi"),
    ("10-18", "Yillik hisobot va strategiyani qayta ko'rib chiqish"),
    ("10-18", "Bozor ulushini kengaytirish maqsadi"),
    ("10-18", "Kelajakdagi 3 yillik strategiyani ishlab chiqish"),
]

async def seed_roadmap_tasks():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM roadmap_tasks") as c:
            count = (await c.fetchone())[0]
        if count == 0:
            now = datetime.datetime.now().isoformat()
            for phase, title in ROADMAP_SEED:
                await db.execute(
                    "INSERT INTO roadmap_tasks (phase, title, notes, status, created_at, updated_at) "
                    "VALUES (?, ?, '', 'pending', ?, ?)",
                    (phase, title, now, now)
                )
            await db.commit()


# ─── ROADMAP CRUD ────────────────────────────────────────────────

async def get_roadmap_tasks(phase=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if phase:
            async with db.execute(
                "SELECT * FROM roadmap_tasks WHERE phase=? ORDER BY id", (phase,)
            ) as c:
                return [_row(r) for r in await c.fetchall()]
        async with db.execute("SELECT * FROM roadmap_tasks ORDER BY phase, id") as c:
            return [_row(r) for r in await c.fetchall()]


async def get_roadmap_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM roadmap_tasks WHERE id=?", (task_id,)) as c:
            r = await c.fetchone()
            return _row(r) if r else None


async def create_roadmap_task(phase, title, notes="", created_by=None):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO roadmap_tasks (phase, title, notes, status, created_by, created_at, updated_at) "
            "VALUES (?, ?, ?, 'pending', ?, ?, ?)",
            (phase, title, notes, created_by, now, now)
        )
        await db.commit()
        return cur.lastrowid


async def update_roadmap_task(task_id, **kwargs):
    if not kwargs:
        return
    now = datetime.datetime.now().isoformat()
    kwargs["updated_at"] = now
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [task_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE roadmap_tasks SET {sets} WHERE id=?", vals)
        await db.commit()


async def delete_roadmap_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM roadmap_tasks WHERE id=?", (task_id,))
        await db.commit()


# ─── EXPENSES CRUD ──────────────────────────────────────────────

async def create_expense(name, amount, currency="USD", deadline="", note="",
                         file_id="", file_type="", created_by=None):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO expenses (name, amount, currency, deadline, note, file_id, file_type, "
            "status, created_by, created_at, updated_at) VALUES (?,?,?,?,?,?,?,'pending',?,?,?)",
            (name, amount, currency, deadline, note, file_id, file_type, created_by, now, now)
        )
        await db.commit()
        return cur.lastrowid


async def get_expense(expense_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM expenses WHERE id=?", (expense_id,)) as c:
            r = await c.fetchone()
            return _row(r) if r else None


async def get_expenses(status=None, created_by=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        wheres, params = [], []
        if status:
            wheres.append("status=?"); params.append(status)
        if created_by:
            wheres.append("created_by=?"); params.append(created_by)
        where = ("WHERE " + " AND ".join(wheres)) if wheres else ""
        async with db.execute(f"SELECT * FROM expenses {where} ORDER BY id DESC", params) as c:
            return [_row(r) for r in await c.fetchall()]


async def update_expense(expense_id, **kwargs):
    if not kwargs:
        return
    now = datetime.datetime.now().isoformat()
    kwargs["updated_at"] = now
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [expense_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE expenses SET {sets} WHERE id=?", vals)
        await db.commit()
