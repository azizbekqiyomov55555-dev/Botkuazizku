import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Konfiguratsiya - Railway'dan olinadi
BOT_TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKEN_SHU_YERGA")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0)) # O'zingizning Telegram ID raqamingiz

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Ma'lumotlar bazasi (SQLite) ---
conn = sqlite3.connect('smm_bot.db')
cursor = conn.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        balance INTEGER DEFAULT 0,
                        referrals INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY,
                        api_url TEXT,
                        api_key TEXT,
                        ref_bonus INTEGER DEFAULT 100)''')
    cursor.execute('INSERT OR IGNORE INTO settings (id, ref_bonus) VALUES (1, 100)')
    conn.commit()

init_db()

# --- KLAWIATURALAR ---
def user_menu():
    kb = [
        [KeyboardButton(text="🛒 Buyurtma berish")],
        [KeyboardButton(text="💰 Pul ishlash"), KeyboardButton(text="👤 Hisobim")],
        [KeyboardButton(text="💳 Hisob to'ldirish")],[KeyboardButton(text="📞 Murojaat"), KeyboardButton(text="📚 Qo'llanma")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def admin_menu():
    kb = [[KeyboardButton(text="⚙️ Asosiy sozlamalar"), KeyboardButton(text="📊 Statistika")],[KeyboardButton(text="📢 Xabar yuborish"), KeyboardButton(text="🔐 Majburiy obuna kanallar")],[KeyboardButton(text="💳 To'lov tizimlar"), KeyboardButton(text="🔑 API")],[KeyboardButton(text="📂 Bo'limlar"), KeyboardButton(text="◀️ Asosiy menyudasiz!")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- STATELAR (Holatlar) ---
class APISetup(StatesGroup):
    url = State()
    key = State()

class CategorySetup(StatesGroup):
    name = State()

# ================= FOYDALANUVCHI QISMI =================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    await message.answer("Asosiy menyudasiz!", reply_markup=user_menu())

@dp.message(F.text == "👤 Hisobim")
async def hisob_handler(message: types.Message):
    user_id = message.from_user.id
    cursor.execute('SELECT balance, referrals FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        text = (f"👤 Sizning ID raqamingiz: <code>{user_id}</code>\n\n"
                f"💵 Balansingiz: {user[0]} so'm\n"
                f"🛍 Buyurtmalaringiz: 0 ta\n"
                f"👥 Referallaringiz: {user[1]} ta\n"
                f"📥 Kiritgan pulingiz: 0 so'm")
        await message.answer(text)

@dp.message(F.text == "💰 Pul ishlash")
async def pul_ishlash(message: types.Message):
    bot_me = await bot.get_me()
    ref_link = f"https://t.me/{bot_me.username}?start={message.from_user.id}"
    cursor.execute('SELECT ref_bonus FROM settings WHERE id=1')
    bonus = cursor.fetchone()[0]
    
    text = (f"🔗 Sizning referal havolangiz:\n\n<code>{ref_link}</code>\n\n"
            f"🎁 1 ta referal uchun {bonus} so'm beriladi\n"
            f"👥 Referallaringiz: 0 ta")
    await message.answer(text, disable_web_page_preview=True)

# ================= ADMIN QISMI =================

@dp.message(Command("boshqaruv"))
async def boshqaruv_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin paneliga xush kelibsiz !", reply_markup=admin_menu())

@dp.message(F.text == "◀️ Asosiy menyudasiz!")
async def back_to_main(message: types.Message):
    await message.answer("Asosiy menyudasiz!", reply_markup=user_menu())

@dp.message(F.text == "🔑 API", F.from_user.id == ADMIN_ID)
async def api_handler(message: types.Message, state: FSMContext):
    cursor.execute('SELECT api_url, api_key FROM settings WHERE id=1')
    api = cursor.fetchone()
    url = api[0] if api[0] else "Kiritilmagan"
    key = api[1] if api[1] else "Kiritilmagan"
    
    text = (f"API manzili:\nNamuna: https://saleseen.uz/api/v2\n\n"
            f"Joriy URL: <code>{url}</code>\nJoriy Kalit: <code>{key}</code>\n\nAPI manzilini kiriting:")
    await message.answer(text)
    await state.set_state(APISetup.url)

@dp.message(APISetup.url, F.from_user.id == ADMIN_ID)
async def api_url_set(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer(f"❗️ {message.text} muvaffaqiyatli qabul qilindi!\n\nAPI kalitini kiriting:")
    await state.set_state(APISetup.key)

@dp.message(APISetup.key, F.from_user.id == ADMIN_ID)
async def api_key_set(message: types.Message, state: FSMContext):
    data = await state.get_data()
    url = data['url']
    key = message.text
    
    cursor.execute('UPDATE settings SET api_url = ?, api_key = ? WHERE id = 1', (url, key))
    conn.commit()
    
    await message.answer("✅ API muvaffaqiyatli qo'shildi!\n💵 Balans: 0 UZS", reply_markup=admin_menu())
    await state.clear()

@dp.message(F.text == "📂 Bo'limlar", F.from_user.id == ADMIN_ID)
async def bolimlar_handler(message: types.Message, state: FSMContext):
    await message.answer("Yangi bo'lim nomini kiriting:\n(Masalan: Obunachi)")
    await state.set_state(CategorySetup.name)

@dp.message(CategorySetup.name, F.from_user.id == ADMIN_ID)
async def add_bolim(message: types.Message, state: FSMContext):
    name = message.text
    await message.answer(f"✅ {name} - bo'limi muvaffaqiyatli qo'shildi!", reply_markup=admin_menu())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
