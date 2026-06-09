TEXTS = {
    "uz": {
        "welcome_new": (
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "🏢 <b>Teplolux</b> — Marketing Monitoring Tizimi\n\n"
            "Tilni tanlang:"
        ),
        "lang_set": "✅ Til belgilandi.",
        "enter_position": (
            "💼 <b>Lavozimingizni kiriting:</b>\n\n"
            "Masalan: Marketing menejer, SMM mutaxassis, Dizayner..."
        ),
        "registration_done": (
            "✅ <b>Ro'yxatdan o'tdingiz!</b>\n\n"
            "👤 {name}\n"
            "💼 {position}\n\n"
            "Asosiy menyuga o'tish uchun /start yuboring."
        ),
        "main_menu": "📋 <b>Asosiy menyu</b>\nSalom, <b>{name}</b>! 👋",
        "not_registered": "⚠️ Siz ro'yxatdan o'tmagansiz.\nIltimos /start yuboring.",
        "no_permission": "❌ Sizda ruxsat yo'q.",
        "no_tasks": "📭 Vazifa topilmadi.",
        "back": "◀️ Orqaga",
        "cancel_action": "❌ Bekor qilish: /bekor",
        "cancelled": "❌ Bekor qilindi.",
        "saved": "✅ Saqlandi!",
        "error": "❌ Xatolik. Qayta urinib ko'ring.",

        # Statuses
        "status_new": "🆕 Yangi",
        "status_in_progress": "🔄 Jarayonda",
        "status_done": "✅ Bajarildi",
        "status_cancelled": "❌ Bekor qilindi",
        "status_review": "👀 Tekshiruvda",

        # Priorities
        "priority_high": "🔴 Yuqori",
        "priority_medium": "🟡 O'rta",
        "priority_low": "🟢 Past",

        # Menu buttons
        "btn_my_tasks": "📋 Mening vazifalarim",
        "btn_my_stats": "📊 Statistikam",
        "btn_admin": "⚙️ Admin panel",
        "btn_lang": "🌐 Til",

        # Admin menu
        "admin_menu": "⚙️ <b>Admin paneli</b>",
        "btn_add_task": "➕ Vazifa qo'shish",
        "btn_add_plan": "📅 Reja qo'shish",
        "btn_all_tasks": "📋 Barcha vazifalar",
        "btn_by_employee": "👥 Hodimlar bo'yicha",
        "btn_all_plans": "📅 Rejalar",
        "btn_stats": "📊 Oylik statistika",
        "btn_users": "👥 Hodimlar",
        "btn_send_report": "📨 Hisobot yuborish",

        # Task creation
        "ask_title": "📝 Vazifa nomini kiriting:\n\n{cancel}",
        "ask_desc": "📄 Tavsifni kiriting (yoki /skip):\n\n{cancel}",
        "ask_category": "📁 Kategoriyani tanlang:\n\n{cancel}",
        "ask_assignee": "👤 Mas'ul hodimni tanlang:\n\n{cancel}",
        "ask_deadline": "📅 Muddatni kiriting (KK.OY.YYYY):\nMasalan: 25.06.2025\n\n{cancel}",
        "ask_priority": "⚡ Ustuvorlikni tanlang:\n\n{cancel}",
        "ask_reminder": "🔔 Eslatma intervalini tanlang:\n\n{cancel}",
        "invalid_date": "❌ Noto'g'ri sana. KK.OY.YYYY formatida kiriting:",
        "invalid_number": "❌ Faqat son kiriting!",
        "task_created": "✅ Vazifa yaratildi!\n\n📋 <b>{title}</b>\n👤 Mas'ul: {name}\n📅 Muddat: {deadline}\n🔔 Eslatma: {reminder}",

        # Plan creation
        "ask_plan_title": "📝 Reja nomini kiriting:\n\n{cancel}",
        "ask_plan_desc": "📄 Tavsif kiriting (yoki /skip):\n\n{cancel}",
        "ask_plan_target": "🎯 Maqsad soni (nechta):\n\n{cancel}",
        "ask_month": "📅 Oyni tanlang:\n\n{cancel}",
        "plan_created": "✅ Reja yaratildi!\n\n📌 <b>{title}</b>\n📅 {month} {year}\n🎯 Maqsad: {target}",

        # Employee task actions
        "ask_status": "🔄 Yangi holatni tanlang:",
        "ask_cancel_reason": "💬 Bekor qilish sababini yozing:\n\n{cancel}",
        "ask_progress": "📊 Bajarilish foizini kiriting (0-100):\n\n{cancel}",
        "status_updated": "✅ Holat yangilandi: {status}",
        "progress_updated": "✅ Foiz yangilandi: {pct}%",
        "invalid_pct": "❌ 0 dan 100 gacha son kiriting!",

        # Notifications
        "notif_new_task": (
            "📌 <b>Yangi vazifa tayinlandi!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📁 {category}\n"
            "📝 {description}\n"
            "📅 Muddat: <b>{deadline}</b>\n"
            "⚡ Ustuvorlik: {priority}\n"
            "🔔 Eslatma: {reminder}\n\n"
            "/mytasks — vazifalarni ko'rish"
        ),
        "notif_3days": (
            "⚠️ <b>3 kun qoldi!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Holat: {status}\n"
            "📊 Bajarildi: {pct}%\n"
            "📅 Muddat: {deadline}\n\n"
            "/mytasks — holatni yangilash"
        ),
        "notif_1day": (
            "🚨 <b>Ertaga muddat!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Holat: {status}\n"
            "📊 Bajarildi: {pct}%\n"
            "📅 Muddat: {deadline}\n\n"
            "/mytasks — holatni yangilash"
        ),
        "notif_overdue": (
            "🔴 <b>Muddat o'tib ketdi!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Holat: {status}\n"
            "📊 Bajarildi: {pct}%\n"
            "📅 Muddat: {deadline}\n\n"
            "Iltimos holatni yangilang: /mytasks"
        ),
        "notif_reminder": (
            "🔔 <b>Vazifa eslatmasi</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Holat: {status}\n"
            "📊 Bajarildi: {pct}%\n"
            "📅 Muddat: {deadline}\n\n"
            "/mytasks — holatni yangilash"
        ),
        "digest_header": "🌅 <b>Xayrli tong, {name}!</b>\nBugungi vazifalaringiz:\n\n",
        "digest_empty": "🌅 <b>Xayrli tong, {name}!</b>\n✅ Bugun aktiv vazifa yo'q!\n",
        "digest_item": "{i}. <b>{title}</b>\n   {status} | 📊{pct}% | 📅{deadline}{extra}\n\n",

        # Reports
        "monthly_report_title": "📊 <b>{name} — {month} {year} oylik hisobot</b>\n",
        "report_sent": "✅ Hisobot barcha hodimlar va adminga yuborildi!",

        # Add user
        "ask_new_user_id": (
            "👤 <b>Yangi hodim qo'shish</b>\n\n"
            "Hodimning Telegram ID raqamini kiriting.\n"
            "ID olish: hodim @userinfobot ga /start yuboring.\n\n{cancel}"
        ),
        "ask_new_user_name": "✅ ID qabul qilindi!\n\n👤 To'liq ismini kiriting (Familiya Ism):\n\n{cancel}",
        "ask_new_user_role": "🎭 Rolini tanlang:",
        "ask_new_user_lang": "🌐 Tilini tanlang:",
        "user_already_exists": "⚠️ Bu foydalanuvchi allaqachon ro'yxatda:\n👤 <b>{name}</b>\n🎭 {role}",
        "user_added": "✅ <b>Hodim qo'shildi!</b>\n\n👤 {name}\n💼 {position}\n🎭 {role}\n\n{notif}",
        "user_notified": "Xabar yuborildi ✅",
        "user_not_notified": "⚠️ Xabar yuborib bo'lmadi (bot bilan muloqot qilmagan)",

        "btn_leaderboard":  "🏆 Reyting",
        "btn_overdue":      "🔴 Kechikkanlar",
        "btn_export_excel": "📥 Excel eksport",

        "help_employee": (
            "📖 <b>FOYDALANISH YO'RIQNOMASI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🚀 <b>Boshlash</b>\n"
            "/start — asosiy menyu\n"
            "/mytasks — vazifalarim\n"
            "/bekor — jarayonni bekor qilish\n\n"

            "📋 <b>Vazifa holatlari</b>\n"
            "🆕 Yangi — hali boshlanmagan\n"
            "🔄 Jarayonda — bajarilmoqda\n"
            "👀 Tekshiruvda — ko'rib chiqilmoqda\n"
            "✅ Bajarildi — tugallangan\n"
            "❌ Bekor — bajarilib bo'lmaydi\n\n"

            "✅ <b>Vazifani tasdiqlash</b>\n"
            "Yangi vazifa kelganda «Qabul qildim» tugmasini bosing.\n"
            "Tasdiqlamasangiz har soatda eslatma keladi!\n\n"

            "🔄 <b>Holatni yangilash</b>\n"
            "Vazifa → «Holatni yangilash» → holatni tanlang\n\n"

            "📊 <b>Foizni yangilash</b>\n"
            "Vazifa → «Foizni yangilash» → 0-100 kiriting\n\n"

            "📎 <b>Fayl yuborish</b>\n"
            "Vazifa → «Fayl yuborish» → rasm/video/hujjat yuboring\n\n"

            "💬 <b>Izoh qoldirish</b>\n"
            "Vazifa → «Izoh qoldirish» → xabar yuboring\n\n"

            "🔔 <b>Avtomatik eslatmalar</b>\n"
            "🌅 09:00 — kunlik vazifalar ro'yhati\n"
            "⚠️ Muddatga 3 kun qolganda\n"
            "🚨 Muddatga 1 kun qolganda\n"
            "🔴 Muddat o'tib ketganda\n\n"

            "❓ <b>Muammo bo'lsa</b>\n"
            "/bekor yuboring va qaytadan boshlang\n"
            "Yoki adminizga murojaat qiling."
        ),

        "help_admin": (
            "📖 <b>ADMIN YO'RIQNOMASI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "⚙️ <b>Admin paneli</b> — /admin\n\n"

            "➕ <b>Vazifa qo'shish</b>\n"
            "Nom → Tavsif → Kategoriya → Hodim → Muddat → Ustuvorlik → Eslatma\n\n"

            "📋 <b>Vazifalar ko'rish</b>\n"
            "Barcha vazifalar — filter bilan\n"
            "Hodimlar bo'yicha — har bir hodim alohida\n\n"

            "🏆 <b>Reyting</b>\n"
            "Barcha vaqt uchun hodimlar reytingi\n\n"

            "🔴 <b>Kechikkanlar</b>\n"
            "Muddati o'tgan vazifalar ro'yhati\n\n"

            "⏳ <b>Tasdiqlanmaganlar</b>\n"
            "Tasdiqlash kutayotgan vazifalar + eslatma yuborish\n\n"

            "📥 <b>Excel eksport</b>\n"
            "Oyni tanlang → .xlsx fayl yuklab olinadi\n\n"

            "📊 <b>Oylik statistika</b>\n"
            "Oy tanlang → batafsil hisobot\n\n"

            "📨 <b>Hisobot yuborish</b>\n"
            "Barcha hodimga oylik hisobot yuborish\n\n"

            "👥 <b>Hodimlar</b>\n"
            "Qo'shish, bloklash, admin qilish\n\n"

            "🗓 <b>Majlislar</b>\n"
            "Yaratish, vazifa biriktirish, hisobot"
        ),

        "categories": [
            "📱 SMM va Kontent",
            "🔍 SEO va Sayt",
            "📢 Reklama (Ads)",
            "🤝 B2B / Hamkorlik",
            "📊 Tahlil va Hisobot",
            "🔧 Texnik",
            "📦 Boshqa",
        ],
        "months": ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
                   "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"],
        "reminders": {
            0: "🔕 Eslatmasiz",
            1: "⏰ Har kuni",
            2: "⏰ Har 2 kunda",
            3: "⏰ Har 3 kunda",
            7: "⏰ Har haftada",
        },
    },

    "ru": {
        "welcome_new": (
            "👋 <b>Добро пожаловать!</b>\n\n"
            "🏢 <b>Teplolux</b> — Система мониторинга\n\n"
            "Выберите язык:"
        ),
        "lang_set": "✅ Язык установлен.",
        "enter_position": (
            "💼 <b>Введите вашу должность:</b>\n\n"
            "Например: Маркетолог, SMM-специалист, Дизайнер..."
        ),
        "registration_done": (
            "✅ <b>Регистрация прошла успешно!</b>\n\n"
            "👤 {name}\n"
            "💼 {position}\n\n"
            "Для перехода в главное меню отправьте /start."
        ),
        "main_menu": "📋 <b>Главное меню</b>\nПривет, <b>{name}</b>! 👋",
        "not_registered": "⚠️ Вы не зарегистрированы.\nОтправьте /start.",
        "no_permission": "❌ У вас нет доступа.",
        "no_tasks": "📭 Задачи не найдены.",
        "back": "◀️ Назад",
        "cancel_action": "❌ Отмена: /bekor",
        "cancelled": "❌ Отменено.",
        "saved": "✅ Сохранено!",
        "error": "❌ Ошибка. Попробуйте снова.",

        "status_new": "🆕 Новая",
        "status_in_progress": "🔄 В процессе",
        "status_done": "✅ Выполнено",
        "status_cancelled": "❌ Отменено",
        "status_review": "👀 На проверке",

        "priority_high": "🔴 Высокий",
        "priority_medium": "🟡 Средний",
        "priority_low": "🟢 Низкий",

        "btn_my_tasks": "📋 Мои задачи",
        "btn_my_stats": "📊 Статистика",
        "btn_admin": "⚙️ Админ панель",
        "btn_lang": "🌐 Язык",

        "admin_menu": "⚙️ <b>Панель администратора</b>",
        "btn_add_task": "➕ Добавить задачу",
        "btn_add_plan": "📅 Добавить план",
        "btn_all_tasks": "📋 Все задачи",
        "btn_by_employee": "👥 По сотрудникам",
        "btn_all_plans": "📅 Планы",
        "btn_stats": "📊 Месячная статистика",
        "btn_users": "👥 Сотрудники",
        "btn_send_report": "📨 Отправить отчёт",

        "ask_title": "📝 Введите название задачи:\n\n{cancel}",
        "ask_desc": "📄 Введите описание (или /skip):\n\n{cancel}",
        "ask_category": "📁 Выберите категорию:\n\n{cancel}",
        "ask_assignee": "👤 Выберите ответственного:\n\n{cancel}",
        "ask_deadline": "📅 Введите срок (ДД.ММ.ГГГГ):\nПример: 25.06.2025\n\n{cancel}",
        "ask_priority": "⚡ Выберите приоритет:\n\n{cancel}",
        "ask_reminder": "🔔 Выберите интервал напоминания:\n\n{cancel}",
        "invalid_date": "❌ Неверный формат. Введите ДД.ММ.ГГГГ:",
        "invalid_number": "❌ Введите только число!",
        "task_created": "✅ Задача создана!\n\n📋 <b>{title}</b>\n👤 Ответственный: {name}\n📅 Срок: {deadline}\n🔔 Напоминание: {reminder}",

        "ask_plan_title": "📝 Введите название плана:\n\n{cancel}",
        "ask_plan_desc": "📄 Описание (или /skip):\n\n{cancel}",
        "ask_plan_target": "🎯 Целевое количество:\n\n{cancel}",
        "ask_month": "📅 Выберите месяц:\n\n{cancel}",
        "plan_created": "✅ План создан!\n\n📌 <b>{title}</b>\n📅 {month} {year}\n🎯 Цель: {target}",

        "ask_status": "🔄 Выберите новый статус:",
        "ask_cancel_reason": "💬 Напишите причину отмены:\n\n{cancel}",
        "ask_progress": "📊 Введите процент выполнения (0-100):\n\n{cancel}",
        "status_updated": "✅ Статус обновлён: {status}",
        "progress_updated": "✅ Прогресс обновлён: {pct}%",
        "invalid_pct": "❌ Введите число от 0 до 100!",

        "notif_new_task": (
            "📌 <b>Назначена новая задача!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📁 {category}\n"
            "📝 {description}\n"
            "📅 Срок: <b>{deadline}</b>\n"
            "⚡ Приоритет: {priority}\n"
            "🔔 Напоминание: {reminder}\n\n"
            "/mytasks — просмотр задач"
        ),
        "notif_3days": (
            "⚠️ <b>Осталось 3 дня!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Статус: {status}\n"
            "📊 Выполнено: {pct}%\n"
            "📅 Срок: {deadline}\n\n"
            "/mytasks — обновить статус"
        ),
        "notif_1day": (
            "🚨 <b>Срок завтра!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Статус: {status}\n"
            "📊 Выполнено: {pct}%\n"
            "📅 Срок: {deadline}\n\n"
            "/mytasks — обновить статус"
        ),
        "notif_overdue": (
            "🔴 <b>Срок просрочен!</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Статус: {status}\n"
            "📊 Выполнено: {pct}%\n"
            "📅 Срок: {deadline}\n\n"
            "Обновите статус: /mytasks"
        ),
        "notif_reminder": (
            "🔔 <b>Напоминание о задаче</b>\n\n"
            "📋 <b>{title}</b>\n"
            "📌 Статус: {status}\n"
            "📊 Выполнено: {pct}%\n"
            "📅 Срок: {deadline}\n\n"
            "/mytasks — обновить статус"
        ),
        "digest_header": "🌅 <b>Доброе утро, {name}!</b>\nВаши задачи на сегодня:\n\n",
        "digest_empty": "🌅 <b>Доброе утро, {name}!</b>\n✅ Активных задач нет!\n",
        "digest_item": "{i}. <b>{title}</b>\n   {status} | 📊{pct}% | 📅{deadline}{extra}\n\n",

        "monthly_report_title": "📊 <b>{name} — {month} {year} отчёт</b>\n",
        "report_sent": "✅ Отчёт отправлен всем сотрудникам и администратору!",

        "ask_new_user_id": (
            "👤 <b>Добавить сотрудника</b>\n\n"
            "Введите Telegram ID сотрудника.\n"
            "ID: пусть отправит /start боту @userinfobot.\n\n{cancel}"
        ),
        "ask_new_user_name": "✅ ID принят!\n\n👤 Введите полное имя (Фамилия Имя):\n\n{cancel}",
        "ask_new_user_role": "🎭 Выберите роль:",
        "ask_new_user_lang": "🌐 Выберите язык:",
        "user_already_exists": "⚠️ Этот пользователь уже зарегистрирован:\n👤 <b>{name}</b>\n🎭 {role}",
        "user_added": "✅ <b>Сотрудник добавлен!</b>\n\n👤 {name}\n💼 {position}\n🎭 {role}\n\n{notif}",
        "user_notified": "Сообщение отправлено ✅",
        "user_not_notified": "⚠️ Не удалось отправить (не начал чат с ботом)",

        "btn_leaderboard":  "🏆 Рейтинг",
        "btn_overdue":      "🔴 Просроченные",
        "btn_export_excel": "📥 Экспорт Excel",

        "help_employee": (
            "📖 <b>РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🚀 <b>Начало работы</b>\n"
            "/start — главное меню\n"
            "/mytasks — мои задачи\n"
            "/bekor — отменить действие\n\n"

            "📋 <b>Статусы задач</b>\n"
            "🆕 Новая — ещё не начата\n"
            "🔄 В процессе — выполняется\n"
            "👀 На проверке — ожидает проверки\n"
            "✅ Выполнена — завершена\n"
            "❌ Отменена — не может быть выполнена\n\n"

            "✅ <b>Подтверждение задачи</b>\n"
            "При получении новой задачи нажмите «Принял».\n"
            "Без подтверждения каждый час будет напоминание!\n\n"

            "🔄 <b>Обновить статус</b>\n"
            "Задача → «Обновить статус» → выберите статус\n\n"

            "📊 <b>Обновить процент</b>\n"
            "Задача → «Обновить процент» → введите 0-100\n\n"

            "📎 <b>Прикрепить файл</b>\n"
            "Задача → «Загрузить файл» → отправьте фото/видео/документ\n\n"

            "💬 <b>Оставить комментарий</b>\n"
            "Задача → «Комментарий» → отправьте сообщение\n\n"

            "🔔 <b>Автоматические напоминания</b>\n"
            "🌅 09:00 — дневной список задач\n"
            "⚠️ За 3 дня до срока\n"
            "🚨 За 1 день до срока\n"
            "🔴 При просрочке\n\n"

            "❓ <b>Проблемы?</b>\n"
            "Отправьте /bekor и начните заново\n"
            "Или обратитесь к администратору."
        ),

        "help_admin": (
            "📖 <b>РУКОВОДСТВО АДМИНИСТРАТОРА</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "⚙️ <b>Панель админа</b> — /admin\n\n"

            "➕ <b>Создать задачу</b>\n"
            "Название → Описание → Категория → Сотрудник → Срок → Приоритет → Напоминание\n\n"

            "📋 <b>Просмотр задач</b>\n"
            "Все задачи — с фильтрацией\n"
            "По сотрудникам — каждый отдельно\n\n"

            "🏆 <b>Рейтинг</b>\n"
            "Рейтинг сотрудников за всё время\n\n"

            "🔴 <b>Просроченные</b>\n"
            "Список задач с истёкшим сроком\n\n"

            "⏳ <b>Неподтверждённые</b>\n"
            "Задачи ожидающие подтверждения + напоминание\n\n"

            "📥 <b>Экспорт Excel</b>\n"
            "Выберите месяц → скачать .xlsx файл\n\n"

            "📊 <b>Статистика</b>\n"
            "Выберите месяц → подробный отчёт\n\n"

            "📨 <b>Отправить отчёт</b>\n"
            "Отправить месячный отчёт всем сотрудникам\n\n"

            "👥 <b>Сотрудники</b>\n"
            "Добавить, заблокировать, назначить админом\n\n"

            "🗓 <b>Совещания</b>\n"
            "Создать, прикрепить задачи, отчёт"
        ),

        "categories": [
            "📱 SMM и Контент",
            "🔍 SEO и Сайт",
            "📢 Реклама (Ads)",
            "🤝 B2B / Партнёрство",
            "📊 Анализ и Отчёт",
            "🔧 Техническое",
            "📦 Прочее",
        ],
        "months": ["Январь","Февраль","Март","Апрель","Май","Июнь",
                   "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"],
        "reminders": {
            0: "🔕 Без напоминаний",
            1: "⏰ Каждый день",
            2: "⏰ Каждые 2 дня",
            3: "⏰ Каждые 3 дня",
            7: "⏰ Каждую неделю",
        },
    }
}


def T(lang: str, key: str, **kw) -> str:
    lang = lang if lang in TEXTS else "uz"
    val = TEXTS[lang].get(key) or TEXTS["uz"].get(key, key)
    if kw:
        try:
            val = val.format(**kw)
        except Exception:
            pass
    return val


def status_txt(lang: str, status: str) -> str:
    return T(lang, "status_" + status)


def priority_txt(lang: str, priority: str) -> str:
    return T(lang, "priority_" + priority)


def reminder_txt(lang: str, days: int) -> str:
    lang = lang if lang in TEXTS else "uz"
    return TEXTS[lang]["reminders"].get(days, f"⏰ Har {days} kunda" if lang == "uz" else f"⏰ Каждые {days} дней")
