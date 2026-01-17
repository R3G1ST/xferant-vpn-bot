from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo
from bot.config import WEBAPP_URL, SUPPORT_URL

def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Все заказы", callback_data="orders_all")
    kb.button(text="🟢 В ожидании", callback_data="orders_wait")
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.adjust(2)
    return kb.as_markup()

def admin_order_buttons(order_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"ok_{order_id}")
    kb.button(text="❌ Отменить", callback_data=f"cancel_{order_id}")
    kb.adjust(2)
    return kb.as_markup()

def user_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Купить подписку", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="📊 Моя статистика", callback_data="user_stats")
    kb.button(text="🤝 Реферальная программа", callback_data="referral_info")
    kb.button(text="🆘 Поддержка", url=SUPPORT_URL)
    kb.adjust(2)
    return kb.as_markup()
