"""
Google Sheets ulanishini tekshirish uchun.
Railway da: python test_sheets.py
"""
import os, json, base64
from dotenv import load_dotenv
load_dotenv()

cred_raw  = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
sheet_id  = os.getenv("GOOGLE_SHEET_ID", "")

print(f"GOOGLE_CREDENTIALS_JSON set: {bool(cred_raw)} (len={len(cred_raw)})")
print(f"GOOGLE_SHEET_ID: {sheet_id!r}")

if not cred_raw:
    print("❌ GOOGLE_CREDENTIALS_JSON bo'sh — Railway Variables ga to'g'ri qo'shilganmi?")
    exit(1)

# JSON parse
try:
    try:
        cred_data = json.loads(cred_raw)
    except json.JSONDecodeError:
        cred_data = json.loads(base64.b64decode(cred_raw).decode())
    print(f"✅ JSON parsed — project: {cred_data.get('project_id')}, email: {cred_data.get('client_email')}")
except Exception as e:
    print(f"❌ JSON parse error: {e}")
    exit(1)

try:
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(cred_data, scopes=scopes)
    gc = gspread.authorize(creds)
    print("✅ gspread client yaratildi")
except Exception as e:
    print(f"❌ gspread init error: {e}")
    exit(1)

try:
    ss = gc.open_by_key(sheet_id)
    print(f"✅ Spreadsheet ochildi: {ss.title!r}")
except Exception as e:
    print(f"❌ Spreadsheet ochilmadi: {e}")
    print("   → Sheet service account bilan ulashilganmi?")
    print(f"   → Email: {cred_data.get('client_email')}")
    exit(1)

try:
    existing = [ws.title for ws in ss.worksheets()]
    print(f"Mavjud varoqlar: {existing}")
    for title, cols in [("Vazifalar", 13), ("Izohlar", 6), ("Faollik", 7)]:
        if title not in existing:
            ws = ss.add_worksheet(title=title, rows=1000, cols=cols)
            print(f"✅ Varaq yaratildi: {title}")
        else:
            print(f"ℹ️  Varaq mavjud: {title}")
except Exception as e:
    print(f"❌ Varaq yaratish xatosi: {e}")
    exit(1)

print("\n✅ Hammasi ishlayapti!")
