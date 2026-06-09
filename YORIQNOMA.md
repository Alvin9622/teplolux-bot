# 📋 TEPLOLUX BOT — FOYDALANISH YO'RIQNOMASI

---

## 🤖 Bot nima?

**Teplolux Bot** — bu kompaniya ichida vazifalarni boshqarish uchun mo'ljallangan Telegram bot.
Bot orqali:
- Sizga berilgan vazifalarni ko'rasiz
- Vazifalar holatini yangilaysiz
- Fayllar va izohlar yuborasiz
- Oylik statistikangizni ko'rasiz

---

## 🚀 Botdan foydalanishni boshlash

### 1-qadam — Botni toping
Telegram da bot nomini qidiring va `/start` yuboring.

### 2-qadam — Tilni tanlang
`🇺🇿 O'zbek` yoki `🇷🇺 Русский` tugmasini bosing.

### 3-qadam — Lavozimingizni kiriting
Masalan: `Marketing menejer`, `SMM mutaxassis`, `Dizayner`

### 4-qadam — Asosiy menyu
Ro'yxatdan o'tgach, asosiy menyu ochiladi:

```
📋 Mening vazifalarim
📊 Statistikam
🌐 Til
```

---

## 📋 VAZIFALAR BILAN ISHLASH

### Vazifalarni ko'rish
`📋 Mening vazifalarim` tugmasini bosing yoki `/mytasks` yuboring.

Har bir vazifa oldida holat belgisi ko'rsatiladi:
| Belgi | Ma'nosi |
|-------|---------|
| 🆕 | Yangi — hali boshlanmagan |
| 🔄 | Jarayonda — bajarilmoqda |
| 👀 | Tekshiruvda — ko'rib chiqilmoqda |
| ✅ | Bajarildi |
| ❌ | Bekor qilindi |

---

### Vazifani tasdiqlash
Yangi vazifa berilganda sizga xabar keladi:

```
📌 Yangi vazifa tayinlandi!
📋 Vazifa nomi
📅 Muddat: 25.06.2025
⚡ Ustuvorlik: Yuqori
```

**✅ Qabul qildim** tugmasini bosib tasdiqlang.
> ⚠️ Tasdiqlamasangiz, har soatda eslatma keladi!

---

### Vazifa holatini yangilash
1. Vazifani bosing
2. `🔄 Holatni yangilash` tugmasini bosing
3. Yangi holatni tanlang:

| Holat | Qachon tanlaymiz |
|-------|-----------------|
| 🔄 Jarayonda | Ishni boshlaganda |
| 👀 Tekshiruvda | Tugatib, admin ko'rishi kerak bo'lganda |
| ✅ Bajarildi | Ish to'liq tugaganda |
| ❌ Bekor | Bajarib bo'lmaydigan sabablar bo'lganda |

> Bekor qilsangiz — **sababini yozish shart**

---

### Bajarilish foizini yangilash
1. Vazifani bosing
2. `📊 Foizni yangilash` tugmasini bosing
3. 0 dan 100 gacha son kiriting (masalan: `75`)

---

### Fayl yuborish
Vazifaga rasm, video yoki hujjat biriktirish:
1. Vazifani bosing
2. `📎 Fayl yuborish` tugmasini bosing
3. Faylni yuboring (izohlash ham mumkin)

---

### Izoh qoldirish
1. Vazifani bosing
2. `💬 Izoh qoldirish` tugmasini bosing
3. Xabarni yuboring

> Izohlar admin ga ham ko'rinadi

---

## 📊 STATISTIKA

`📊 Statistikam` tugmasini bosing — joriy oy uchun:
- Jami vazifalar soni
- Bajarilganlar, jarayondagilar, kechikkanlar
- Bajarilish foizi va progress bar
- Har bir vazifa holati

---

## 🔔 AVTOMATIK ESLATMALAR

Bot quyidagi hollarda sizga xabar yuboradi:

| Eslatma | Qachon keladi |
|---------|--------------|
| 🌅 Kunlik digest | Har kuni 09:00 da |
| ⚠️ 3 kun qoldi | Muddatgacha 3 kun qolganda |
| 🚨 Ertaga muddat | Muddatgacha 1 kun qolganda |
| 🔴 Muddat o'tdi | Muddat o'tib ketganda |
| ⏳ Tasdiqlanmagan | Tasdiqlash eslatmasi |
| 🔔 Shaxsiy eslatma | Admin belgilagan intervalda |

---

## ❓ KO'P SO'RALADIGAN SAVOLLAR

**Vazifani ko'rolmayapman?**
`/start` yuboring va qayta kiring.

**Xato xabar chiqdi?**
`/bekor` yuboring va qaytadan boshlang.

**Tilni o'zgartirmoqchiman?**
`🌐 Til` tugmasini bosing.

**Vazifam ko'rinmayapti?**
Faqat **faol** (bajarilmagan) vazifalar ko'rsatiladi. Barcha vazifalar uchun `📊 Statistikam` ga kiring.

---

## ⚙️ ADMIN UCHUN QO'LLANMA

> Bu bo'lim faqat administrator uchun

### Admin panelini ochish
`/admin` yuboring yoki `⚙️ Admin panel` tugmasini bosing.

### Admin panel imkoniyatlari:

| Tugma | Vazifasi |
|-------|---------|
| ➕ Vazifa qo'shish | Hodimga yangi vazifa berish |
| 📅 Reja qo'shish | Oylik reja yaratish |
| 📋 Barcha vazifalar | Filtrlash bilan ko'rish |
| 👥 Hodimlar bo'yicha | Har bir hodim vazifalarini ko'rish |
| 📅 Rejalar | Oylik rejalar va bajarilish foizi |
| 📊 Oylik statistika | Oy bo'yicha batafsil hisobot |
| 🏆 Reyting | Hodimlar reytingi (barcha vaqt) |
| 🔴 Kechikkanlar | Muddati o'tgan vazifalar |
| ⏳ Tasdiqlanmaganlar | Tasdiqlanmagan vazifalar |
| 👥 Hodimlar | Hodimlarni boshqarish |
| 📨 Hisobot yuborish | Barcha hodimga oylik hisobot |
| 📥 Excel eksport | Vazifalarni Excel ga yuklash |
| 🗓 Majlislar | Majlislarni boshqarish |

---

### Vazifa qo'shish tartibi:
1. `➕ Vazifa qo'shish` → vazifa nomi
2. Tavsif (yoki `/skip`)
3. Kategoriyani tanlang
4. Mas'ul hodimni tanlang
5. Muddatni kalendardan tanlang
6. Ustuvorlikni tanlang
7. Eslatma intervalini tanlang

Hodim darhol xabar oladi va tasdiqlashi kerak.

---

### Excel eksport:
1. `📥 Excel eksport` tugmasini bosing
2. Oyni tanlang (yoki barcha vazifalar)
3. `.xlsx` fayl yuboriladi

Faylda: vazifa nomi, mas'ul, muddat, holat, bajarilish %, yaratuvchi.

---

### Hodimlarni boshqarish:
- `👑 Admin qilish` — hodimga admin huquqi berish
- `🚫 Bloklash` — hodimni tizimdan chiqarish
- `📋 Vazifalarini ko'rish` — hodimning barcha vazifalari

---

## 📞 YORDAM

Muammo bo'lsa — adminizga murojaat qiling yoki `/start` bilan qayta kiring.

---

*Teplolux Monitoring Tizimi • 2025*
