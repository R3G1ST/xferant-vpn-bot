import os
from pathlib import Path

# Загружаем переменные из .env файла если он существует
env_path = Path('.env')
if env_path.exists():
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                except ValueError:
                    continue

# TARIFFS configuration
TARIFFS = {
    "m1": {
        "days": int(os.getenv("TARIFF_M1_DAYS", "30")),
        "devices": int(os.getenv("TARIFF_M1_DEVICES", "1")),
        "price": int(os.getenv("TARIFF_M1_PRICE", "200"))
    },
    "m3": {
        "days": int(os.getenv("TARIFF_M3_DAYS", "90")),
        "devices": int(os.getenv("TARIFF_M3_DEVICES", "2")),
        "price": int(os.getenv("TARIFF_M3_PRICE", "500"))
    },
    "m6": {
        "days": int(os.getenv("TARIFF_M6_DAYS", "180")),
        "devices": int(os.getenv("TARIFF_M6_DEVICES", "3")),
        "price": int(os.getenv("TARIFF_M6_PRICE", "900"))
    },
}

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PAY_TEXT = os.getenv("PAY_TEXT", "Оплатите заказ и ожидайте подтверждения администратором")

# Xferant VPN configuration
VPN_SERVER = os.getenv("VPN_SERVER", "extra.xferant-vpn.ru")
VPN_OBFS_PASSWORD = os.getenv("VPN_OBFS_PASSWORD", "xferantHyst")
VPN_PORT = os.getenv("VPN_PORT", "443")
VPN_SNI = os.getenv("VPN_SNI", "yandex.ru")
VPN_SERVER_NAME = os.getenv("VPN_SERVER_NAME", "Xferant Sweden")

# S-UI API configuration
SUI_API_URL = os.getenv("SUI_API_URL", "https://extra.xferant-vpn.ru/api")
SUI_API_KEY = os.getenv("SUI_API_KEY", "rWAsKPkFaCQePlZf7SELBaaIS6HmWAyL")

# Web App configuration
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://extra.xferant-vpn.ru/miniapp")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/xferant_support")

# Проверка обязательных переменных
if not BOT_TOKEN:
    print("❌ ВНИМАНИЕ: BOT_TOKEN не установлен!")
