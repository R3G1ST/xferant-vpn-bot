import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineQueryResultArticle, InputTextMessageContent, WebAppInfo
from aiogram.filters import Command

from bot.config import BOT_TOKEN, ADMIN_ID, TARIFFS, PAY_TEXT, VPN_SERVER
from bot.db import db, create_vpn_user, init_db
from bot.keyboards import admin_menu, admin_order_buttons, user_menu
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def generate_referral_link(user_id: int) -> str:
    return f"https://t.me/xferant_vpn_bot?start=ref_{user_id}"

@dp.message(Command("start"))
async def start_command(m: Message):
    if m.text and m.text.startswith("/start ref_"):
        await handle_referral_start(m)
    else:
        text = f"""🔒 Добро пожаловать в Xferant VPN!
        
Премиум VPN сервер в Швеции от команды Xferant.

🌟 Преимущества Xferant VPN:
• 🚀 Высокая скорость (270 Mbps)
• 🔒 Защита от блокировок с obfs
• 🌐 Шведское законодательство
• 📱 До 3 устройств одновременно
• ⚡ Технология Hysteria2
• 🏢 Надежный сервер: {VPN_SERVER}

💎 Xferant - качество проверенное временем!

Используйте /menu для доступа к функциям"""
        await m.answer(text)

@dp.message(Command("menu"))
async def user_menu_command(m: Message):
    text = "🎛️ Панель управления Xferant VPN"
    await m.answer(text, reply_markup=user_menu())

@dp.message(Command("admin"))
async def admin_start(m: Message):
    if m.from_user.id != ADMIN_ID:
        return await m.answer("❌ Доступ запрещен")
    
    await m.answer("👨‍💻 Админ-панель Xferant VPN", reply_markup=admin_menu())

@dp.message(Command("ref"))
async def referral_command(m: Message):
    ref_link = generate_referral_link(m.from_user.id)
    text = f"""🔒 Реферальная программа Xferant VPN

Приглашайте друзей и получайте бонусы!

🎁 За каждого приглашенного:
• Вы получаете +7 дней к подписке
• Друг получает скидку 10% на первый заказ

💎 Xferant - делитесь качеством!

📎 Ваша ссылка: {ref_link}
📊 Статистика: /ref_stats"""
    await m.answer(text)

@dp.message(Command("ref_stats"))
async def referral_stats(m: Message):
    referrals = await db.get_referrals_by_referrer(m.from_user.id)
    count = await db.get_referral_count(m.from_user.id)
    
    text = f"""🔒 Статистика Xferant VPN:

👥 Приглашено пользователей: {count}
💎 Бонусных дней доступно: {count * 7}
📎 Ссылка для приглашений: {generate_referral_link(m.from_user.id)}"""
    await m.answer(text)

async def handle_referral_start(m: Message):
    try:
        if not m.text:
            return
            
        ref_id = int(m.text.split("ref_")[1])
        if ref_id == m.from_user.id:
            await m.answer("❌ Нельзя использовать свою ссылку!")
            return
        
        await db.create_referral(ref_id, m.from_user.id)
        await m.answer("🔒 Добро пожаловать! Вы присоединились по реферальной ссылке Xferant VPN.")
        
    except Exception as e:
        logger.error(f"Referral error: {e}")
        await m.answer("❌ Ошибка обработки реферальной ссылки")

@dp.message(F.content_type=="web_app_data")
async def webapp_handler(m: Message):
    try:
        data = json.loads(m.web_app_data.data)
        action = data.get("action")
        query_id = m.web_app_data.query_id
        
        if action.startswith("buy_"):
            tariff_key = action.split("_")[1]
            if tariff_key not in TARIFFS:
                await m.answer("❌ Неверный тариф")
                return
            
            order = await db.create_order(
                m.from_user.id, 
                m.from_user.username or "unknown",
                tariff_key, 
                query_id
            )
            
            await m.answer(PAY_TEXT)
            await bot.send_message(
                ADMIN_ID, 
                f"🔒 Новый заказ Xferant VPN #{order['id']} ({tariff_key}) от @{m.from_user.username}",
                reply_markup=admin_order_buttons(order['id'])
            )
        
        elif action=="connect":
            await m.answer("🔗 Используйте /menu для доступа к функциям Xferant VPN")
        
        elif action=="stats":
            await m.answer("📊 Используйте /menu для просмотра статистики")
    
    except Exception as e:
        logger.error(f"WebApp error: {e}")
        await m.answer("❌ Ошибка обработки запроса")

@dp.callback_query(F.data.startswith("orders_"))
async def list_orders(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("❌ Доступ запрещен")
    
    status = cb.data.split("_")[1]
    if status == "all":
        orders = await db.get_orders_by_status()
    else:
        orders = await db.get_orders_by_status(status)
    
    if not orders:
        await cb.message.answer("📦 Заказы отсутствуют")
        return
    
    for order in orders:
        text = f"🔒 Заказ Xferant VPN #{order['id']}\nПользователь: @{order['username']}\nТариф: {order['tariff']}\nСтатус: {order['status']}"
        await cb.message.answer(text, reply_markup=admin_order_buttons(order['id']))

@dp.callback_query(F.data.startswith("ok_"))
async def approve_order(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("❌ Доступ запрещен")
    
    order_id = int(cb.data.split("_")[1])
    order = await db.get_order(order_id)
    
    if not order or order['status'] != 'wait':
        return await cb.answer("❌ Заказ не найден или уже обработан")
    
    t = TARIFFS[order['tariff']]
    link = await create_vpn_user(order_id, t["days"])
    
    if link:
        if order['webapp_query_id']:
            await bot.answer_web_app_query(
                web_app_query_id=order['webapp_query_id'],
                result=InlineQueryResultArticle(
                    id=str(order['id']),
                    title="🔒 Xferant VPN Config",
                    input_message_content=InputTextMessageContent(link)
                )
            )
        else:
            await bot.send_message(order['user_id'], 
                f"""🔒 Ваша конфигурация Xferant VPN готова!

💎 Сервер: {VPN_SERVER}
⚡ Скорость: 270 Mbps
📱 Устройств: {t['devices']}
🕒 Дней: {t['days']}

🔗 Ссылка Hysteria2:
```{link}```

Xferant - качество проверенное временем!""")
        
        await cb.message.edit_text("✅ Xferant VPN аккаунт создан")
    else:
        await cb.message.edit_text("❌ Ошибка создания Xferant VPN аккаунта")

@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_order(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("❌ Доступ запрещен")
    
    order_id = int(cb.data.split("_")[1])
    await db.update_order_status(order_id, 'canceled')
    await cb.message.edit_text("❌ Заказ отменён")

@dp.callback_query(F.data=="admin_stats")
async def admin_stats(cb: CallbackQuery):
    orders = await db.get_orders_by_status()
    done_orders = [o for o in orders if o['status'] == 'done']
    wait_orders = [o for o in orders if o['status'] == 'wait']
    referrals_count = len(await db.get_referrals_by_referrer(ADMIN_ID))
    
    text = f"""🔒 Статистика Xferant VPN:

Всего заказов: {len(orders)}
✅ Подтверждено: {len(done_orders)}
⏳ В ожидании: {len(wait_orders)}
🤝 Рефералов: {referrals_count}

💎 Xferant - растем вместе!"""
    await cb.message.answer(text)

@dp.callback_query(F.data=="user_stats")
async def user_stats_handler(cb: CallbackQuery):
    orders = await db.get_orders_by_status('done')
    user_orders = [o for o in orders if o['user_id'] == cb.from_user.id]
    
    if user_orders:
        order = user_orders[-1]  # Последний заказ
        days_left = (order['expiry_date'] - datetime.datetime.utcnow()).days if order.get('expiry_date') else 0
        
        text = f"""🔒 Ваша статистика Xferant VPN:

💎 Сервер: {order.get('server_location', 'Xferant Sweden')}
⏰ Осталось дней: {max(days_left, 0)}
🆔 Логин: {order.get('sui_username', 'Не назначен')}
🌐 Домен: {VPN_SERVER}"""
    else:
        text = "❌ У вас нет активной подписки Xferant VPN"
    
    await cb.message.answer(text)

@dp.callback_query(F.data=="referral_info")
async def referral_info_handler(cb: CallbackQuery):
    ref_link = generate_referral_link(cb.from_user.id)
    text = f"""🤝 Реферальная программа Xferant VPN

🎁 За каждого приглашенного:
• Вы получаете +7 дней
• Друг получает скидку 10%

💎 Xferant - делитесь качеством!

📎 Ваша ссылка: {ref_link}"""
    await cb.message.answer(text)

async def main():
    await init_db()
    logger.info("Xferant VPN Bot started successfully")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
