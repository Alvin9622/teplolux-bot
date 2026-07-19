TEXTS = {
    "uz": {
        "welcome_new": (
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "🏢 <b>Teplolux</b> — Marketing Monitoring Tizimi\n\n"
            "Tilni tanlang:"
        ),
        "lang_set":    "✅ Til belgilandi.",
        "choose_lang": "🌐 Tilni tanlang:",
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
        "btn_unconfirmed":  "⏳ Tasdiqlanmaganlar",
        "btn_roadmap":      "🗺 Yo'l xaritasi",
        "btn_expenses":     "💰 Marketing xarajatlari",

        # Road Map
        "roadmap_menu":      "🗺 <b>Teplolux Yo'l xaritasi</b>\n\nBosqichni tanlang:",
        "roadmap_phase_1_3":  "📍 1–3 oy — Kirish bosqichi",
        "roadmap_phase_4_6":  "🚀 4–6 oy — Faol bosqich",
        "roadmap_phase_7_9":  "📈 7–9 oy — Kengayish",
        "roadmap_phase_10_18":"🏆 10–18 oy — Barqarorlik",
        "roadmap_add":        "➕ Yangi vazifa qo'shish",
        "roadmap_ask_phase":  "Qaysi bosqichga qo'shmoqchisiz?",
        "roadmap_ask_title":  "Vazifa nomini kiriting:\n\n{cancel}",
        "roadmap_ask_notes":  "Izoh kiriting (yoki /skip):\n\n{cancel}",
        "roadmap_added":      "✅ Vazifa qo'shildi!",
        "roadmap_updated":    "✅ Yangilandi!",
        "roadmap_deleted":    "🗑 O'chirildi!",
        "roadmap_empty":      "Bu bosqichda vazifa yo'q.",
        "roadmap_mark_done":  "✅ Bajarildi deb belgilash",
        "roadmap_mark_pending":"⬜ Bajarilmagan deb belgilash",
        "roadmap_edit_title": "✏️ Nomni o'zgartirish",
        "roadmap_edit_notes": "📝 Izohni o'zgartirish",
        "roadmap_ask_edit_title": "Yangi nomni kiriting:",
        "roadmap_ask_edit_notes": "Yangi izohni kiriting (yoki /skip):",
        "roadmap_confirm_del":"⚠️ O'chirishni tasdiqlaysizmi?\n\n<b>{title}</b>",
        "roadmap_yes_del":    "🗑 Ha, o'chir",

        # Expenses
        "expense_menu":           "💰 <b>Marketing xarajatlari</b>\n\nQuyidagilardan birini tanlang:",
        "expense_add":            "➕ Yangi xarajat",
        "expense_my":             "📋 Mening xarajatlarim",
        "expense_all":            "📊 Barcha xarajatlar",
        "expense_pending_list":   "⏳ Tasdiq kutmoqda",
        "expense_ask_name":       "Xarajat nomini kiriting:\n\n{cancel}",
        "expense_ask_amount":     "Summani kiriting (faqat raqam):\n\n{cancel}",
        "expense_ask_currency":   "Valyutani tanlang:",
        "expense_ask_deadline":   "To'lov muddatini kiriting (KK.OO.YYYY) yoki /skip:\n\n{cancel}",
        "expense_ask_note":       "Izoh kiriting (yoki /skip):\n\n{cancel}",
        "expense_ask_file":       "📎 Chek yoki hujjat yuboring (foto, fayl) yoki /skip:\n\n{cancel}",
        "expense_submitted":      "✅ Xarajat yuborildi! Admin tasdiqlanishini kuting.\n\n💰 <b>{name}</b>\n💵 {amount} {currency}",
        "expense_approved_msg":   "✅ <b>Xarajatingiz tasdiqlandi!</b>\n\n💰 {name}\n💵 {amount} {currency}",
        "expense_rejected_msg":   "❌ <b>Xarajat rad etildi</b>\n\n💰 {name}\n💬 Sabab: {reason}",
        "expense_postponed_msg":  "🔄 <b>Xarajat kechiktirildi</b>\n\n💰 {name}\n📅 Yangi muddat: {date}",
        "expense_ask_reject":     "Rad etish sababini kiriting:",
        "expense_ask_postpone":   "Yangi muddatni kiriting (KK.OO.YYYY):",
        "expense_invalid_amount": "❌ Noto'g'ri summa. Faqat raqam kiriting:",
        "expense_none":           "Xarajatlar topilmadi.",
        "expense_notif_admin":    "💰 <b>Yangi xarajat!</b>\n\n📋 {name}\n💵 {amount} {currency}\n📅 Muddat: {deadline}\n👤 {author}\n💬 {note}",
        "btn_approve":            "✅ Tasdiqlash",
        "btn_reject":             "❌ Rad etish",
        "btn_postpone":           "🔄 Kechiktirish",
        "btn_mark_paid":          "💳 To'landi",
        "exp_status_pending":     "⏳ Kutilmoqda",
        "exp_status_approved":    "✅ Tasdiqlangan",
        "exp_status_rejected":    "❌ Rad etilgan",
        "exp_status_postponed":   "🔄 Kechiktirilgan",
        "exp_status_paid":        "💳 To'langan",

        # Task edit
        "task_edit_header": "✏️ <b>Vazifani tahrirlash</b>\n\n📋 {title}\n👤 {name}\n📅 {deadline}\n\nNimani o'zgartirmoqchisiz?",
        "field_updated":    "✅ O'zgartirildi!",
        "task_deleted":     "🗑 Vazifa o'chirildi.",
        "category_updated": "✅ Kategoriya o'zgartirildi: <b>{val}</b>",
        "priority_updated": "✅ Ustuvorlik o'zgartirildi: <b>{val}</b>",
        "reminder_updated": "✅ Eslatma o'zgartirildi: <b>{val}</b>",
        "deadline_updated": "✅ Muddat: <b>{dl}</b>",
        "date_updated":     "✅ Sana: <b>{dl}</b>",
        "deadline_select":  "📅 <b>Yangi muddatni tanlang:</b>",
        "date_select":      "📅 Yangi sanani tanlang:",
        "session_expired":  "⚠️ Sessiya tugagan. Vazifani qaytadan oching.",

        # Plans
        "plan_update_btn":    "✏️ Bajarilganini yangilash",
        "plan_update_select": "📅 Qaysi rejaning bajarilganini yangilash?",
        "plan_done_ask":      "🎯 Bajarilgan sonini kiriting (0 dan boshlab):\n\n{cancel}",
        "plan_updated":       "✅ Yangilandi! Bajarildi: {done}",

        # Stats/report
        "month_select_stats":  "📊 <b>Oyni tanlang:</b>",
        "month_select_report": "📨 <b>Hisobot uchun oyni tanlang:</b>",

        # Employees
        "tasks_by_employee": "👥 <b>Hodimlar bo'yicha vazifalar:</b>",
        "employees_title":   "👥 <b>Hodimlar</b> — {n} kishi:",
        "employees_short":   "👥 <b>Hodimlar:</b>",
        "role_admin":        "👑 Admin",
        "role_employee":     "👤 Hodim",
        "welcome_added_uz":  "👋 Xush kelibsiz, {name}!\n\nTeplolux monitoring tizimiga qo'shildingiz.\n🎭 {role}\n\n/start yuboring.",

        # Meetings
        "meetings_title":       "🗓 <b>Majlislar</b> — {n} ta:",
        "new_meeting_btn":      "➕ Yangi majlis",
        "meeting_new_title_ask":"📝 Majlis mavzusini kiriting:",
        "meeting_agenda_ask":   "📄 Kun tartibi / muhokama qilinadigan masalalar:\n(yoki /skip)",
        "meeting_date_select":  "📅 <b>Majlis sanasini tanlang:</b>",
        "meeting_created":      "✅ <b>Majlis yaratildi!</b>\n\n📋 {title}\n📅 {dl}\n\nBarcha xabardor qilindi.\n🆔 #{id}",
        "meeting_notif":        "🗓 <b>Yangi majlis!</b>\n\n📋 <b>{title}</b>\n📅 {dl}",
        "meeting_edit_what":    "Nimani o'zgartirish?",
        "meeting_edit_topic":   "📝 Mavzuni o'zgartirish",
        "meeting_edit_agenda":  "📄 Kun tartibini o'zgartirish",
        "meeting_edit_dec":     "✅ Qarorlar qo'shish",
        "meeting_edit_date":    "📅 Sanani o'zgartirish",
        "meeting_tasks_title":  "📋 Vazifalar: {n} ta",
        "meeting_report_title": "📊 <b>Majlis hisoboti</b>",
        "meeting_tasks_status": "<b>Vazifalar holati:</b>",
        "link_task_btn":        "📋 Vazifa biriktirish",
        "task_select":          "📋 Vazifani tanlang:",
        "linked":               "✅ Biriktirildi!",
        "meeting_deleted":      "✅ O'chirildi",
        "meeting_edit_btn":     "✏️ Tahrirlash",
        "meeting_report_btn":   "📊 Hisobot",
        "meeting_delete_btn":   "🗑 O'chirish",
        "enter_new_topic":      "📝 Yangi mavzuni kiriting:",
        "enter_new_agenda":     "📄 Yangi kun tartibini kiriting:",
        "enter_decisions":      "✅ Qabul qilingan qarorlarni kiriting:",

        # Unconfirmed
        "unconfirmed_none":  "✅ Tasdiqlanmagan vazifa yo'q!",
        "unconfirmed_title": "⏳ <b>Tasdiqlanmagan vazifalar</b> — {n} ta:",

        # Excel export
        "excel_select_period": "📥 <b>Excel eksport — oyni tanlang:</b>",
        "excel_all_tasks_btn": "📥 Barcha vazifalar",
        "excel_send_group":    "📤 Guruhga yuborish",
        "excel_sent_group":    "✅ Guruhga yuborildi!",
        "group_not_set":       "❌ Guruh sozlanmagan!",
        "no_tasks_found":      "📭 Vazifa topilmadi.",

        # Comments / files
        "comment_ask":    "💬 Izohingizni yozing:\n\n⬅️ Bekor: /bekor",
        "comment_added":  "✅ Izoh qo'shildi!",
        "file_ask":       "📎 <b>Fayl yuborish</b>\n\nRasm, video yoki hujjat yuboring.\n\n⬅️ Bekor: /bekor",
        "file_uploaded":  "✅ Fayl yuklandi!",
        "files_count":    "📎 {n} ta fayl",

        # Confirm task
        "confirm_accepted":    "✅ Qabul qilindi!",
        "confirm_already":     "✅ Allaqachon qabul qilingan",
        "confirm_not_found":   "Vazifa topilmadi",
        "confirm_notif":       "✅ <b>Vazifa qabul qilindi</b>\n\n📋 {title}\n👤 {name}\n🆔 #{id}",

        # Overdue
        "overdue_none": "✅ Kechikkan vazifa yo'q!",

        # Common
        "no_active_process": "Hozir hech qanday jarayon yo'q.",

        "help_employee": (
            "📖 <b>FOYDALANISH YO'RIQNOMASI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🚀 <b>Buyruqlar</b>\n"
            "/start — asosiy menyu\n"
            "/mytasks — vazifalarim ro'yxati\n"
            "/bekor — joriy amalni bekor qilish\n\n"

            "📋 <b>Mening vazifalarim</b>\n"
            "Sizga biriktirilgan barcha vazifalar ko'rinadi.\n"
            "Holat ikonlari: 🆕 Yangi · 🔄 Jarayonda · 👀 Tekshiruvda · ✅ Bajarildi · ❌ Bekor\n\n"

            "✅ <b>Yangi vazifani tasdiqlash</b>\n"
            "Vazifa kelganda «✅ Qabul qildim» tugmasini bosing.\n"
            "Tasdiqlamasangiz har soatda eslatma keladi!\n\n"

            "🔄 <b>Holatni yangilash</b>\n"
            "Vazifa → Holatni yangilash → kerakli holatni tanlang\n\n"

            "📊 <b>Bajarilish foizini yangilash</b>\n"
            "Vazifa → Foizni yangilash → 0–100 orasida raqam kiriting\n\n"

            "📎 <b>Fayl yuborish</b>\n"
            "Vazifa → Fayl yuborish → rasm/video/hujjat yuboring\n\n"

            "💬 <b>Izoh qoldirish</b>\n"
            "Vazifa → Izoh qoldirish → xabar yuboring\n\n"

            "📊 <b>Dashboard</b>\n"
            "Umumiy ko'rinish: bajarilgan/jarayon/kechikkan vazifalar soni\n\n"

            "💡 <b>G'oyalar va takliflar</b>\n"
            "G'oya, muammo yoki kelajak rejangizni yozing.\n"
            "3 tur: 💡 G'oya · ⚠️ Muammo · 🚀 Kelajak rejasi\n"
            "Admin ko'rib chiqadi va sizga javob beradi.\n\n"

            "🌐 <b>Mini App</b>\n"
            "«Mini App» tugmasini bosing — brauzerda to'liq dashboard:\n"
            "vazifalar, yo'l xarita, xarajatlar, statistika grafiklari.\n\n"

            "🔔 <b>Avtomatik eslatmalar</b>\n"
            "🌅 09:00 — kunlik vazifalar ro'yxati\n"
            "⚠️ Muddatga 3 kun qolganda ogohlantirish\n"
            "🚨 Muddatga 1 kun qolganda ogohlantirish\n"
            "🔴 Muddat o'tib ketganda xabar\n\n"

            "❓ <b>Muammo bo'lsa</b>\n"
            "/bekor yuboring va qaytadan boshlang\n"
            "Yoki adminizga murojaat qiling."
        ),

        "help_admin": (
            "📖 <b>ADMIN YO'RIQNOMASI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "⚙️ <b>Admin paneli</b> — /admin yoki «Admin panel» tugmasi\n\n"

            "➕ <b>Vazifa qo'shish</b>\n"
            "Admin panel → Vazifa qo'shish\n"
            "Nom → Tavsif → Kategoriya → Hodim → Muddat → Ustuvorlik → Eslatma\n\n"

            "📋 <b>Barcha vazifalar</b>\n"
            "Filter: Barchasi / Yangi / Jarayonda / Tekshiruvda / Bajarildi / Bekor\n"
            "Hodimlar bo'yicha — har bir hodim alohida ko'rinadi\n\n"

            "🏆 <b>Reyting (Leaderboard)</b>\n"
            "Barcha vaqt uchun hodimlar reytingi: bajarilgan/umumiy/kechikkan\n\n"

            "🔴 <b>Kechikkan vazifalar</b>\n"
            "Muddati o'tgan barcha vazifalar ro'yxati\n\n"

            "⏳ <b>Tasdiqlanmaganlar</b>\n"
            "Hodim «Qabul qildim» bosamasdan turgan vazifalar + eslatma yuborish\n\n"

            "📥 <b>Excel eksport</b>\n"
            "Oy tanlang → .xlsx fayl yuklab olinadi (barcha vazifalar bilan)\n\n"

            "📊 <b>Oylik statistika</b>\n"
            "Oy tanlang → batafsil hisobot: holat, hodim, kategoriya bo'yicha\n\n"

            "📨 <b>Hisobot yuborish</b>\n"
            "Barcha hodimga oylik natijalar hisobotini yuborish\n\n"

            "👥 <b>Hodimlar boshqaruvi</b>\n"
            "Yangi hodim qo'shish · Bloklash · Admin tayinlash / olib tashlash\n\n"

            "🗓 <b>Majlislar</b>\n"
            "Majlis yaratish, vazifalar biriktirish, hisobot ko'rish\n\n"

            "🗺 <b>Yo'l xarita (Road Map)</b>\n"
            "4 bosqich: 1-3, 4-6, 7-9, 10-18 oy\n"
            "Har bir vazifaga muddat va mas'ul belgilash mumkin\n"
            "Kechikkan vazifalar haqida 09:00 da avtomatik eslatma\n\n"

            "💰 <b>Marketing xarajatlari</b>\n"
            "Hodim xarajat so'rovi yuboradi → admin tasdiqlaydi/rad etadi/kechiktiradi\n"
            "Tasdiqlangan xarajat to'langanda «To'landi» belgilanadi\n"
            "Xarajat ma'lumotlari faqat admin DM ga boradi (guruhga chiqmaydi!)\n\n"

            "💰 <b>Byudjet nazorati</b>\n"
            "Har oy uchun USD/UZS/RUB limitlarini belgilang\n"
            "80% va 100% da avtomatik ogohlantirish keladi\n\n"

            "📋 <b>Faoliyat logi</b>\n"
            "Admin paneli → Faoliyat logi — barcha o'zgarishlar tarixi\n\n"

            "💡 <b>G'oyalar va takliflar</b>\n"
            "Hodimlar yozgan g'oyalar, muammolar, kelajak rejalar\n"
            "Holat o'zgartirish: Ko'rib chiqilmoqda → Qabul qilindi / Rad etildi\n"
            "Izoh qoldirish — muallif xabardor bo'ladi\n\n"

            "📊 <b>Dashboard</b>\n"
            "Umumiy ko'rinish: vazifalar, yo'l xarita bosqichlari, byudjet holati\n\n"

            "🌐 <b>Mini App</b>\n"
            "«Mini App» tugmasi — to'liq veb-dashboard:\n"
            "Grafik statistika · Byudjet tarixi · Leaderboard · Xarajat tahlili\n\n"

            "📊 <b>Google Sheets avtomatik sinxron</b>\n"
            "Barcha vazifalar, izohlar, faollik, yo'l xarita,\n"
            "xarajatlar va g'oyalar Google Sheetsga real vaqtda yoziladi.\n\n"

            "🔔 <b>Rejali eslatmalar</b>\n"
            "🌅 09:00 — kunlik digest (barcha hodimga)\n"
            "⚠️ 09:30 / 15:30 — muddatga yaqin vazifalar\n"
            "🗺 09:00 — kechikkan yo'l xarita vazifalari\n"
            "💰 10:00 — 3+ kun kutayotgan xarajat so'rovlari\n"
            "📅 1-kuni 10:00 — o'tgan oylik hisobot\n"
            "📆 Dushanba 09:00 — haftalik hisobot"
        ),

        # Budget
        "btn_budget":       "💰 Byudjet nazorati",
        "budget_menu":      "📊 <b>Oylik byudjet holati</b>",
        "budget_set":       "💾 Limit belgilash",
        "budget_ask_usd":   "💵 USD limiti kiriting (0 = cheksiz):",
        "budget_ask_uzs":   "🇺🇿 UZS limiti kiriting (0 = cheksiz):",
        "budget_ask_rub":   "🇷🇺 RUB limiti kiriting (0 = cheksiz):",
        "budget_saved":     "✅ Byudjet limiti saqlandi!",
        "budget_alert_80":  "⚠️ <b>Byudjet ogohlantirishI!</b>\n{currency} byudjeti 80% dan oshdi: {spent} / {limit}",
        "budget_alert_100": "🚨 <b>Byudjet limiti oshdi!</b>\n{currency}: {spent} / {limit}",
        # Dashboard
        "btn_dashboard":    "📊 Dashboard",
        "dashboard_title":  "📊 <b>Dashboard</b>",
        "dashboard_refresh":"🔄 Yangilash",
        "btn_miniapp":      "🌐 Mini App",
        "miniapp_info": (
            "🌐 <b>Telegram Mini App</b>\n\n"
            "Bu funksiya tez orada ishga tushadi!\n\n"
            "Mini App orqali siz:\n"
            "• Barcha vazifalarni vizual jadvalda ko'rasiz\n"
            "• Xarajatlar statistikasini grafikda ko'rasiz\n"
            "• Yo'l xaritasini interaktiv tarzda boshqarasiz\n\n"
            "⏳ Ishlab chiqilmoqda..."
        ),
        # Activity log
        "btn_activity":     "📋 Faoliyat logi",
        "activity_log_title":"📋 <b>Faoliyat logi</b>",
        "activity_empty":   "Hech qanday faoliyat yo'q.",
        # Roadmap deadline/assignee
        "roadmap_ask_deadline":"📅 Muddat kiriting (KK.OO.YYYY) yoki /skip:",
        "roadmap_ask_assignee":"👤 Mas'ul hodim ismini kiriting yoki /skip:",
        "roadmap_edit_deadline":"📅 Muddat o'zgartirish",
        "roadmap_edit_assignee":"👤 Mas'ul o'zgartirish",
        # Expense stats
        "exp_stats_title":  "📈 <b>Xarajat statistikasi</b>",
        "btn_exp_stats":    "📈 Statistika",

        # Ideas
        "btn_ideas":            "💡 G'oyalar va takliflar",
        "ideas_menu_title":     "💡 <b>G'oyalar va takliflar</b>\n\nBu bo'limda xohlagan taklifingiz, muammolaringiz yoki kelajakdagi g'oyalaringizni yozishingiz mumkin.",
        "ideas_choose_type":    "📌 Qaysi turda yozmoqchisiz?",
        "idea_type_idea":       "💡 G'oya / taklif",
        "idea_type_problem":    "⚠️ Muammo",
        "idea_type_future":     "🚀 Kelajak rejasi",
        "ideas_ask_text":       "✏️ Fikringizni yozing:\n\n<i>Imkon qadar batafsil yozing</i>",
        "ideas_saved":          "✅ Fikringiz qabul qilindi! Rahmat 🙏\n\nAdmin tez orada ko'rib chiqadi.",
        "ideas_list_title":     "💡 <b>G'oyalar ro'yxati</b>",
        "ideas_my_title":       "💡 <b>Mening g'oyalarim</b>",
        "ideas_empty":          "Hozircha g'oya yo'q.",
        "ideas_view_title":     "💡 <b>G'oya #{id}</b>",
        "ideas_status_new":     "🆕 Yangi",
        "ideas_status_review":  "👀 Ko'rib chiqilmoqda",
        "ideas_status_accepted":"✅ Qabul qilindi",
        "ideas_status_rejected":"❌ Rad etildi",
        "ideas_admin_note_ask": "📝 Admin izohi (yoki /skip):",
        "ideas_admin_note_saved":"✅ Izoh saqlandi.",
        "idea_type_label_idea":   "💡 G'oya",
        "idea_type_label_problem":"⚠️ Muammo",
        "idea_type_label_future": "🚀 Kelajak",

        # Work Plans
        "btn_workplan":         "📋 Ish rejalari",
        "btn_my_workplan":      "📋 Mening rejam",
        "wp_menu_title":        "📋 <b>Ish rejalari</b>",
        "wp_templates_title":   "📋 <b>Shablonlar</b>",
        "wp_no_templates":      "Shablon yo'q. Yangi shablon yarating.",
        "wp_template_new":      "➕ Yangi shablon",
        "wp_ask_title":         "📝 Reja nomi (masalan: SMM Oylik reja):",
        "wp_ask_position":      "💼 Bu reja qaysi lavozim uchun?\n(masalan: SMM menejer, Savdo menejer, Mobilograf)",
        "wp_ask_period":        "📅 Davr turini tanlang:",
        "wp_period_monthly":    "🗓 Oylik",
        "wp_period_weekly":     "📆 Haftalik",
        "wp_ask_item_title":    "✏️ Band nomi kiriting:\n(masalan: Instagram post, Mijoz qo'ng'irog'i)",
        "wp_ask_item_target":   "🎯 Maqsad soni kiriting (masalan: 20):",
        "wp_ask_item_unit":     "📏 O'lchov birligi (masalan: ta, marta, dona) yoki /skip:",
        "wp_item_added":        "✅ Band qo'shildi! Yana qo'shish uchun yuboring yoki /done:",
        "wp_template_saved":    "✅ Shablon saqlandi! Endi hodimga tayinlang.",
        "wp_assign_title":      "👤 Qaysi hodimga tayinlansin?",
        "wp_ask_month":         "📅 Qaysi oy uchun? (masalan: 7 yoki 12):",
        "wp_assigned":          "✅ Reja tayinlandi!",
        "wp_my_plan_empty":     "📭 Joriy oy uchun reja yo'q.\nAdmin hali tayinlamagan.",
        "wp_plan_title":        "📋 <b>{title}</b>\n📅 {month}/{year}\n\nBajarilish: {pct}%\n",
        "wp_item_done":         "✅ Yangilandi! {done}/{target} {unit}",
        "wp_ask_done_count":    "🔢 Nechta bajardingiz? (0-{target}):",
        "wp_all_plans":         "📋 Barcha hodimlar rejalari",
        # KPI
        "btn_kpi":              "📊 KPI",
        "btn_my_kpi":           "📊 Mening KPI",
        "kpi_menu_title":       "📊 <b>KPI boshqaruvi</b>",
        "kpi_my_title":         "📊 <b>Mening KPI natijalarim</b>",
        "kpi_no_targets":       "KPI maqsadlar belgilanmagan.",
        "kpi_ask_metric":       "📌 KPI ko'rsatkich nomi:\n(masalan: Postlar soni, Sotuvlar USD, Yangi mijozlar)",
        "kpi_ask_target":       "🎯 Maqsad qiymat kiriting (masalan: 30):",
        "kpi_ask_unit":         "📏 Birlik (masalan: ta, USD, dona) yoki /skip:",
        "kpi_metric_added":     "✅ Ko'rsatkich qo'shildi! Yana qo'shish uchun davom eting yoki /done:",
        "kpi_saved":            "✅ KPI maqsadlar saqlandi!",
        "kpi_ask_actual":       "🔢 Hozirgi natijani kiriting ({unit}):",
        "kpi_updated":          "✅ KPI yangilandi! {actual}/{target} {unit} ({pct}%)",
        # Content Calendar
        "btn_content":          "📅 Kontent kalendar",
        "content_menu_title":   "📅 <b>Kontent kalendar</b>",
        "content_ask_date":     "📅 Sana kiriting (KK.OO.YYYY):",
        "content_ask_platform": "📱 Platforma tanlang:",
        "content_ask_type":     "🎬 Kontent turi tanlang:",
        "content_ask_title":    "✏️ Kontent nomi/mavzusi:",
        "content_ask_note":     "📝 Qo'shimcha izoh (ixtiyoriy) yoki /skip:",
        "content_saved":        "✅ Kontent rejaga qo'shildi!",
        "content_empty":        "Bu haftada kontent yo'q.",
        "content_week_title":   "📅 <b>Haftalik kontent rejasi</b>",
        "content_done":         "✅ Bajarildi deb belgilandi!",
        "content_failed":       "❌ Bajarilmadi deb belgilandi.",

        # Time management
        "btn_time":     "⏱ Vaqt boshqaruvi",
        # QR code
        "btn_qr":       "🔳 QR kod yasash",
        "qr_ask_input": "🔳 <b>QR kod generatori</b>\n\nHavola yoki matn yuboring — men uni QR kod (PNG) qilib qaytaraman.\n\n<i>Masalan: https://teploluxgroup.uz</i>",
        "qr_done":      "✅ <b>QR kod tayyor!</b>\n\n🔗 {data}",
        "qr_again":     "🔁 Yana QR kod yasash uchun havola/matn yuboring yoki menyuga qayting.",
        "qr_invalid":   "❌ Bo'sh xabar. Havola yoki matn yuboring.",
        "qr_too_long":  "❌ Matn juda uzun (maksimal 1500 belgi).",

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
        "lang_set":    "✅ Язык установлен.",
        "choose_lang": "🌐 Выберите язык:",
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
        "btn_unconfirmed":  "⏳ Неподтверждённые",
        "btn_roadmap":      "🗺 Дорожная карта",
        "btn_expenses":     "💰 Маркетинговые расходы",

        # Road Map
        "roadmap_menu":      "🗺 <b>Дорожная карта Teplolux</b>\n\nВыберите этап:",
        "roadmap_phase_1_3":  "📍 1–3 мес — Вход",
        "roadmap_phase_4_6":  "🚀 4–6 мес — Активный этап",
        "roadmap_phase_7_9":  "📈 7–9 мес — Расширение",
        "roadmap_phase_10_18":"🏆 10–18 мес — Стабильность",
        "roadmap_add":        "➕ Добавить задачу",
        "roadmap_ask_phase":  "В какой этап добавить?",
        "roadmap_ask_title":  "Введите название задачи:\n\n{cancel}",
        "roadmap_ask_notes":  "Введите примечание (или /skip):\n\n{cancel}",
        "roadmap_added":      "✅ Задача добавлена!",
        "roadmap_updated":    "✅ Обновлено!",
        "roadmap_deleted":    "🗑 Удалено!",
        "roadmap_empty":      "В этом этапе нет задач.",
        "roadmap_mark_done":  "✅ Отметить выполненным",
        "roadmap_mark_pending":"⬜ Отметить невыполненным",
        "roadmap_edit_title": "✏️ Изменить название",
        "roadmap_edit_notes": "📝 Изменить примечание",
        "roadmap_ask_edit_title": "Введите новое название:",
        "roadmap_ask_edit_notes": "Введите новое примечание (или /skip):",
        "roadmap_confirm_del":"⚠️ Подтвердите удаление?\n\n<b>{title}</b>",
        "roadmap_yes_del":    "🗑 Да, удалить",

        # Expenses
        "expense_menu":           "💰 <b>Маркетинговые расходы</b>\n\nВыберите действие:",
        "expense_add":            "➕ Новый расход",
        "expense_my":             "📋 Мои расходы",
        "expense_all":            "📊 Все расходы",
        "expense_pending_list":   "⏳ Ожидают подтверждения",
        "expense_ask_name":       "Введите название расхода:\n\n{cancel}",
        "expense_ask_amount":     "Введите сумму (только цифры):\n\n{cancel}",
        "expense_ask_currency":   "Выберите валюту:",
        "expense_ask_deadline":   "Введите срок оплаты (ДД.ММ.ГГГГ) или /skip:\n\n{cancel}",
        "expense_ask_note":       "Введите примечание (или /skip):\n\n{cancel}",
        "expense_ask_file":       "📎 Загрузите чек или документ (фото, файл) или /skip:\n\n{cancel}",
        "expense_submitted":      "✅ Расход отправлен! Ожидайте подтверждения.\n\n💰 <b>{name}</b>\n💵 {amount} {currency}",
        "expense_approved_msg":   "✅ <b>Расход подтверждён!</b>\n\n💰 {name}\n💵 {amount} {currency}",
        "expense_rejected_msg":   "❌ <b>Расход отклонён</b>\n\n💰 {name}\n💬 Причина: {reason}",
        "expense_postponed_msg":  "🔄 <b>Расход отложен</b>\n\n💰 {name}\n📅 Новый срок: {date}",
        "expense_ask_reject":     "Введите причину отклонения:",
        "expense_ask_postpone":   "Введите новый срок (ДД.ММ.ГГГГ):",
        "expense_invalid_amount": "❌ Неверная сумма. Введите только цифры:",
        "expense_none":           "Расходы не найдены.",
        "expense_notif_admin":    "💰 <b>Новый расход!</b>\n\n📋 {name}\n💵 {amount} {currency}\n📅 Срок: {deadline}\n👤 {author}\n💬 {note}",
        "btn_approve":            "✅ Подтвердить",
        "btn_reject":             "❌ Отклонить",
        "btn_postpone":           "🔄 Отложить",
        "btn_mark_paid":          "💳 Оплачено",
        "exp_status_pending":     "⏳ Ожидает",
        "exp_status_approved":    "✅ Подтверждён",
        "exp_status_rejected":    "❌ Отклонён",
        "exp_status_postponed":   "🔄 Отложен",
        "exp_status_paid":        "💳 Оплачен",

        # Task edit
        "task_edit_header": "✏️ <b>Редактирование задачи</b>\n\n📋 {title}\n👤 {name}\n📅 {deadline}\n\nЧто изменить?",
        "field_updated":    "✅ Изменено!",
        "task_deleted":     "🗑 Задача удалена.",
        "category_updated": "✅ Категория изменена: <b>{val}</b>",
        "priority_updated": "✅ Приоритет изменён: <b>{val}</b>",
        "reminder_updated": "✅ Напоминание изменено: <b>{val}</b>",
        "deadline_updated": "✅ Срок: <b>{dl}</b>",
        "date_updated":     "✅ Дата: <b>{dl}</b>",
        "deadline_select":  "📅 <b>Выберите новый срок:</b>",
        "date_select":      "📅 Выберите новую дату:",
        "session_expired":  "⚠️ Сессия истекла. Откройте задачу заново.",

        # Plans
        "plan_update_btn":    "✏️ Обновить выполненное",
        "plan_update_select": "📅 Какой план обновить?",
        "plan_done_ask":      "🎯 Введите выполненное количество (от 0):\n\n{cancel}",
        "plan_updated":       "✅ Обновлено! Выполнено: {done}",

        # Stats/report
        "month_select_stats":  "📊 <b>Выберите месяц:</b>",
        "month_select_report": "📨 <b>Выберите месяц для отчёта:</b>",

        # Employees
        "tasks_by_employee": "👥 <b>Задачи по сотрудникам:</b>",
        "employees_title":   "👥 <b>Сотрудники</b> — {n} чел:",
        "employees_short":   "👥 <b>Сотрудники:</b>",
        "role_admin":        "👑 Администратор",
        "role_employee":     "👤 Сотрудник",
        "welcome_added_uz":  "👋 Добро пожаловать, {name}!\n\nВы добавлены в систему Teplolux.\n🎭 {role}\n\n/start",

        # Meetings
        "meetings_title":       "🗓 <b>Совещания</b> — {n} шт:",
        "new_meeting_btn":      "➕ Новое совещание",
        "meeting_new_title_ask":"📝 Введите тему совещания:",
        "meeting_agenda_ask":   "📄 Повестка дня / обсуждаемые вопросы:\n(или /skip)",
        "meeting_date_select":  "📅 <b>Выберите дату совещания:</b>",
        "meeting_created":      "✅ <b>Совещание создано!</b>\n\n📋 {title}\n📅 {dl}\n\nВсе уведомлены.\n🆔 #{id}",
        "meeting_notif":        "🗓 <b>Новое совещание!</b>\n\n📋 <b>{title}</b>\n📅 {dl}",
        "meeting_edit_what":    "Что изменить?",
        "meeting_edit_topic":   "📝 Изменить тему",
        "meeting_edit_agenda":  "📄 Изменить повестку",
        "meeting_edit_dec":     "✅ Добавить решения",
        "meeting_edit_date":    "📅 Изменить дату",
        "meeting_tasks_title":  "📋 Задачи: {n} шт",
        "meeting_report_title": "📊 <b>Отчёт совещания</b>",
        "meeting_tasks_status": "<b>Статус задач:</b>",
        "link_task_btn":        "📋 Прикрепить задачу",
        "task_select":          "📋 Выберите задачу:",
        "linked":               "✅ Прикреплено!",
        "meeting_deleted":      "✅ Удалено",
        "meeting_edit_btn":     "✏️ Редактировать",
        "meeting_report_btn":   "📊 Отчёт",
        "meeting_delete_btn":   "🗑 Удалить",
        "enter_new_topic":      "📝 Введите новую тему:",
        "enter_new_agenda":     "📄 Введите новую повестку:",
        "enter_decisions":      "✅ Введите принятые решения:",

        # Unconfirmed
        "unconfirmed_none":  "✅ Нет неподтверждённых задач!",
        "unconfirmed_title": "⏳ <b>Неподтверждённые задачи</b> — {n} шт:",

        # Excel export
        "excel_select_period": "📥 <b>Экспорт Excel — выберите период:</b>",
        "excel_all_tasks_btn": "📥 Все задачи",
        "excel_send_group":    "📤 Отправить в группу",
        "excel_sent_group":    "✅ Отправлено в группу!",
        "group_not_set":       "❌ Группа не настроена!",
        "no_tasks_found":      "📭 Задачи не найдены.",

        # Comments / files
        "comment_ask":    "💬 Напишите комментарий:\n\n⬅️ Отмена: /bekor",
        "comment_added":  "✅ Комментарий добавлен!",
        "file_ask":       "📎 <b>Загрузить файл</b>\n\nОтправьте фото, видео или документ.\n\n⬅️ Отмена: /bekor",
        "file_uploaded":  "✅ Файл загружен!",
        "files_count":    "📎 {n} файл(ов)",

        # Confirm task
        "confirm_accepted":    "✅ Принято!",
        "confirm_already":     "✅ Уже принято",
        "confirm_not_found":   "Задача не найдена",
        "confirm_notif":       "✅ <b>Задача принята</b>\n\n📋 {title}\n👤 {name}\n🆔 #{id}",

        # Overdue
        "overdue_none": "✅ Просроченных задач нет!",

        # Common
        "no_active_process": "Нет активного процесса.",

        "help_employee": (
            "📖 <b>РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "🚀 <b>Команды</b>\n"
            "/start — главное меню\n"
            "/mytasks — список моих задач\n"
            "/bekor — отменить текущее действие\n\n"

            "📋 <b>Мои задачи</b>\n"
            "Отображаются все задачи, назначенные вам.\n"
            "Иконки статусов: 🆕 Новая · 🔄 В процессе · 👀 На проверке · ✅ Выполнена · ❌ Отменена\n\n"

            "✅ <b>Подтверждение задачи</b>\n"
            "При получении новой задачи нажмите «✅ Принял».\n"
            "Без подтверждения будет напоминание каждый час!\n\n"

            "🔄 <b>Обновить статус</b>\n"
            "Задача → Обновить статус → выберите нужный статус\n\n"

            "📊 <b>Обновить процент выполнения</b>\n"
            "Задача → Обновить процент → введите число от 0 до 100\n\n"

            "📎 <b>Прикрепить файл</b>\n"
            "Задача → Загрузить файл → отправьте фото/видео/документ\n\n"

            "💬 <b>Оставить комментарий</b>\n"
            "Задача → Комментарий → отправьте сообщение\n\n"

            "📊 <b>Дашборд</b>\n"
            "Общий обзор: выполненные/в процессе/просроченные задачи\n\n"

            "💡 <b>Идеи и предложения</b>\n"
            "Напишите идею, проблему или план на будущее.\n"
            "3 типа: 💡 Идея · ⚠️ Проблема · 🚀 Будущий план\n"
            "Админ рассмотрит и ответит вам.\n\n"

            "🌐 <b>Mini App</b>\n"
            "Кнопка «Mini App» — полный дашборд в браузере:\n"
            "задачи, дорожная карта, расходы, графики статистики.\n\n"

            "🔔 <b>Автоматические напоминания</b>\n"
            "🌅 09:00 — дневной список задач\n"
            "⚠️ За 3 дня до срока — предупреждение\n"
            "🚨 За 1 день до срока — предупреждение\n"
            "🔴 При просрочке — уведомление\n\n"

            "❓ <b>Проблемы?</b>\n"
            "Отправьте /bekor и начните заново\n"
            "Или обратитесь к администратору."
        ),

        "help_admin": (
            "📖 <b>РУКОВОДСТВО АДМИНИСТРАТОРА</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"

            "⚙️ <b>Панель администратора</b> — /admin или кнопка «Панель админа»\n\n"

            "➕ <b>Создать задачу</b>\n"
            "Панель → Создать задачу\n"
            "Название → Описание → Категория → Сотрудник → Срок → Приоритет → Напоминание\n\n"

            "📋 <b>Все задачи</b>\n"
            "Фильтр: Все / Новые / В процессе / На проверке / Выполнены / Отменены\n"
            "По сотрудникам — каждый отдельно\n\n"

            "🏆 <b>Рейтинг (Leaderboard)</b>\n"
            "Рейтинг сотрудников за всё время: выполнено/всего/просрочено\n\n"

            "🔴 <b>Просроченные задачи</b>\n"
            "Список всех задач с истёкшим сроком\n\n"

            "⏳ <b>Неподтверждённые</b>\n"
            "Задачи, где сотрудник не нажал «Принял» + отправить напоминание\n\n"

            "📥 <b>Экспорт Excel</b>\n"
            "Выберите месяц → скачать .xlsx (все задачи с деталями)\n\n"

            "📊 <b>Статистика по месяцам</b>\n"
            "Выберите месяц → подробный отчёт: по статусам, сотрудникам, категориям\n\n"

            "📨 <b>Отправить отчёт</b>\n"
            "Отправить итоги месяца всем сотрудникам\n\n"

            "👥 <b>Управление сотрудниками</b>\n"
            "Добавить · Заблокировать · Назначить/снять админа\n\n"

            "🗓 <b>Совещания</b>\n"
            "Создать совещание, прикрепить задачи, просмотреть отчёт\n\n"

            "🗺 <b>Дорожная карта (Road Map)</b>\n"
            "4 этапа: 1-3, 4-6, 7-9, 10-18 месяцев\n"
            "Для каждой задачи: срок и ответственный\n"
            "Автоматическое напоминание о просроченных задачах в 09:00\n\n"

            "💰 <b>Маркетинговые расходы</b>\n"
            "Сотрудник отправляет запрос → админ одобряет/отклоняет/откладывает\n"
            "После оплаты — отмечается «Оплачено»\n"
            "Данные о расходах идут только в DM админа (не в группу!)\n\n"

            "💰 <b>Контроль бюджета</b>\n"
            "Установите лимиты USD/UZS/RUB на каждый месяц\n"
            "Автоматическое предупреждение при 80% и 100% использовании\n\n"

            "📋 <b>Журнал активности</b>\n"
            "Панель → Журнал активности — полная история всех изменений\n\n"

            "💡 <b>Идеи и предложения</b>\n"
            "Идеи, проблемы и будущие планы от сотрудников\n"
            "Смена статуса: На рассмотрении → Принята / Отклонена\n"
            "Оставить комментарий — автор получит уведомление\n\n"

            "📊 <b>Дашборд</b>\n"
            "Общий обзор: задачи, этапы дорожной карты, состояние бюджета\n\n"

            "🌐 <b>Mini App</b>\n"
            "Кнопка «Mini App» — полный веб-дашборд:\n"
            "Графики · История бюджета · Leaderboard · Анализ расходов\n\n"

            "📊 <b>Автосинхронизация с Google Sheets</b>\n"
            "Задачи, комментарии, активность, дорожная карта,\n"
            "расходы и идеи — записываются в Google Sheets в реальном времени.\n\n"

            "🔔 <b>Плановые уведомления</b>\n"
            "🌅 09:00 — дневной дайджест (всем сотрудникам)\n"
            "⚠️ 09:30 / 15:30 — задачи с приближающимся сроком\n"
            "🗺 09:00 — просроченные задачи дорожной карты\n"
            "💰 10:00 — запросы расходов, ожидающие 3+ дня\n"
            "📅 1-го числа 10:00 — отчёт за прошлый месяц\n"
            "📆 Понедельник 09:00 — еженедельный отчёт"
        ),

        # Budget
        "btn_budget":       "💰 Контроль бюджета",
        "budget_menu":      "📊 <b>Состояние месячного бюджета</b>",
        "budget_set":       "💾 Установить лимит",
        "budget_ask_usd":   "💵 Введите лимит USD (0 = без лимита):",
        "budget_ask_uzs":   "🇺🇿 Введите лимит UZS (0 = без лимита):",
        "budget_ask_rub":   "🇷🇺 Введите лимит RUB (0 = без лимита):",
        "budget_saved":     "✅ Лимит бюджета сохранён!",
        "budget_alert_80":  "⚠️ <b>Внимание по бюджету!</b>\n{currency} бюджет превысил 80%: {spent} / {limit}",
        "budget_alert_100": "🚨 <b>Лимит бюджета превышен!</b>\n{currency}: {spent} / {limit}",
        # Dashboard
        "btn_dashboard":    "📊 Дашборд",
        "dashboard_title":  "📊 <b>Дашборд</b>",
        "dashboard_refresh":"🔄 Обновить",
        "btn_miniapp":      "🌐 Mini App",
        "miniapp_info": (
            "🌐 <b>Telegram Mini App</b>\n\n"
            "Эта функция скоро будет запущена!\n\n"
            "Через Mini App вы сможете:\n"
            "• Просматривать все задачи в визуальной таблице\n"
            "• Видеть статистику расходов в графиках\n"
            "• Управлять дорожной картой интерактивно\n\n"
            "⏳ В разработке..."
        ),
        # Activity log
        "btn_activity":     "📋 Журнал активности",
        "activity_log_title":"📋 <b>Журнал активности</b>",
        "activity_empty":   "Активности нет.",
        # Roadmap deadline/assignee
        "roadmap_ask_deadline":"📅 Введите дедлайн (ДД.ММ.ГГГГ) или /skip:",
        "roadmap_ask_assignee":"👤 Введите имя ответственного или /skip:",
        "roadmap_edit_deadline":"📅 Изменить дедлайн",
        "roadmap_edit_assignee":"👤 Изменить ответственного",
        # Expense stats
        "exp_stats_title":  "📈 <b>Статистика расходов</b>",
        "btn_exp_stats":    "📈 Статистика",

        # Ideas
        "btn_ideas":            "💡 Идеи и предложения",
        "ideas_menu_title":     "💡 <b>Идеи и предложения</b>\n\nЗдесь вы можете написать свои предложения, проблемы или идеи для будущего.",
        "ideas_choose_type":    "📌 Выберите тип:",
        "idea_type_idea":       "💡 Идея / предложение",
        "idea_type_problem":    "⚠️ Проблема",
        "idea_type_future":     "🚀 План на будущее",
        "ideas_ask_text":       "✏️ Напишите вашу мысль:\n\n<i>Пишите как можно подробнее</i>",
        "ideas_saved":          "✅ Ваша идея принята! Спасибо 🙏\n\nАдмин скоро рассмотрит её.",
        "ideas_list_title":     "💡 <b>Список идей</b>",
        "ideas_my_title":       "💡 <b>Мои идеи</b>",
        "ideas_empty":          "Пока нет идей.",
        "ideas_view_title":     "💡 <b>Идея #{id}</b>",
        "ideas_status_new":     "🆕 Новая",
        "ideas_status_review":  "👀 На рассмотрении",
        "ideas_status_accepted":"✅ Принята",
        "ideas_status_rejected":"❌ Отклонена",
        "ideas_admin_note_ask": "📝 Комментарий админа (или /skip):",
        "ideas_admin_note_saved":"✅ Комментарий сохранён.",
        "idea_type_label_idea":   "💡 Идея",
        "idea_type_label_problem":"⚠️ Проблема",
        "idea_type_label_future": "🚀 План",

        # Work Plans
        "btn_workplan":         "📋 Рабочие планы",
        "btn_my_workplan":      "📋 Мой план",
        "wp_menu_title":        "📋 <b>Рабочие планы</b>",
        "wp_templates_title":   "📋 <b>Шаблоны</b>",
        "wp_no_templates":      "Шаблонов нет. Создайте новый шаблон.",
        "wp_template_new":      "➕ Новый шаблон",
        "wp_ask_title":         "📝 Название плана (пример: SMM Месячный план):",
        "wp_ask_position":      "💼 Для какой должности?\n(пример: SMM менеджер, Менеджер по продажам, Мобилограф)",
        "wp_ask_period":        "📅 Выберите тип периода:",
        "wp_period_monthly":    "🗓 Ежемесячный",
        "wp_period_weekly":     "📆 Еженедельный",
        "wp_ask_item_title":    "✏️ Название пункта:\n(пример: Пост в Instagram, Звонок клиенту)",
        "wp_ask_item_target":   "🎯 Целевое количество (пример: 20):",
        "wp_ask_item_unit":     "📏 Единица измерения (пример: шт, раз, USD) или /skip:",
        "wp_item_added":        "✅ Пункт добавлен! Добавьте ещё или /done:",
        "wp_template_saved":    "✅ Шаблон сохранён! Теперь назначьте сотруднику.",
        "wp_assign_title":      "👤 Кому назначить?",
        "wp_ask_month":         "📅 На какой месяц? (пример: 7 или 12):",
        "wp_assigned":          "✅ План назначен!",
        "wp_my_plan_empty":     "📭 На этот месяц план не назначен.\nАдмин ещё не создал.",
        "wp_plan_title":        "📋 <b>{title}</b>\n📅 {month}/{year}\n\nВыполнение: {pct}%\n",
        "wp_item_done":         "✅ Обновлено! {done}/{target} {unit}",
        "wp_ask_done_count":    "🔢 Сколько выполнено? (0-{target}):",
        "wp_all_plans":         "📋 Планы всех сотрудников",
        # KPI
        "btn_kpi":              "📊 KPI",
        "btn_my_kpi":           "📊 Мой KPI",
        "kpi_menu_title":       "📊 <b>Управление KPI</b>",
        "kpi_my_title":         "📊 <b>Мои KPI результаты</b>",
        "kpi_no_targets":       "KPI цели не установлены.",
        "kpi_ask_metric":       "📌 Название показателя:\n(пример: Количество постов, Продажи USD, Новые клиенты)",
        "kpi_ask_target":       "🎯 Целевое значение (пример: 30):",
        "kpi_ask_unit":         "📏 Единица (пример: шт, USD, раз) или /skip:",
        "kpi_metric_added":     "✅ Показатель добавлен! Добавьте ещё или /done:",
        "kpi_saved":            "✅ KPI цели сохранены!",
        "kpi_ask_actual":       "🔢 Введите текущий результат ({unit}):",
        "kpi_updated":          "✅ KPI обновлён! {actual}/{target} {unit} ({pct}%)",
        # Content Calendar
        "btn_content":          "📅 Контент-календарь",
        "content_menu_title":   "📅 <b>Контент-календарь</b>",
        "content_ask_date":     "📅 Введите дату (ДД.ММ.ГГГГ):",
        "content_ask_platform": "📱 Выберите платформу:",
        "content_ask_type":     "🎬 Выберите тип контента:",
        "content_ask_title":    "✏️ Название/тема контента:",
        "content_ask_note":     "📝 Дополнительный комментарий (необязательно) или /skip:",
        "content_saved":        "✅ Контент добавлен в план!",
        "content_empty":        "На этой неделе контента нет.",
        "content_week_title":   "📅 <b>Недельный план контента</b>",
        "content_done":         "✅ Отмечено как выполнено!",
        "content_failed":       "❌ Отмечено как не выполнено.",

        # Time management
        "btn_time":     "⏱ Управление временем",
        # QR code
        "btn_qr":       "🔳 Создать QR-код",
        "qr_ask_input": "🔳 <b>Генератор QR-кода</b>\n\nОтправьте ссылку или текст — я верну его в виде QR-кода (PNG).\n\n<i>Например: https://teploluxgroup.uz</i>",
        "qr_done":      "✅ <b>QR-код готов!</b>\n\n🔗 {data}",
        "qr_again":     "🔁 Отправьте ещё ссылку/текст для нового QR-кода или вернитесь в меню.",
        "qr_invalid":   "❌ Пустое сообщение. Отправьте ссылку или текст.",
        "qr_too_long":  "❌ Текст слишком длинный (максимум 1500 символов).",

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
