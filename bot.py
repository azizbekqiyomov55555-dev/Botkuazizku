import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import sqlite3
from datetime import datetime

# ========================
# SOZLAMALAR
# ========================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # @BotFather dan olingan token
ADMIN_ID = 123456789  # Admin Telegram ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========================
# DATABASE
# ========================
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance REAL DEFAULT 0,
            joined_at TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS social_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            link TEXT,
            added_at TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            link TEXT,
            service TEXT,
            quantity INTEGER,
            price REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, username, full_name):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, full_name, balance, joined_at) VALUES (?, ?, ?, 0, ?)",
        (user_id, username, full_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def update_balance(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_user_accounts(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM social_accounts WHERE user_id = ?", (user_id,))
    accounts = c.fetchall()
    conn.close()
    return accounts

def add_social_account(user_id, platform, link):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO social_accounts (user_id, platform, link, added_at) VALUES (?, ?, ?, ?)",
        (user_id, platform, link, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def create_order(user_id, platform, link, service, quantity, price):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (user_id, platform, link, service, quantity, price, status, created_at) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)",
        (user_id, platform, link, service, quantity, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_user_orders(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10", (user_id,))
    orders = c.fetchall()
    conn.close()
    return orders

def get_all_users():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users

# ========================
# STATES
# ========================
class OrderStates(StatesGroup):
    waiting_platform_name = State()
    waiting_link = State()
    waiting_service = State()
    waiting_quantity = State()
    confirming_order = State()

class PaymentStates(StatesGroup):
    waiting_amount = State()
    waiting_receipt = State()

class AddAccountStates(StatesGroup):
    waiting_platform = State()
    waiting_link = State()

class BroadcastState(StatesGroup):
    waiting_message = State()

# ========================
# XIZMATLAR RO'YXATI
# ========================
SERVICES = {
    "Instagram": {
        "👥 Followers": {"price_per_1k": 5000, "min": 100, "max": 10000},
        "❤️ Likes": {"price_per_1k": 2000, "min": 50, "max": 5000},
        "👁️ Views": {"price_per_1k": 1000, "min": 100, "max": 50000},
        "💬 Comments": {"price_per_1k": 10000, "min": 10, "max": 500},
    },
    "YouTube": {
        "👥 Subscribers": {"price_per_1k": 10000, "min": 100, "max": 5000},
        "👁️ Views": {"price_per_1k": 3000, "min": 500, "max": 100000},
        "👍 Likes": {"price_per_1k": 5000, "min": 50, "max": 5000},
    },
    "Telegram": {
        "👥 Members": {"price_per_1k": 8000, "min": 100, "max": 10000},
        "👁️ Post Views": {"price_per_1k": 1500, "min": 100, "max": 50000},
    },
    "TikTok": {
        "👥 Followers": {"price_per_1k": 7000, "min": 100, "max": 10000},
        "❤️ Likes": {"price_per_1k": 3000, "min": 100, "max": 10000},
        "👁️ Views": {"price_per_1k": 1500, "min": 1000, "max": 100000},
    },
    "Twitter/X": {
        "👥 Followers": {"price_per_1k": 12000, "min": 100, "max": 5000},
        "❤️ Likes": {"price_per_1k": 4000, "min": 50, "max": 5000},
    },
}

# ========================
# KLAVIATURA
# ========================
def main_menu_kb(user_id=None):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛒 Buyurtma berish")
    builder.button(text="📋 Buyurtmalar")
    builder.button(text="💰 Hisobim")
    builder.button(text="💳 Hisob to'ldirish")
    builder.button(text="📞 Murojaat")
    builder.button(text="📖 Qo'llanma")
    if user_id and user_id == ADMIN_ID:
        builder.button(text="🖥 Boshqaruv")
    builder.adjust(1, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def platforms_kb():
    builder = ReplyKeyboardBuilder()
    for platform in SERVICES.keys():
        builder.button(text=platform)
    builder.button(text="🔙 Orqaga")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def services_kb(platform):
    builder = ReplyKeyboardBuilder()
    for service in SERVICES[platform].keys():
        builder.button(text=service)
    builder.button(text="🔙 Orqaga")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def back_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔙 Orqaga")
    return builder.as_markup(resize_keyboard=True)

def confirm_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data="confirm_order")
    builder.button(text="❌ Bekor qilish", callback_data="cancel_order")
    builder.adjust(2)
    return builder.as_markup()

def admin_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="👥 Foydalanuvchilar")
    builder.button(text="📊 Statistika")
    builder.button(text="📢 Xabar yuborish")
    builder.button(text="💰 Balans to'ldirish")
    builder.button(text="🔙 Orqaga")
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

# ========================
# HANDLERS - START
# ========================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    add_user(user.id, user.username or "", user.full_name)
    
    await message.answer(
        f"🖥 Asosiy menyudasiz!",
        reply_markup=main_menu_kb(user.id)
    )

# ========================
# BUYURTMA BERISH
# ========================
@dp.message(F.text == "🛒 Buyurtma berish")
async def order_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📱 Ijtimoiy tarmoqni tanlang:",
        reply_markup=platforms_kb()
    )
    await state.set_state(OrderStates.waiting_platform_name)

@dp.message(OrderStates.waiting_platform_name)
async def order_platform_selected(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("🖥 Asosiy menyu", reply_markup=main_menu_kb(message.from_user.id))
        return
    
    platform = message.text
    if platform not in SERVICES:
        await message.answer("⚠️ Noto'g'ri tanlov! Quyidagi tarmoqlardan birini tanlang:")
        return
    
    await state.update_data(platform=platform)
    
    services_text = f"📱 *{platform}* xizmatlari:\n\n"
    for service, info in SERVICES[platform].items():
        services_text += f"{service}\n"
        services_text += f"  💰 Narx: {info['price_per_1k']:,} so'm / 1000 ta\n"
        services_text += f"  📊 Min: {info['min']:,} | Max: {info['max']:,}\n\n"
    
    await message.answer(
        services_text,
        parse_mode="Markdown",
        reply_markup=services_kb(platform)
    )
    await state.set_state(OrderStates.waiting_service)

@dp.message(OrderStates.waiting_service)
async def order_service_selected(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("📱 Ijtimoiy tarmoqni tanlang:", reply_markup=platforms_kb())
        await state.set_state(OrderStates.waiting_platform_name)
        return
    
    data = await state.get_data()
    platform = data.get("platform")
    
    if message.text not in SERVICES[platform]:
        await message.answer("⚠️ Noto'g'ri xizmat! Ro'yxatdan birini tanlang.")
        return
    
    await state.update_data(service=message.text)
    
    await message.answer(
        "🔗 Profil yoki post linkini kiriting:\n\n"
        "Misol: https://instagram.com/username",
        reply_markup=back_kb()
    )
    await state.set_state(OrderStates.waiting_link)

@dp.message(OrderStates.waiting_link)
async def order_link_entered(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        data = await state.get_data()
        platform = data.get("platform")
        await message.answer("Xizmatni tanlang:", reply_markup=services_kb(platform))
        await state.set_state(OrderStates.waiting_service)
        return
    
    link = message.text
    if not (link.startswith("http://") or link.startswith("https://")):
        await message.answer("⚠️ Noto'g'ri link! https:// bilan boshlangan link kiriting.")
        return
    
    await state.update_data(link=link)
    data = await state.get_data()
    platform = data.get("platform")
    service = data.get("service")
    service_info = SERVICES[platform][service]
    
    await message.answer(
        f"🔢 Miqdorni kiriting:\n\n"
        f"📊 Min: {service_info['min']:,}\n"
        f"📊 Max: {service_info['max']:,}\n"
        f"💰 Narx: {service_info['price_per_1k']:,} so'm / 1000 ta",
        reply_markup=back_kb()
    )
    await state.set_state(OrderStates.waiting_quantity)

@dp.message(OrderStates.waiting_quantity)
async def order_quantity_entered(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("🔗 Link kiriting:", reply_markup=back_kb())
        await state.set_state(OrderStates.waiting_link)
        return
    
    try:
        quantity = int(message.text.replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    
    data = await state.get_data()
    platform = data.get("platform")
    service = data.get("service")
    link = data.get("link")
    service_info = SERVICES[platform][service]
    
    if quantity < service_info["min"] or quantity > service_info["max"]:
        await message.answer(
            f"⚠️ Miqdor {service_info['min']:,} dan {service_info['max']:,} gacha bo'lishi kerak!"
        )
        return
    
    price = (quantity / 1000) * service_info["price_per_1k"]
    balance = get_balance(message.from_user.id)
    
    await state.update_data(quantity=quantity, price=price)
    
    confirm_text = (
        f"📋 *Buyurtma tafsilotlari:*\n\n"
        f"📱 Platforma: {platform}\n"
        f"⚙️ Xizmat: {service}\n"
        f"🔗 Link: {link}\n"
        f"🔢 Miqdor: {quantity:,}\n"
        f"💰 Narx: {price:,.0f} so'm\n\n"
        f"💳 Hisobingiz: {balance:,.0f} so'm\n"
    )
    
    if balance < price:
        confirm_text += f"\n⚠️ *Hisobingizda mablag' yetarli emas!*\n"
        confirm_text += f"Yetishmaydi: {(price - balance):,.0f} so'm"
    
    await message.answer(
        confirm_text,
        parse_mode="Markdown",
        reply_markup=confirm_kb()
    )
    await state.set_state(OrderStates.confirming_order)

@dp.callback_query(F.data == "confirm_order", OrderStates.confirming_order)
async def order_confirmed(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    
    platform = data.get("platform")
    service = data.get("service")
    link = data.get("link")
    quantity = data.get("quantity")
    price = data.get("price")
    
    balance = get_balance(user_id)
    
    if balance < price:
        await callback.answer("❌ Hisobingizda mablag' yetarli emas!", show_alert=True)
        return
    
    # Balansdan ayirish
    update_balance(user_id, -price)
    
    # Buyurtma yaratish
    order_id = create_order(user_id, platform, link, service, quantity, price)
    
    await callback.message.edit_text(
        f"✅ *Buyurtma qabul qilindi!*\n\n"
        f"🆔 Buyurtma ID: #{order_id}\n"
        f"📱 Platforma: {platform}\n"
        f"⚙️ Xizmat: {service}\n"
        f"🔢 Miqdor: {quantity:,}\n"
        f"💰 To'landi: {price:,.0f} so'm\n\n"
        f"⏳ Buyurtma bajarilmoqda...",
        parse_mode="Markdown"
    )
    
    # Admin ga xabar
    try:
        user = callback.from_user
        await bot.send_message(
            ADMIN_ID,
            f"🆕 *Yangi buyurtma #{order_id}*\n\n"
            f"👤 Foydalanuvchi: {user.full_name} (@{user.username or 'yoq'})\n"
            f"🆔 ID: {user_id}\n"
            f"📱 Platforma: {platform}\n"
            f"⚙️ Xizmat: {service}\n"
            f"🔗 Link: {link}\n"
            f"🔢 Miqdor: {quantity:,}\n"
            f"💰 Narx: {price:,.0f} so'm",
            parse_mode="Markdown"
        )
    except Exception:
        pass
    
    await state.clear()
    await callback.message.answer("🖥 Asosiy menyu", reply_markup=main_menu_kb(user_id))

@dp.callback_query(F.data == "cancel_order", OrderStates.confirming_order)
async def order_cancelled(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await state.clear()
    await callback.message.answer("🖥 Asosiy menyu", reply_markup=main_menu_kb(callback.from_user.id))

# ========================
# BUYURTMALAR RO'YXATI
# ========================
@dp.message(F.text == "📋 Buyurtmalar")
async def show_orders(message: types.Message):
    orders = get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer("📭 Sizda hali buyurtmalar yo'q.")
        return
    
    text = "📋 *So'nggi buyurtmalaringiz:*\n\n"
    status_emoji = {"pending": "⏳", "processing": "🔄", "completed": "✅", "cancelled": "❌"}
    
    for order in orders[:5]:
        order_id, user_id, platform, link, service, quantity, price, status, created_at = order
        emoji = status_emoji.get(status, "❓")
        text += (
            f"🆔 #{order_id} | {emoji} {status.upper()}\n"
            f"📱 {platform} — {service}\n"
            f"🔢 {quantity:,} | 💰 {price:,.0f} so'm\n"
            f"📅 {created_at[:10]}\n\n"
        )
    
    await message.answer(text, parse_mode="Markdown")

# ========================
# HISOB
# ========================
@dp.message(F.text == "💰 Hisobim")
async def show_balance(message: types.Message):
    balance = get_balance(message.from_user.id)
    orders = get_user_orders(message.from_user.id)
    total_spent = sum(o[6] for o in orders if o[7] in ["completed", "processing", "pending"])
    
    await message.answer(
        f"💰 *Hisobim*\n\n"
        f"💳 Balans: *{balance:,.0f} so'm*\n"
        f"📊 Jami buyurtmalar: {len(orders)} ta\n"
        f"💸 Jami sarflangan: {total_spent:,.0f} so'm",
        parse_mode="Markdown"
    )

# ========================
# HISOB TO'LDIRISH
# ========================
@dp.message(F.text == "💳 Hisob to'ldirish")
async def topup_start(message: types.Message, state: FSMContext):
    await message.answer(
        "💳 *Hisob to'ldirish*\n\n"
        "To'lov usullari:\n"
        "🏦 Click / Payme / Uzcard\n\n"
        "📲 Karta raqami: *8600 1234 5678 9012*\n"
        "👤 Egasi: *Azizbek*\n\n"
        "💰 Qancha to'ldirmoqchisiz? (so'mda kiriting)\n"
        "Misol: 50000",
        parse_mode="Markdown",
        reply_markup=back_kb()
    )
    await state.set_state(PaymentStates.waiting_amount)

@dp.message(PaymentStates.waiting_amount)
async def topup_amount(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await state.clear()
        await message.answer("🖥 Asosiy menyu", reply_markup=main_menu_kb(message.from_user.id))
        return
    
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        if amount < 5000:
            await message.answer("⚠️ Minimal to'lov 5,000 so'm!")
            return
    except ValueError:
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    
    await state.update_data(amount=amount)
    await message.answer(
        f"✅ *{amount:,} so'm* to'lovni amalga oshiring va chekni yuboring.\n\n"
        "📸 To'lov chekini (screenshot) yuboring:",
        parse_mode="Markdown"
    )
    await state.set_state(PaymentStates.waiting_receipt)

@dp.message(PaymentStates.waiting_receipt, F.photo)
async def topup_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")
    user = message.from_user
    
    # Admin ga chek yuborish
    try:
        await bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=(
                f"💳 *Yangi to'lov so'rovi*\n\n"
                f"👤 {user.full_name} (@{user.username or 'yoq'})\n"
                f"🆔 ID: {user.id}\n"
                f"💰 Miqdor: {amount:,} so'm\n\n"
                f"Tasdiqlash uchun:\n"
                f"/topup_{user.id}_{amount}"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    
    await message.answer(
        "✅ *Chek qabul qilindi!*\n\n"
        "⏳ Admin tekshirib, hisobingizni to'ldiradi.\n"
        "Odatda 5-30 daqiqa ichida.",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(user.id)
    )
    await state.clear()

# ========================
# QO'LLANMA
# ========================
@dp.message(F.text == "📖 Qo'llanma")
async def guide(message: types.Message):
    await message.answer(
        "📖 *Foydalanish qo'llanmasi*\n\n"
        "1️⃣ *Hisob to'ldirish* — Balansni to'ldiring\n"
        "2️⃣ *Buyurtma berish* — Platforma va xizmat tanlang\n"
        "3️⃣ *Link kiriting* — Profil yoki post linkini kiriting\n"
        "4️⃣ *Miqdor kiriting* — Nechta kerakligini kiriting\n"
        "5️⃣ *Tasdiqlang* — Buyurtma boshlanadi!\n\n"
        "❓ Savollar bo'lsa: @admin_username ga yozing",
        parse_mode="Markdown"
    )

# ========================
# MUROJAAT
# ========================
@dp.message(F.text == "📞 Murojaat")
async def contact(message: types.Message):
    await message.answer(
        "📞 *Bog'lanish*\n\n"
        "👤 Admin: @admin_username\n"
        "📧 Email: admin@example.com\n"
        "⏰ Ish vaqti: 9:00 - 22:00\n\n"
        "💬 Xabar yozing, tez javob beramiz!",
        parse_mode="Markdown"
    )

# ========================
# ADMIN PANEL
# ========================
@dp.message(F.text == "🖥 Boshqaruv")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = get_all_users()
    await message.answer(
        f"🖥 *Admin Panel*\n\n"
        f"👥 Jami foydalanuvchilar: {len(users)} ta",
        parse_mode="Markdown",
        reply_markup=admin_kb()
    )

@dp.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = get_all_users()
    text = f"👥 *Foydalanuvchilar ({len(users)} ta):*\n\n"
    
    for user in users[:20]:
        user_id, username, full_name, balance, joined_at = user
        text += f"👤 {full_name} | 💰 {balance:,.0f} so'm\n"
        text += f"   @{username or 'yoq'} | 🆔 {user_id}\n\n"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "📊 Statistika")
async def admin_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = get_all_users()
    total_balance = sum(u[3] for u in users)
    
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(price) FROM orders WHERE status='completed'")
    completed = c.fetchone()
    c.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
    pending = c.fetchone()
    conn.close()
    
    await message.answer(
        f"📊 *Statistika*\n\n"
        f"👥 Foydalanuvchilar: {len(users)} ta\n"
        f"💰 Jami balanslar: {total_balance:,.0f} so'm\n"
        f"✅ Bajarilgan: {completed[0]} ta | {(completed[1] or 0):,.0f} so'm\n"
        f"⏳ Kutayotgan: {pending[0]} ta",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("📢 Yubormoqchi bo'lgan xabaringizni kiriting:")
    await state.set_state(BroadcastState.waiting_message)

@dp.message(BroadcastState.waiting_message)
async def broadcast_send(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = get_all_users()
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await bot.send_message(user[0], message.text)
            sent += 1
        except Exception:
            failed += 1
    
    await message.answer(
        f"✅ Yuborildi: {sent} ta\n❌ Yuborilmadi: {failed} ta",
        reply_markup=admin_kb()
    )
    await state.clear()

# Admin balans to'ldirish komandasi
@dp.message(Command("topup"))
async def admin_topup(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    # Format: /topup_USER_ID_AMOUNT
    parts = message.text.split("_")
    if len(parts) != 3:
        await message.answer("Format: /topup_USER_ID_AMOUNT")
        return
    
    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("Noto'g'ri format!")
        return
    
    update_balance(user_id, amount)
    
    await message.answer(f"✅ {user_id} ga {amount:,} so'm qo'shildi!")
    
    try:
        await bot.send_message(
            user_id,
            f"✅ *Hisobingiz to'ldirildi!*\n\n"
            f"💰 +{amount:,} so'm qo'shildi.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

@dp.message(F.text == "🔙 Orqaga")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🖥 Asosiy menyu", reply_markup=main_menu_kb(message.from_user.id))

# ========================
# MAIN
# ========================
async def main():
    init_db()
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
