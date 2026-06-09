import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN  = os.getenv("BOT_TOKEN", "")
ADMIN_IDS  = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip()]
GROUP_ID   = int(os.getenv("GROUP_ID", "0"))  # Telegram guruh ID (ixtiyoriy)
DB_PATH    = os.getenv("DB_PATH", "data/teplolux.db")
