import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.environ.get("BOT_TOKEN", "SIZNING_TOKENINGIZ")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- MA'LUMOTLAR BAZASI ---
conn = sqlite3.connect('smm_panel.db')
cursor = conn.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, referrals INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS apis (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, key TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, network TEXT, name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, cat_id INTEGER, api_id INTEGER, service_id INTEGER, price INTEGER, desc TEXT)''')
    conn.commit()

init_db()

# --- KLAWIATURALAR ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Buyurtma berish")],
        [KeyboardButton(text="Buyurtmalar"), KeyboardButton(text="Hisobim")],[KeyboardButton(text="Pul ishlash"), KeyboardButton(text="Hisob to'ldirish")],[KeyboardButton(text="Murojaat"), KeyboardButton(text="Qo'llanma")]
    ], resize_keyboard=True)

def admin_menu():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⚙️ Asosiy sozlamalar"), KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📤 Xabar yuborish")],[KeyboardButton(text="🧲 Majburiy obuna kanallar")],
        [KeyboardButton(text="💳 To'lov tizimlar"), KeyboardButton(text="🔑 API")],
        [KeyboardButton(text="👤 Foydalanuvchini boshqarish")],[KeyboardButton(text="📚 Qo'llanmalar"), KeyboardButton(text="🛍 Buyurtmalar")]
    ], resize_keyboard=True)

def back_reply_menu():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Orqaga")]], resize_keyboard=True)

# --- STATELAR ---
class APISetup(StatesGroup):
    url = State()
    key = State()

class CategorySetup(StatesGroup):
    network = State()
    name = State()

class ServiceSetup(StatesGroup):
    cat_id = State()
    api_id = State()
    service_id = State()
    price = State()
    desc = State()

class MurojaatState(StatesGroup):
    text = State()

# ================= FOYDALANUVCHI QISMI =================

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (message.from_user.id,))
    conn.commit()
    await message.answer("Asosiy menyudasiz!", reply_markup=main_menu())

@dp.message(F.text == "Hisobim")
async def hisob_handler(message: types.Message):
    cursor.execute('SELECT balance, referrals FROM users WHERE user_id = ?', (message.from_user.id,))
    user = cursor.fetchone()
    if user:
        text = (f"👤 Sizning ID raqamingiz: <code>{message.from_user.id}</code>\n"
                f"💵 Balansingiz: {user[0]} so'm\n"
                f"🛍 Buyurtmalaringiz: 0 ta\n"
                f"👥 Referallaringiz: {user[1]} ta\n"
                f"📥 Kiritgan pullaringiz: 0 so'm")
        btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Hisobni to'ldirish", callback_data="none")]])
        await message.answer(text, reply_markup=btn)

@dp.message(F.text == "Pul ishlash")
async def pul_ishlash(message: types.Message):
    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔗 Taklif qilish", callback_data="taklif_qilish")]])
    await message.answer("Quyidagilardan birini tanlang:", reply_markup=btn)

@dp.callback_query(F.data == "taklif_qilish")
async def taklif_link(call: CallbackQuery):
    bot_me = await bot.get_me()
    text = (f"🔗 Sizning referal havolangiz:\n\n"
            f"<code>https://t.me/{bot_me.username}?start={call.from_user.id}</code>\n\n"
            f"1 ta referal uchun 100 so'm beriladi\n"
            f"👥 Referallaringiz: 0 ta")
    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Orqaga", callback_data="del_msg")]])
    await call.message.edit_text(text, reply_markup=btn)

@dp.message(F.text == "Buyurtmalar")
async def buyurtmalar(message: types.Message):
    await message.answer("❗️ Sizda buyurtmalar mavjud emas.")

@dp.message(F.text == "Hisob to'ldirish")
async def tolov(message: types.Message):
    await message.answer("⚠️ To'lov tizimlari mavjud emas!")

@dp.message(F.text == "Qo'llanma")
async def qollanma(message: types.Message):
    await message.answer("⚠️ Qo'llanmalar mavjud emas.")

@dp.message(F.text == "Murojaat")
async def murojaat(message: types.Message, state: FSMContext):
    await message.answer("📄 Murojaat matnini yozib yuboring.", reply_markup=back_reply_menu())
    await state.set_state(MurojaatState.text)

@dp.message(MurojaatState.text)
async def murojaat_send(message: types.Message, state: FSMContext):
    if message.text == "Orqaga":
        await state.clear()
        await message.answer("Asosiy menyudasiz!", reply_markup=main_menu())
        return
    await message.answer("✅ Murojaat adminga yuborildi!", reply_markup=main_menu())
    await state.clear()

# ================= BUYURTMA BERISH (TARMOQLAR) =================
@dp.message(F.text == "Buyurtma berish")
async def buyurtma_berish(message: types.Message):
    kb =[[InlineKeyboardButton(text="📊 Instgram", callback_data="net_Instgram"), InlineKeyboardButton(text="🟢 Telgram", callback_data="net_Telgram")],[InlineKeyboardButton(text="Youtube", callback_data="net_Youtube"), InlineKeyboardButton(text="Tik tok", callback_data="net_Tiktok")]
    ]
    if message.from_user.id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="➕ Qo'shish", callback_data="add_network_fake")])
    await message.answer("Quyidagi ijtimoiy tarmoqlardan birini tanlang.", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ================= ADMIN QISMI =================

@dp.message(Command("boshqaruv"))
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin paneliga hush kelibsiz !", reply_markup=admin_menu())

@dp.message(F.text == "🔑 API", F.from_user.id == ADMIN_ID)
async def api_menu(message: types.Message):
    cursor.execute("SELECT COUNT(*) FROM apis")
    count = cursor.fetchone()[0]
    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ API qo'shish", callback_data="add_api")]])
    await message.answer(f"🔑 API'lar ro'yhati: {count} ta", reply_markup=btn)

@dp.callback_query(F.data == "add_api")
async def add_api(call: CallbackQuery, state: FSMContext):
    await call.message.answer("API manzilini kiriting:\nNamuna: https://capitalsmmapi.uz/api/v2")
    await state.set_state(APISetup.url)

@dp.message(APISetup.url, F.from_user.id == ADMIN_ID)
async def api_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer(f"❗️ {message.text}\nmuvaffaqiyatli qabul qilindi!\n\nAPI kalitini kiriting:")
    await state.set_state(APISetup.key)

@dp.message(APISetup.key, F.from_user.id == ADMIN_ID)
async def api_key(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT INTO apis (url, key) VALUES (?, ?)", (data['url'], message.text))
    conn.commit()
    await message.answer("✅ API muvaffaqiyatli qo'shildi!\n💵 Balans: 1481 UZS", reply_markup=admin_menu())
    await state.clear()

# ================= BO'LIM VA XIZMAT QO'SHISH =================
@dp.callback_query(F.data.startswith("net_"))
async def net_cats(call: CallbackQuery, state: FSMContext):
    network = call.data.split("_")[1]
    cursor.execute("SELECT id, name FROM categories WHERE network=?", (network,))
    cats = cursor.fetchall()
    
    kb =[]
    for cat in cats:
        kb.append([InlineKeyboardButton(text=cat[1], callback_data=f"cat_{cat[0]}")])
        
    if call.from_user.id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"addcat_{network}")])
        kb.append([InlineKeyboardButton(text="📝 Tahrirlash", callback_data="none"), InlineKeyboardButton(text="🗑 O'chirish", callback_data="none")])
    kb.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="del_msg")])
    
    text = "Quyidagi bo'limlardan birini tanlang." if cats else "⚠️ Bo'limlar mavjud emas!"
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("addcat_"))
async def add_cat(call: CallbackQuery, state: FSMContext):
    network = call.data.split("_")[1]
    await state.update_data(network=network)
    await call.message.answer("Yangi bo'lim nomini kiriting:")
    await state.set_state(CategorySetup.name)

@dp.message(CategorySetup.name, F.from_user.id == ADMIN_ID)
async def cat_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT INTO categories (network, name) VALUES (?, ?)", (data['network'], message.text))
    conn.commit()
    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Yana bo'lim qo'shish", callback_data=f"addcat_{data['network']}")]])
    await message.answer(f"✅ {message.text} - bo'limi muvaffaqiyatli qo'shildi!", reply_markup=btn)
    await state.clear()

@dp.callback_query(F.data.startswith("cat_"))
async def show_services(call: CallbackQuery):
    cat_id = call.data.split("_")[1]
    cursor.execute("SELECT id, price FROM services WHERE cat_id=?", (cat_id,))
    svcs = cursor.fetchall()
    
    kb =[]
    if call.from_user.id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"addsvc_{cat_id}")])
        kb.append([InlineKeyboardButton(text="📝 Tahrirlash", callback_data="none"), InlineKeyboardButton(text="🗑 O'chirish", callback_data="none")])
    kb.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="del_msg")])
    
    text = "Quyidagi xizmatlardan birini tanlang:\nNarxlar 1000 tasi uchun berilgan" if svcs else "⚠️ Xizmatlar mavjud emas!"
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("addsvc_"))
async def add_svc_api(call: CallbackQuery, state: FSMContext):
    cat_id = call.data.split("_")[1]
    await state.update_data(cat_id=cat_id)
    await call.message.answer("📋 Xizmat APISini tanlang:\n1. saleseen.uz")
    await state.set_state(ServiceSetup.api_id)

@dp.message(ServiceSetup.api_id, F.from_user.id == ADMIN_ID)
async def add_svc_id(message: types.Message, state: FSMContext):
    await state.update_data(api_id=message.text)
    await message.answer("🆔 Xizmat IDsini kiriting:")
    await state.set_state(ServiceSetup.service_id)

@dp.message(ServiceSetup.service_id, F.from_user.id == ADMIN_ID)
async def add_svc_price(message: types.Message, state: FSMContext):
    await state.update_data(service_id=message.text)
    await message.answer("💵 Xizmat narxini kiriting:")
    await state.set_state(ServiceSetup.price)

@dp.message(ServiceSetup.price, F.from_user.id == ADMIN_ID)
async def add_svc_desc(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("📝 Xizmat haqida ma'lumot kiriting:")
    await state.set_state(ServiceSetup.desc)

@dp.message(ServiceSetup.desc, F.from_user.id == ADMIN_ID)
async def add_svc_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT INTO services (cat_id, api_id, service_id, price, desc) VALUES (?, ?, ?, ?, ?)", 
                   (data['cat_id'], data['api_id'], data['service_id'], data['price'], message.text))
    conn.commit()
    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Yana xizmat qo'shish", callback_data=f"addsvc_{data['cat_id']}")]])
    await message.answer("✅ Xizmat muvaffaqiyatli qo'shildi!", reply_markup=btn)
    await state.clear()

@dp.callback_query(F.data == "del_msg")
async def delete_msg(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Asosiy menyudasiz!", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
