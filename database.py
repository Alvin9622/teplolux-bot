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

        CREATE TABLE IF NOT EXISTS ideas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id      INTEGER NOT NULL,
            full_name  TEXT DEFAULT '',
            username   TEXT DEFAULT '',
            role       TEXT DEFAULT 'employee',
            type       TEXT DEFAULT 'idea',
            text       TEXT NOT NULL,
            status     TEXT DEFAULT 'new',
            admin_note TEXT DEFAULT '',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS work_plan_templates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            position    TEXT DEFAULT '',
            period_type TEXT DEFAULT 'monthly',
            created_by  INTEGER,
            created_at  TEXT,
            is_active   INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS work_plan_template_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id  INTEGER NOT NULL,
            title        TEXT NOT NULL,
            target_count INTEGER DEFAULT 1,
            unit         TEXT DEFAULT 'dona',
            order_num    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS work_plans (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            template_id INTEGER,
            title       TEXT NOT NULL,
            period_type TEXT DEFAULT 'monthly',
            month       INTEGER,
            year        INTEGER,
            week_num    INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'active',
            created_by  INTEGER,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS work_plan_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id      INTEGER NOT NULL,
            title        TEXT NOT NULL,
            target_count INTEGER DEFAULT 1,
            done_count   INTEGER DEFAULT 0,
            unit         TEXT DEFAULT 'dona',
            notes        TEXT DEFAULT '',
            status       TEXT DEFAULT 'pending',
            order_num    INTEGER DEFAULT 0,
            updated_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS kpi_targets (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            month        INTEGER NOT NULL,
            year         INTEGER NOT NULL,
            metric_name  TEXT NOT NULL,
            target_value REAL DEFAULT 0,
            actual_value REAL DEFAULT 0,
            unit         TEXT DEFAULT '',
            note         TEXT DEFAULT '',
            created_by   INTEGER,
            created_at   TEXT,
            updated_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS content_calendar (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            plan_date    TEXT NOT NULL,
            platform     TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title        TEXT DEFAULT '',
            status       TEXT DEFAULT 'planned',
            note         TEXT DEFAULT '',
            created_by   INTEGER,
            created_at   TEXT,
            updated_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS time_logs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            task_name        TEXT NOT NULL,
            category         TEXT,
            start_time       TEXT NOT NULL,
            end_time         TEXT,
            duration_seconds INTEGER,
            log_date         TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_plans (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            plan_date  TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, plan_date)
        );

        CREATE TABLE IF NOT EXISTS daily_plan_items (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id  INTEGER NOT NULL,
            position INTEGER NOT NULL,
            text     TEXT NOT NULL,
            is_done  INTEGER DEFAULT 0,
            done_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            task_name       TEXT,
            start_time      TEXT NOT NULL,
            ends_at         TEXT NOT NULL,
            planned_minutes INTEGER DEFAULT 25,
            status          TEXT DEFAULT 'active',
            session_date    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_focus_stats (
            user_id             INTEGER PRIMARY KEY,
            current_streak      INTEGER DEFAULT 0,
            longest_streak      INTEGER DEFAULT 0,
            last_active_date    TEXT,
            total_focus_minutes INTEGER DEFAULT 0,
            total_pomodoros     INTEGER DEFAULT 0,
            focus_points        INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS time_blocks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            block_date TEXT NOT NULL,
            title      TEXT NOT NULL,
            category   TEXT,
            start_time TEXT NOT NULL,
            end_time   TEXT NOT NULL,
            priority   TEXT DEFAULT 'medium',
            reminded   INTEGER DEFAULT 0,
            status     TEXT DEFAULT 'planned'
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


# ─── IDEAS ──────────────────────────────────────────────────────

async def create_idea(tg_id, full_name, username, role, idea_type, text):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO ideas (tg_id,full_name,username,role,type,text,status,created_at) VALUES (?,?,?,?,?,?,?,?)",
            (tg_id, full_name, username or "", role, idea_type, text, "new", now)
        )
        await db.commit()
        return c.lastrowid


async def get_idea(idea_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM ideas WHERE id=?", (idea_id,)) as c:
            r = await c.fetchone()
            return _row(r) if r else None


async def get_ideas(status=None, tg_id=None, idea_type=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        wheres, params = [], []
        if status:
            wheres.append("status=?"); params.append(status)
        if tg_id:
            wheres.append("tg_id=?"); params.append(tg_id)
        if idea_type:
            wheres.append("type=?"); params.append(idea_type)
        where = ("WHERE " + " AND ".join(wheres)) if wheres else ""
        async with db.execute(f"SELECT * FROM ideas {where} ORDER BY id DESC", params) as c:
            return [_row(r) for r in await c.fetchall()]


async def update_idea(idea_id, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [idea_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE ideas SET {sets} WHERE id=?", vals)
        await db.commit()


# ─── WORK PLAN TEMPLATES ─────────────────────────────────────────

async def create_wp_template(title, position, period_type, created_by):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO work_plan_templates (title,position,period_type,created_by,created_at) VALUES (?,?,?,?,?)",
            (title, position, period_type, created_by, now)
        )
        await db.commit()
        return c.lastrowid

async def add_wp_template_item(template_id, title, target_count, unit, order_num):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO work_plan_template_items (template_id,title,target_count,unit,order_num) VALUES (?,?,?,?,?)",
            (template_id, title, target_count, unit, order_num)
        )
        await db.commit()

async def get_wp_templates(position=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if position:
            async with db.execute("SELECT * FROM work_plan_templates WHERE is_active=1 AND position=? ORDER BY id DESC", (position,)) as c:
                return [_row(r) for r in await c.fetchall()]
        async with db.execute("SELECT * FROM work_plan_templates WHERE is_active=1 ORDER BY id DESC") as c:
            return [_row(r) for r in await c.fetchall()]

async def get_wp_template(template_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM work_plan_templates WHERE id=?", (template_id,)) as c:
            return _row(await c.fetchone())

async def get_wp_template_items(template_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM work_plan_template_items WHERE template_id=? ORDER BY order_num", (template_id,)) as c:
            return [_row(r) for r in await c.fetchall()]

async def delete_wp_template(template_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE work_plan_templates SET is_active=0 WHERE id=?", (template_id,))
        await db.commit()


# ─── WORK PLANS ──────────────────────────────────────────────────

async def create_work_plan(user_id, template_id, title, period_type, month, year, week_num, created_by):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO work_plans (user_id,template_id,title,period_type,month,year,week_num,created_by,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (user_id, template_id, title, period_type, month, year, week_num, created_by, now)
        )
        await db.commit()
        return c.lastrowid

async def add_work_plan_item(plan_id, title, target_count, unit, order_num=0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO work_plan_items (plan_id,title,target_count,unit,order_num) VALUES (?,?,?,?,?)",
            (plan_id, title, target_count, unit, order_num)
        )
        await db.commit()

async def get_work_plans(user_id=None, month=None, year=None, status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        wheres, params = [], []
        if user_id:  wheres.append("wp.user_id=?");  params.append(user_id)
        if month:    wheres.append("wp.month=?");     params.append(month)
        if year:     wheres.append("wp.year=?");      params.append(year)
        if status:   wheres.append("wp.status=?");    params.append(status)
        where = ("WHERE " + " AND ".join(wheres)) if wheres else ""
        sql = f"""
            SELECT wp.*, u.full_name as assignee_name
            FROM work_plans wp
            LEFT JOIN users u ON wp.user_id = u.id
            {where} ORDER BY wp.id DESC
        """
        async with db.execute(sql, params) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_work_plan(plan_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT wp.*, u.full_name as assignee_name FROM work_plans wp LEFT JOIN users u ON wp.user_id=u.id WHERE wp.id=?",
            (plan_id,)
        ) as c:
            return _row(await c.fetchone())

async def get_work_plan_items(plan_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM work_plan_items WHERE plan_id=? ORDER BY id", (plan_id,)) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_work_plan_item(item_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM work_plan_items WHERE id=?", (item_id,)) as c:
            return _row(await c.fetchone())

async def update_work_plan_item(item_id, **kwargs):
    now = datetime.datetime.now().isoformat()
    kwargs["updated_at"] = now
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [item_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE work_plan_items SET {sets} WHERE id=?", vals)
        await db.commit()

async def update_work_plan(plan_id, **kwargs):
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [plan_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE work_plans SET {sets} WHERE id=?", vals)
        await db.commit()


# ─── KPI ─────────────────────────────────────────────────────────

async def create_kpi_target(user_id, month, year, metric_name, target_value, unit, created_by, note=""):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO kpi_targets (user_id,month,year,metric_name,target_value,actual_value,unit,note,created_by,created_at,updated_at) VALUES (?,?,?,?,?,0,?,?,?,?,?)",
            (user_id, month, year, metric_name, target_value, unit, note, created_by, now, now)
        )
        await db.commit()
        return c.lastrowid

async def get_kpi_targets(user_id=None, month=None, year=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        wheres, params = [], []
        if user_id: wheres.append("k.user_id=?"); params.append(user_id)
        if month:   wheres.append("k.month=?");   params.append(month)
        if year:    wheres.append("k.year=?");     params.append(year)
        where = ("WHERE " + " AND ".join(wheres)) if wheres else ""
        sql = f"SELECT k.*, u.full_name as user_name FROM kpi_targets k LEFT JOIN users u ON k.user_id=u.id {where} ORDER BY k.id"
        async with db.execute(sql, params) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_kpi_target(kpi_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM kpi_targets WHERE id=?", (kpi_id,)) as c:
            return _row(await c.fetchone())

async def update_kpi_target(kpi_id, **kwargs):
    now = datetime.datetime.now().isoformat()
    kwargs["updated_at"] = now
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [kpi_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE kpi_targets SET {sets} WHERE id=?", vals)
        await db.commit()

async def delete_kpi_target(kpi_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM kpi_targets WHERE id=?", (kpi_id,))
        await db.commit()


# ─── CONTENT CALENDAR ────────────────────────────────────────────

async def create_content_entry(user_id, plan_date, platform, content_type, title, created_by, note=""):
    now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            "INSERT INTO content_calendar (user_id,plan_date,platform,content_type,title,status,note,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (user_id, plan_date, platform, content_type, title, "planned", note, created_by, now, now)
        )
        await db.commit()
        return c.lastrowid

async def get_content_entries(user_id=None, date_from=None, date_to=None, status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        wheres, params = [], []
        if user_id:   wheres.append("c.user_id=?");             params.append(user_id)
        if date_from: wheres.append("c.plan_date>=?");          params.append(date_from)
        if date_to:   wheres.append("c.plan_date<=?");          params.append(date_to)
        if status:    wheres.append("c.status=?");              params.append(status)
        where = ("WHERE " + " AND ".join(wheres)) if wheres else ""
        sql = f"SELECT c.*, u.full_name as user_name FROM content_calendar c LEFT JOIN users u ON c.user_id=u.id {where} ORDER BY c.plan_date, c.id"
        async with db.execute(sql, params) as c:
            return [_row(r) for r in await c.fetchall()]

async def get_content_entry(entry_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM content_calendar WHERE id=?", (entry_id,)) as c:
            return _row(await c.fetchone())

async def update_content_entry(entry_id, **kwargs):
    now = datetime.datetime.now().isoformat()
    kwargs["updated_at"] = now
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [entry_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE content_calendar SET {sets} WHERE id=?", vals)
        await db.commit()

async def delete_content_entry(entry_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM content_calendar WHERE id=?", (entry_id,))
        await db.commit()

async def get_content_stats(user_id, month, year):
    """Oylik kontent statistikasi."""
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    date_from = f"{year}-{month:02d}-01"
    date_to   = f"{year}-{month:02d}-{last_day}"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT status, COUNT(*) as cnt FROM content_calendar WHERE user_id=? AND plan_date BETWEEN ? AND ? GROUP BY status",
            (user_id, date_from, date_to)
        ) as c:
            rows = {r["status"]: r["cnt"] for r in await c.fetchall()}
        async with db.execute(
            "SELECT platform, COUNT(*) as cnt FROM content_calendar WHERE user_id=? AND plan_date BETWEEN ? AND ? AND status='done' GROUP BY platform",
            (user_id, date_from, date_to)
        ) as c:
            by_platform = {r["platform"]: r["cnt"] for r in await c.fetchall()}
    return {"by_status": rows, "by_platform": by_platform}


# ═══════════════════════════════════════════════════════════════
#  TIME MANAGEMENT — vaqt hisobi
# ═══════════════════════════════════════════════════════════════

async def get_active_time_log(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM time_logs WHERE user_id=? AND end_time IS NULL "
            "ORDER BY id DESC LIMIT 1", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def start_time_log(user_id, task, category):
    now = datetime.datetime.now()
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO time_logs (user_id, task_name, category, start_time, log_date) "
            "VALUES (?,?,?,?,?)",
            (user_id, task, category, now.isoformat(), now.strftime("%Y-%m-%d")))
        await conn.commit()


async def stop_time_log(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM time_logs WHERE user_id=? AND end_time IS NULL "
            "ORDER BY id DESC LIMIT 1", (user_id,))
        row = await cur.fetchone()
        if not row:
            return None
        start = datetime.datetime.fromisoformat(row["start_time"])
        end   = datetime.datetime.now()
        dur   = int((end - start).total_seconds())
        await conn.execute(
            "UPDATE time_logs SET end_time=?, duration_seconds=? WHERE id=?",
            (end.isoformat(), dur, row["id"]))
        await conn.commit()
        d = dict(row)
        d["duration_seconds"] = dur
        d["end_time"] = end.isoformat()
        return d


async def today_total_str(user_id):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "SELECT COALESCE(SUM(duration_seconds),0) FROM time_logs "
            "WHERE user_id=? AND log_date=? AND duration_seconds IS NOT NULL",
            (user_id, today))
        (total,) = await cur.fetchone()
    m = total // 60
    h, mm = divmod(m, 60)
    return f"{h} soat {mm} daq" if h else f"{mm} daq"


async def time_by_category_since(user_id, start_date):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "SELECT COALESCE(category,'Boshqa'), COALESCE(SUM(duration_seconds),0) "
            "FROM time_logs WHERE user_id=? AND log_date>=? "
            "AND duration_seconds IS NOT NULL GROUP BY category",
            (user_id, start_date))
        return await cur.fetchall()


# ═══════════════════════════════════════════════════════════════
#  POMODORO
# ═══════════════════════════════════════════════════════════════

async def start_pomodoro(user_id, task, minutes, ends_at):
    now = datetime.datetime.now()
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "INSERT INTO pomodoro_sessions "
            "(user_id, task_name, start_time, ends_at, planned_minutes, status, session_date) "
            "VALUES (?,?,?,?,?, 'active', ?)",
            (user_id, task, now.isoformat(), ends_at.isoformat(),
             minutes, now.strftime("%Y-%m-%d")))
        await conn.commit()
        return cur.lastrowid


async def get_active_pomodoro(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM pomodoro_sessions WHERE user_id=? AND status='active' "
            "ORDER BY id DESC LIMIT 1", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_pomodoro_session(session_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM pomodoro_sessions WHERE id=?", (session_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_active_pomodoros():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM pomodoro_sessions WHERE status='active'")
        return [dict(r) for r in await cur.fetchall()]


async def complete_pomodoro(session_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM pomodoro_sessions WHERE id=?", (session_id,))
        s = await cur.fetchone()
        if not s or s["status"] != "active":
            return
        await conn.execute(
            "UPDATE pomodoro_sessions SET status='completed' WHERE id=?",
            (session_id,))
        await conn.execute(
            "INSERT INTO user_focus_stats "
            "(user_id, total_focus_minutes, total_pomodoros, focus_points) "
            "VALUES (?,?,1,10) "
            "ON CONFLICT(user_id) DO UPDATE SET "
            "total_focus_minutes = total_focus_minutes + ?, "
            "total_pomodoros = total_pomodoros + 1, "
            "focus_points = focus_points + 10",
            (s["user_id"], s["planned_minutes"], s["planned_minutes"]))
        await conn.commit()
    await touch_streak(s["user_id"])


async def cancel_pomodoro(session_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE pomodoro_sessions SET status='cancelled' WHERE id=?",
            (session_id,))
        await conn.commit()


async def count_today_pomodoros(user_id):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "SELECT COUNT(*) FROM pomodoro_sessions "
            "WHERE user_id=? AND session_date=? AND status='completed'",
            (user_id, today))
        (n,) = await cur.fetchone()
        return n


async def count_pomodoros_since(user_id, start_date):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "SELECT COUNT(*) FROM pomodoro_sessions "
            "WHERE user_id=? AND session_date>=? AND status='completed'",
            (user_id, start_date))
        (n,) = await cur.fetchone()
        return n


# ═══════════════════════════════════════════════════════════════
#  KUNLIK REJA (DAILY PLAN / MIT)
# ═══════════════════════════════════════════════════════════════

async def save_daily_plan(user_id, plan_date, items):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT id FROM daily_plans WHERE user_id=? AND plan_date=?",
            (user_id, plan_date))
        row = await cur.fetchone()
        if row:
            plan_id = row["id"]
            await conn.execute(
                "DELETE FROM daily_plan_items WHERE plan_id=?", (plan_id,))
        else:
            cur = await conn.execute(
                "INSERT INTO daily_plans (user_id, plan_date, created_at) "
                "VALUES (?,?,?)",
                (user_id, plan_date, datetime.datetime.now().isoformat()))
            plan_id = cur.lastrowid
        for pos, text in enumerate(items, start=1):
            await conn.execute(
                "INSERT INTO daily_plan_items (plan_id, position, text) "
                "VALUES (?,?,?)", (plan_id, pos, text))
        await conn.commit()


async def get_plan_items(user_id, plan_date):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT i.* FROM daily_plan_items i "
            "JOIN daily_plans p ON p.id=i.plan_id "
            "WHERE p.user_id=? AND p.plan_date=? ORDER BY i.position",
            (user_id, plan_date))
        return [dict(r) for r in await cur.fetchall()]


async def toggle_plan_item(item_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT is_done FROM daily_plan_items WHERE id=?", (item_id,))
        row = await cur.fetchone()
        if not row:
            return False
        new_val = 0 if row["is_done"] else 1
        done_at = datetime.datetime.now().isoformat() if new_val else None
        await conn.execute(
            "UPDATE daily_plan_items SET is_done=?, done_at=? WHERE id=?",
            (new_val, done_at, item_id))
        await conn.commit()
        return bool(new_val)


async def plan_completion_since(user_id, start_date):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(i.is_done),0) "
            "FROM daily_plan_items i JOIN daily_plans p ON p.id=i.plan_id "
            "WHERE p.user_id=? AND p.plan_date>=?", (user_id, start_date))
        total, done = await cur.fetchone()
        return round(done / total * 100) if total else 0


# ═══════════════════════════════════════════════════════════════
#  FOKUS STATISTIKA / STREAK
# ═══════════════════════════════════════════════════════════════

async def get_focus_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM user_focus_stats WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if row:
            return dict(row)
        return {"user_id": user_id, "current_streak": 0, "longest_streak": 0,
                "last_active_date": None, "total_focus_minutes": 0,
                "total_pomodoros": 0, "focus_points": 0}


async def add_focus_points(user_id, points):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO user_focus_stats (user_id, focus_points) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET focus_points = focus_points + ?",
            (user_id, points, points))
        await conn.commit()


async def touch_streak(user_id):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT current_streak, longest_streak, last_active_date "
            "FROM user_focus_stats WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row:
            await conn.execute(
                "INSERT INTO user_focus_stats "
                "(user_id, current_streak, longest_streak, last_active_date) "
                "VALUES (?,1,1,?)", (user_id, today))
            await conn.commit()
            return
        last = row["last_active_date"]
        if last == today:
            return
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        new_streak = row["current_streak"] + 1 if last == yesterday else 1
        longest = max(row["longest_streak"], new_streak)
        await conn.execute(
            "UPDATE user_focus_stats SET current_streak=?, longest_streak=?, "
            "last_active_date=? WHERE user_id=?",
            (new_streak, longest, today, user_id))
        await conn.commit()


async def get_all_employee_ids():
    """Barcha faol foydalanuvchilarning telegram ID lari (eslatmalar uchun)."""
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("SELECT telegram_id FROM users WHERE is_active=1")
        return [r[0] for r in await cur.fetchall()]


# ═══════════════════════════════════════════════════════════════
#  VAQT BLOKLARI (TIME BLOCKING) — Stage 2
# ═══════════════════════════════════════════════════════════════

async def add_time_block(user_id, block_date, title, category, start, end, priority):
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            "INSERT INTO time_blocks "
            "(user_id, block_date, title, category, start_time, end_time, priority) "
            "VALUES (?,?,?,?,?,?,?)",
            (user_id, block_date, title, category, start, end, priority))
        await conn.commit()
        return cur.lastrowid


async def get_time_block(block_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM time_blocks WHERE id=?", (block_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_blocks_for_day(user_id, block_date):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM time_blocks WHERE user_id=? AND block_date=? "
            "ORDER BY start_time", (user_id, block_date))
        return [dict(r) for r in await cur.fetchall()]


async def get_blocks_for_reminder(block_date):
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute(
            "SELECT * FROM time_blocks WHERE block_date=? "
            "AND status='planned' AND reminded=0", (block_date,))
        return [dict(r) for r in await cur.fetchall()]


async def mark_block_reminded(block_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE time_blocks SET reminded=1 WHERE id=?", (block_id,))
        await conn.commit()


async def set_block_status(block_id, status):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("UPDATE time_blocks SET status=? WHERE id=?", (status, block_id))
        await conn.commit()


async def delete_time_block(block_id):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM time_blocks WHERE id=?", (block_id,))
        await conn.commit()


async def get_last_activity(user_id):
    """Barcha modullardan oxirgi faollik vaqtini qaytaradi (aqlli nudge uchun)."""
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute("""
            SELECT MAX(ts) FROM (
                SELECT MAX(COALESCE(end_time, start_time)) AS ts
                    FROM time_logs WHERE user_id=?
                UNION ALL
                SELECT MAX(start_time) FROM pomodoro_sessions WHERE user_id=?
                UNION ALL
                SELECT MAX(i.done_at) FROM daily_plan_items i
                    JOIN daily_plans p ON p.id=i.plan_id WHERE p.user_id=?
            )
        """, (user_id, user_id, user_id))
        (ts,) = await cur.fetchone()
        return datetime.datetime.fromisoformat(ts) if ts else None
