import os
import sys
import logging
import uuid
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", "8234965653"))
except ValueError:
    logging.error("❌ ADMIN_ID должен быть числом!")
    sys.exit(1)

YOUR_CARD_NUMBER = os.environ.get("YOUR_CARD_NUMBER", "2200 7017 7526 7336")
YOUR_NAME = "Эмиль Г."

# ================== ССЫЛКИ ==================
USER_AGREEMENT_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-08-15-10"
PRIVACY_POLICY_URL = "https://telegra.ph/Politika-konfidencialnosti-08-15-17"

# ================== ТОВАРЫ ==================
PRODUCTS = {
    "cpp_course": {
        "id": "cpp_course",
        "name": "🚀 C++ с нуля до гуру (2026)",
        "description": """
📚 **Полный курс по C++:**
• С нуля до профессионального уровня
• 50+ часов практики

🎯 **Чему научитесь:**
• ООП и шаблоны
• Многопоточность
• Работа с памятью
• Сетевое программирование
""",
        "price": 199
    },
    "frontend_course": {
        "id": "frontend_course",
        "name": "💻 Профессия Фронтенд разработчик",
        "description": """
📚 **Полный курс по Frontend:**
• HTML/CSS/JavaScript
• React + Redux
• TypeScript
• Next.js

🎯 **Чему научитесь:**
• Создавать современные сайты
• Работать с API
• Оптимизировать производительность
""",
        "price": 99
    }
}

# ================== ИНИЦИАЛИЗАЦИЯ ==================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# База данных
payments_db = {}

# ================== ФУНКЦИИ ==================
def get_user_full_name(user: types.User) -> str:
    parts = []
    if user.first_name:
        parts.append(user.first_name)
    if user.last_name:
        parts.append(user.last_name)
    return ' '.join(parts) if parts else "Не указано"

def generate_payment_id() -> str:
    date_part = datetime.now().strftime("%d%m")
    random_part = str(uuid.uuid4())[:4].upper()
    return f"PAY{date_part}{random_part}"

async def notify_admin(text: str, reply_markup=None):
    """Безопасная отправка сообщения админу"""
    try:
        await bot.send_message(ADMIN_ID, text, reply_markup=reply_markup, parse_mode="Markdown")
        return True
    except Exception as e:
        logging.error(f"⚠️ Не удалось отправить сообщение админу: {e}")
        return False

# ================== КОМАНДЫ ==================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 C++ (199 руб)", callback_data="show_cpp")],
            [InlineKeyboardButton(text="💻 Фронтенд (99 руб)", callback_data="show_frontend")],
            [
                InlineKeyboardButton(text="📄 Соглашение", url=USER_AGREEMENT_URL),
                InlineKeyboardButton(text="🔒 Политика", url=PRIVACY_POLICY_URL)
            ],
            [InlineKeyboardButton(text="📞 Поддержка", url=f"https://t.me/Leimskiy")],
        ]
    )
    
    await message.answer(
        "👋 **Добро пожаловать в магазин курсов!**\n\n"
        "Выберите курс:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.message(Command("info"))
async def cmd_info(message: Message):
    info_text = (
        f"📄 **Пользовательское соглашение**\n"
        f"{USER_AGREEMENT_URL}\n\n"
        f"🔒 **Политика конфиденциальности**\n"
        f"{PRIVACY_POLICY_URL}\n\n"
        f"Ознакомьтесь с документами перед использованием бота."
    )
    await message.answer(info_text, parse_mode="Markdown", disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data == "show_cpp")
async def show_cpp(callback: CallbackQuery):
    """Показать курс C++"""
    product = PRODUCTS["cpp_course"]
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Купить", callback_data="buy_cpp")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
        ]
    )
    
    await callback.message.edit_text(
        f"{product['name']}\n"
        f"{product['description']}\n\n"
        f"💰 **Цена: {product['price']} руб**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_frontend")
async def show_frontend(callback: CallbackQuery):
    """Показать курс Frontend"""
    product = PRODUCTS["frontend_course"]
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Купить", callback_data="buy_frontend")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
        ]
    )
    
    await callback.message.edit_text(
        f"{product['name']}\n"
        f"{product['description']}\n\n"
        f"💰 **Цена: {product['price']} руб**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Назад в меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 C++ с нуля до гуру (199 руб)", callback_data="show_cpp")],
            [InlineKeyboardButton(text="💻 Профессия Фронтенд (99 руб)", callback_data="show_frontend")],
            [InlineKeyboardButton(text="📞 Поддержка", url=f"https://t.me/Leimskiy")]
        ]
    )
    
    await callback.message.edit_text(
        "👋 **Добро пожаловать в магазин курсов!**\n\n"
        "Выберите курс:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "buy_cpp")
async def buy_cpp(callback: CallbackQuery):
    """Покупка C++"""
    await buy_product(callback, "cpp_course")

@dp.callback_query(lambda c: c.data == "buy_frontend")
async def buy_frontend(callback: CallbackQuery):
    """Покупка Frontend"""
    await buy_product(callback, "frontend_course")

async def buy_product(callback: CallbackQuery, product_id: str):
    """Общая функция покупки"""
    product = PRODUCTS[product_id]
    payment_id = generate_payment_id()
    full_name = get_user_full_name(callback.from_user)
    username = f"@{callback.from_user.username}" if callback.from_user.username else "нет"
    
    # Сохраняем платеж
    payments_db[payment_id] = {
        "user_id": callback.from_user.id,
        "username": username,
        "username_raw": callback.from_user.username,
        "full_name": full_name,
        "product": product['name'],
        "amount": product['price'],
        "status": "WAITING_PAYMENT",
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    
    # Уведомление админу
    await notify_admin(
        f"🆕 **НОВАЯ ПОКУПКА**\n\n"
        f"📚 Курс: {product['name']}\n"
        f"💰 Сумма: {product['price']} руб\n"
        f"🆔 Номер: `{payment_id}`\n\n"
        f"👤 Покупатель:\n"
        f"└ Имя: {full_name}\n"
        f"└ Username: {username}\n"
        f"└ ID: {callback.from_user.id}"
    )
    
    # Клавиатура для оплаты
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{payment_id}")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{payment_id}")]
        ]
    )
    
    await callback.message.edit_text(
        f"✅ **Оплата на карту**\n\n"
        f"💰 **Сумма:** {product['price']} руб\n\n"
        f"💳 **Номер карты:**\n"
        f"`{YOUR_CARD_NUMBER}`\n\n"
        f"👤 **Получатель:** {YOUR_NAME}\n\n"
        f"После перевода нажмите кнопку **'Я оплатил'**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith('paid_'))
async def callback_paid(callback: CallbackQuery):
    """Пользователь оплатил"""
    payment_id = callback.data.replace('paid_', '')
    
    if payment_id not in payments_db:
        await callback.answer("❌ Платеж не найден", show_alert=True)
        return
    
    payment = payments_db[payment_id]
    
    if payment['status'] != 'WAITING_PAYMENT':
        await callback.answer("Платеж уже обработан", show_alert=True)
        return
    
    payment['status'] = 'WAITING_CONFIRM'
    
    # Клавиатура для админа
    admin_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ ПОДТВЕРДИТЬ", callback_data=f"confirm_{payment_id}"),
                InlineKeyboardButton(text="❌ ОТКЛОНИТЬ", callback_data=f"reject_{payment_id}")
            ]
        ]
    )
    
    # Ссылка на пользователя
    user_link = f"https://t.me/{payment['username_raw']}" if payment['username_raw'] else f"ID: {payment['user_id']}"
    
    await notify_admin(
        f"⚠️ **ПОДТВЕРДИТЕ ПЕРЕВОД**\n\n"
        f"📚 Курс: {payment['product']}\n"
        f"💰 Сумма: {payment['amount']} руб\n"
        f"🆔 Номер: `{payment_id}`\n\n"
        f"👤 Покупатель:\n"
        f"└ Имя: {payment['full_name']}\n"
        f"└ Username: {payment['username']}\n"
        f"└ Ссылка: {user_link}\n\n"
        f"💳 Карта: {YOUR_CARD_NUMBER}\n\n"
        f"❗️ Пользователь сообщил о переводе",
        reply_markup=admin_keyboard
    )
    
    await callback.message.edit_text(
        f"✅ **Заявка отправлена!**\n\n"
        f"📚 Курс: {payment['product']}\n"
        f"💰 Сумма: {payment['amount']} руб\n"
        f"🆔 Номер: `{payment_id}`\n\n"
        f"⏳ Ожидайте, скоро админ свяжется с вами",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith('cancel_'))
async def callback_cancel(callback: CallbackQuery):
    """Отмена платежа"""
    payment_id = callback.data.replace('cancel_', '')
    
    if payment_id in payments_db:
        payments_db[payment_id]['status'] = 'REJECTED'
        await callback.message.edit_text("❌ Платеж отменен")
        await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith('confirm_'))
async def callback_confirm(callback: CallbackQuery):
    """Админ подтверждает"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только админ", show_alert=True)
        return
    
    payment_id = callback.data.replace('confirm_', '')
    
    if payment_id in payments_db:
        payment = payments_db[payment_id]
        payment['status'] = 'CONFIRMED'
        
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ **ПЛАТЕЖ ПОДТВЕРЖДЕН**"
        )
        
        await bot.send_message(
            payment['user_id'],
            f"✅ **Платеж подтвержден!**\n\n"
            f"📚 Курс: {payment['product']}\n"
            f"💰 Сумма: {payment['amount']} руб\n\n"
            f"👨‍💼 Админ скоро свяжется с вами",
            parse_mode="Markdown"
        )
        await callback.answer("✅ Подтверждено")

@dp.callback_query(lambda c: c.data and c.data.startswith('reject_'))
async def callback_reject(callback: CallbackQuery):
    """Админ отклоняет"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Только админ", show_alert=True)
        return
    
    payment_id = callback.data.replace('reject_', '')
    
    if payment_id in payments_db:
        payment = payments_db[payment_id]
        payment['status'] = 'REJECTED'
        
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ **ПЛАТЕЖ ОТКЛОНЕН**"
        )
        
        await bot.send_message(
            payment['user_id'],
            f"❌ **Платеж отклонен**\n\n"
            f"📚 Курс: {payment['product']}\n"
            f"💰 Сумма: {payment['amount']} руб\n\n"
            f"Свяжитесь с администратором",
            parse_mode="Markdown"
        )
        await callback.answer("❌ Отклонено")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Проверка статуса"""
    await message.answer("🔍 Введите номер платежа (например: PAY2512A7B9):")

@dp.message(lambda message: message.text and message.text.upper().startswith('PAY'))
async def check_status(message: Message):
    """Проверка статуса по номеру"""
    payment_id = message.text.strip().upper()
    
    if payment_id in payments_db:
        payment = payments_db[payment_id]
        
        status_text = {
            'WAITING_PAYMENT': '⏳ Ожидает оплаты',
            'WAITING_CONFIRM': '⏳ Проверка админом',
            'CONFIRMED': '✅ Подтвержден',
            'REJECTED': '❌ Отклонен'
        }.get(payment['status'], '❓')
        
        await message.answer(
            f"📊 **Статус платежа**\n\n"
            f"📚 Курс: {payment['product']}\n"
            f"💰 Сумма: {payment['amount']} руб\n"
            f"🆔 Номер: `{payment_id}`\n"
            f"📊 Статус: {status_text}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ Платеж не найден")

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Админ панель"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет доступа")
        return
    
    total = len(payments_db)
    waiting_payment = len([p for p in payments_db.values() if p['status'] == 'WAITING_PAYMENT'])
    waiting_confirm = len([p for p in payments_db.values() if p['status'] == 'WAITING_CONFIRM'])
    confirmed = len([p for p in payments_db.values() if p['status'] == 'CONFIRMED'])
    
    await message.answer(
        f"👨‍💻 **АДМИН ПАНЕЛЬ**\n\n"
        f"📊 **Статистика:**\n"
        f"└ Всего: {total}\n"
        f"└ ⏳ Ожидают оплаты: {waiting_payment}\n"
        f"└ ⚠️ Ждут подтверждения: {waiting_confirm}\n"
        f"└ ✅ Подтверждено: {confirmed}",
        parse_mode="Markdown"
    )

# ================== ЗАПУСК ==================
async def main():
    logging.info("=" * 50)
    logging.info("📚 МАГАЗИН КУРСОВ ЗАПУЩЕН!")
    logging.info("=" * 50)
    logging.info(f"👤 Admin ID: {ADMIN_ID}")
    logging.info(f"💳 Карта: {YOUR_CARD_NUMBER}")
    logging.info("=" * 50)
    
    # Бесконечный цикл для Railway
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"❌ Ошибка: {e}")
            logging.info("🔄 Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())