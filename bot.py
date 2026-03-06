import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import sqlite3
from datetime import datetime
import os

# ===================== CONFIG =====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
# ==================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===================== DATABASE =====================
def init_db():
    conn = sqlite3.connect("smm_bot.db")
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        balance INTEGER DEFAULT 0,
        referral_id INTEGER DEFAULT NULL,
        total_deposited INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS networks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        network_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY (network_id) REFERENCES networks(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        api_id TEXT,
        name TEXT,
        price_per_1000 INTEGER,
        min_qty INTEGER DEFAULT 100,
        max_qty INTEGER DEFAULT 100000,
        description TEXT DEFAULT '',
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id INTEGER,
        link TEXT,
        quantity INTEGER,
        price INTEGER,
        status TEXT DEFAULT 'Bajarilmoqda',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (service_id) REFERENCES services(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        type TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Default networks
    for net in ["Telgram", "Instgram", "Tik tok", "Youtube"]:
        c.execute("INSERT OR IGNORE INTO networks (name) VALUES (?)", (net,))
    
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect("smm_bot.db")

# ---- User functions ----
def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def create_user(user_id, username, full_name, referral_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, full_name, referral_id) VALUES (?,?,?,?)",
              (user_id, username, full_name, referral_id))
    # Give referral bonus
    if referral_id and referral_id != user_id:
        c.execute("UPDATE users SET balance=balance+500 WHERE user_id=?", (referral_id,))
        c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?,500,'referral','Referal bonus')", (referral_id,))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def update_balance(user_id, amount):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_referral_count(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE referral_id=?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_total_deposited(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT total_deposited FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_order_count(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

# ---- Network/Category/Service functions ----
def get_networks():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM networks")
    rows = c.fetchall()
    conn.close()
    return rows

def get_categories(network_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM categories WHERE network_id=?", (network_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_services(category_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE category_id=?", (category_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_service(service_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE id=?", (service_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_order(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT o.*, s.name as sname, s.price_per_1000, n.name as nname, cat.name as catname
                 FROM orders o
                 JOIN services s ON o.service_id=s.id
                 JOIN categories cat ON s.category_id=cat.id
                 JOIN networks n ON cat.network_id=n.id
                 WHERE o.id=?""", (order_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_orders(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT o.id, n.name, cat.name, o.quantity, o.price, o.status, o.link, o.created_at
                 FROM orders o
                 JOIN services s ON o.service_id=s.id
                 JOIN categories cat ON s.category_id=cat.id
                 JOIN networks n ON cat.network_id=n.id
                 WHERE o.user_id=?
                 ORDER BY o.id DESC LIMIT 10""", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def create_order(user_id, service_id, link, quantity, price):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, service_id, link, quantity, price) VALUES (?,?,?,?,?)",
              (user_id, service_id, link, quantity, price))
    order_id = c.lastrowid
    c.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (price, user_id))
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?,-?,'order',?)",
              (user_id, price, f"Buyurtma #{order_id}"))
    conn.commit()
    conn.close()
    return order_id

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_banned=0")
    active = c.fetchone()[0]
    conn.close()
    return total, active

def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= datetime('now', '-1 day')")
    new_24h = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= datetime('now', '-7 days')")
    new_7d = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= datetime('now', '-30 days')")
    new_30d = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_banned=0")
    active_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE balance > 0")
    paying = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(total_deposited),0) FROM users")
    total_money = c.fetchone()[0]
    
    # Activity last 24h, 7d, 30d (users who made orders)
    c.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE created_at >= datetime('now', '-1 day')")
    active_24h = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE created_at >= datetime('now', '-7 days')")
    active_7d = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE created_at >= datetime('now', '-30 days')")
    active_30d = c.fetchone()[0]
    
    conn.close()
    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_24h": new_24h,
        "new_7d": new_7d,
        "new_30d": new_30d,
        "paying": paying,
        "total_money": total_money,
        "active_24h": active_24h,
        "active_7d": active_7d,
        "active_30d": active_30d,
    }

def get_faq():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM faq")
    rows = c.fetchall()
    conn.close()
    return rows

def add_faq(question, answer):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO faq (question, answer) VALUES (?,?)", (question, answer))
    conn.commit()
    conn.close()

def delete_faq(faq_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM faq WHERE id=?", (faq_id,))
    conn.commit()
    conn.close()

# ===================== KEYBOARDS =====================
def main_menu(is_admin=False):
    kb = ReplyKeyboardBuilder()
    kb.button(text="🛒 Buyurtma berish")
    kb.button(text="📦 Buyurtmalar")
    kb.button(text="👤 Hisobim")
    kb.button(text="💰 Hisob to'ldirish")
    kb.button(text="💵 Pul ishlash")
    kb.button(text="🆘 Murojaat")
    kb.button(text="📚 Qo'llanma")
    if is_admin:
        kb.button(text="🖥 Boshqaruv")
    kb.adjust(1, 2, 2, 2, 1) if is_admin else kb.adjust(1, 2, 2, 2)
    return kb.as_markup(resize_keyboard=True)

def admin_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📊 Statistika")
    kb.button(text="👥 Foydalanuvchilar")
    kb.button(text="📝 Buyurtmalar")
    kb.button(text="🌐 Tarmoqlar")
    kb.button(text="📚 Qo'llanmalar")
    kb.button(text="📢 Xabar yuborish")
    kb.button(text="◀️ Orqaga")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup(resize_keyboard=True)

def networks_keyboard(networks, back=False):
    kb = InlineKeyboardBuilder()
    for n in networks:
        kb.button(text=n[1], callback_data=f"net_{n[0]}")
    if back:
        kb.button(text="➕ Qo'shish", callback_data="admin_add_network")
    kb.adjust(2)
    return kb.as_markup()

def order_networks_keyboard(networks):
    kb = InlineKeyboardBuilder()
    for n in networks:
        kb.button(text=n[1], callback_data=f"order_net_{n[0]}")
    kb.adjust(2)
    return kb.as_markup()

def categories_keyboard(cats, network_id):
    kb = InlineKeyboardBuilder()
    for cat in cats:
        kb.button(text=cat[2], callback_data=f"order_cat_{cat[0]}")
    kb.button(text="◀️ Orqaga", callback_data="order_back_net")
    kb.adjust(1)
    return kb.as_markup()

def services_keyboard(services, cat_id):
    kb = InlineKeyboardBuilder()
    for s in services:
        speed = "⚡-Tezkor" if s[4] > 5000 else "🐢-Sekin"
        kb.button(text=f"{s[3]} [{speed}]", callback_data=f"order_srv_{s[0]}")
    kb.button(text="◀️ Orqaga", callback_data=f"order_back_cat_{cat_id}")
    kb.adjust(1)
    return kb.as_markup()

def service_confirm_keyboard(service_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Buyurtma berish", callback_data=f"order_confirm_{service_id}")
    kb.button(text="◀️ Orqaga", callback_data="order_back_services")
    kb.adjust(1)
    return kb.as_markup()

def back_keyboard(cb_data="back_main"):
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data=cb_data)
    return kb.as_markup()

def topup_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Click / Payme orqali", callback_data="topup_card")
    kb.button(text="◀️ Orqaga", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

# ===================== STATES =====================
class OrderState(StatesGroup):
    select_network = State()
    select_category = State()
    select_service = State()
    enter_link = State()
    enter_quantity = State()
    confirm = State()

class TopupState(StatesGroup):
    enter_amount = State()
    confirm_payment = State()

class AdminState(StatesGroup):
    add_network = State()
    add_category_net = State()
    add_category_name = State()
    add_service_cat = State()
    add_service_api = State()
    add_service_name = State()
    add_service_price = State()
    add_service_min = State()
    add_service_max = State()
    add_service_desc = State()
    broadcast = State()
    find_user = State()
    add_money_user = State()
    add_money_amount = State()
    remove_money_user = State()
    remove_money_amount = State()
    add_faq_q = State()
    add_faq_a = State()
    topup_confirm = State()
    topup_user = State()
    topup_amount = State()
    edit_order_id = State()
    edit_order_status = State()

class ContactState(StatesGroup):
    message = State()

class FaqState(StatesGroup):
    select = State()

# ===================== HANDLERS =====================

# /start
@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or ""
    
    # Check referral
    args = message.text.split()
    referral_id = None
    if len(args) > 1:
        try:
            referral_id = int(args[1])
        except:
            pass
    
    if not get_user(user_id):
        create_user(user_id, username, full_name, referral_id)
    
    is_admin = user_id in ADMIN_IDS
    await message.answer(
        f"🖥 Asosiy menyudasiz!",
        reply_markup=main_menu(is_admin)
    )

# ===================== BUYURTMA BERISH =====================
@dp.message(F.text == "🛒 Buyurtma berish")
async def order_start(message: types.Message, state: FSMContext):
    await state.clear()
    networks = get_networks()
    if not networks:
        await message.answer("Hozircha tarmoqlar yo'q.")
        return
    await message.answer(
        "Quyidagi ijtimoiy tarmoqlardan birini tanlang.",
        reply_markup=order_networks_keyboard(networks)
    )
    await state.set_state(OrderState.select_network)

@dp.callback_query(F.data.startswith("order_net_"), OrderState.select_network)
async def order_select_network(callback: types.CallbackQuery, state: FSMContext):
    net_id = int(callback.data.split("_")[2])
    cats = get_categories(net_id)
    await state.update_data(net_id=net_id)
    
    if not cats:
        await callback.answer("Bu tarmoqda bo'limlar yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "Quyidagi bo'limlardan birini tanlang.\n(Narxlar 1000 tasi uchun berilgan)",
        reply_markup=categories_keyboard(cats, net_id)
    )
    await state.set_state(OrderState.select_category)

@dp.callback_query(F.data == "order_back_net")
async def order_back_net(callback: types.CallbackQuery, state: FSMContext):
    networks = get_networks()
    await callback.message.edit_text(
        "Quyidagi ijtimoiy tarmoqlardan birini tanlang.",
        reply_markup=order_networks_keyboard(networks)
    )
    await state.set_state(OrderState.select_network)

@dp.callback_query(F.data.startswith("order_cat_"), OrderState.select_category)
async def order_select_category(callback: types.CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    services = get_services(cat_id)
    await state.update_data(cat_id=cat_id)
    
    if not services:
        await callback.answer("Bu bo'limda xizmatlar yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "Xizmat APIni tanlang:",
        reply_markup=services_keyboard(services, cat_id)
    )
    await state.set_state(OrderState.select_service)

@dp.callback_query(F.data.startswith("order_back_cat_"))
async def order_back_cat(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    net_id = data.get("net_id", 0)
    cats = get_categories(net_id)
    await callback.message.edit_text(
        "Quyidagi bo'limlardan birini tanlang.\n(Narxlar 1000 tasi uchun berilgan)",
        reply_markup=categories_keyboard(cats, net_id)
    )
    await state.set_state(OrderState.select_category)

@dp.callback_query(F.data == "order_back_services")
async def order_back_services(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cat_id = data.get("cat_id", 0)
    services = get_services(cat_id)
    await callback.message.edit_text(
        "Xizmat APIni tanlang:",
        reply_markup=services_keyboard(services, cat_id)
    )
    await state.set_state(OrderState.select_service)

@dp.callback_query(F.data.startswith("order_srv_"), OrderState.select_service)
async def order_select_service(callback: types.CallbackQuery, state: FSMContext):
    srv_id = int(callback.data.split("_")[2])
    srv = get_service(srv_id)
    if not srv:
        await callback.answer("Xizmat topilmadi!", show_alert=True)
        return
    
    # srv: id, cat_id, api_id, name, price_per_1000, min_qty, max_qty, description
    speed = "⚡-Tezkor" if srv[4] > 5000 else "🐢-Sekin"
    
    # Get network name
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT n.name, cat.name FROM categories cat 
                 JOIN networks n ON cat.network_id=n.id 
                 WHERE cat.id=?""", (srv[1],))
    row = c.fetchone()
    conn.close()
    net_name = row[0] if row else ""
    cat_name = row[1] if row else ""
    
    desc = srv[7] if srv[7] else "Yo'q 💬"
    
    text = (
        f"{net_name} - 👤 {cat_name} [ {speed} ]\n\n"
        f"💰 Narxi (1000x): {srv[4]} So'm\n\n"
        f"| {desc}\n\n"
        f"⬇️ Minimal: {srv[5]} ta\n"
        f"⬆️ Maksimal: {srv[6]} ta"
    )
    
    await state.update_data(srv_id=srv_id, srv=srv, net_name=net_name, cat_name=cat_name)
    await callback.message.edit_text(text, reply_markup=service_confirm_keyboard(srv_id))

@dp.callback_query(F.data.startswith("order_confirm_"))
async def order_enter_link(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔗 Havola (link) ni kiriting:")
    await state.set_state(OrderState.enter_link)

@dp.message(OrderState.enter_link)
async def order_link_entered(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    srv = get_service(data["srv_id"])
    
    await message.answer(
        f"📊 Buyurtma miqdorini kiriting:\n\n"
        f"⬇️ Minimal: {srv[5]} ta\n"
        f"⬆️ Maksimal: {srv[6]} ta"
    )
    await state.set_state(OrderState.enter_quantity)

@dp.message(OrderState.enter_quantity)
async def order_quantity_entered(message: types.Message, state: FSMContext):
    try:
        qty = int(message.text.strip())
    except:
        await message.answer("❌ Noto'g'ri son. Qaytadan kiriting:")
        return
    
    data = await state.get_data()
    srv = get_service(data["srv_id"])
    
    if qty < srv[5] or qty > srv[6]:
        await message.answer(f"❌ Miqdor {srv[5]} dan {srv[6]} gacha bo'lishi kerak!")
        return
    
    price = int(qty * srv[4] / 1000)
    balance = get_balance(message.from_user.id)
    
    if balance < price:
        kb = InlineKeyboardBuilder()
        kb.button(text="💳 Hisobni to'ldirish", callback_data="goto_topup")
        await message.answer(
            f"⚠️ Hisobingizda yetarli mablag' mavjud emas!\n\n"
            f"💰 Narxi: {price} So'm\n"
            f"📊 Miqdor: {qty} ta\n\n"
            f"Boshqa miqdor kiritib ko'ring:",
            reply_markup=kb.as_markup()
        )
        return
    
    await state.update_data(qty=qty, price=price)
    
    # Confirm order
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data="order_final_confirm")
    kb.button(text="❌ Bekor qilish", callback_data="order_cancel")
    kb.adjust(2)
    
    await message.answer(
        f"📋 Buyurtma ma'lumotlari:\n\n"
        f"🌐 Tarmoq: {data['net_name']}\n"
        f"📂 Bo'lim: {data['cat_name']}\n"
        f"🔗 Havola: {data['link']}\n"
        f"📊 Miqdor: {qty} ta\n"
        f"💰 Narxi: {price} So'm\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=kb.as_markup()
    )
    await state.set_state(OrderState.confirm)

@dp.callback_query(F.data == "order_final_confirm", OrderState.confirm)
async def order_final_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    
    order_id = create_order(user_id, data["srv_id"], data["link"], data["qty"], data["price"])
    
    await state.clear()
    await callback.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"🆔 Buyurtma ID si: {order_id}\n\n"
        f"⏳ To'lovingiz 5 daqiqadan 24 soatgacha bo'lgan vaqt ichida amalga oshiriladi!"
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🆕 Yangi buyurtma!\n\n"
                f"🆔 ID: {order_id}\n"
                f"👤 Foydalanuvchi: {user_id}\n"
                f"🌐 Tarmoq: {data['net_name']}\n"
                f"📂 Bo'lim: {data['cat_name']}\n"
                f"🔗 Havola: {data['link']}\n"
                f"📊 Miqdor: {data['qty']} ta\n"
                f"💰 Narxi: {data['price']} So'm"
            )
        except:
            pass

@dp.callback_query(F.data == "order_cancel")
async def order_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")

@dp.callback_query(F.data == "goto_topup")
async def goto_topup(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💳 Hisobni to'ldirish uchun quyidagi ma'lumotlarni yuboramiz.\n\nTo'ldirish miqdorini kiriting (minimal 1000 So'm):"
    )
    await state.set_state(TopupState.enter_amount)

# ===================== BUYURTMALAR =====================
@dp.message(F.text == "📦 Buyurtmalar")
async def my_orders(message: types.Message):
    orders = get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📦 Sizda hali buyurtmalar yo'q.")
        return
    
    text = "📦 So'nggi 10 ta buyurtmalaringiz:\n\n"
    for o in orders:
        status_emoji = "⏳" if o[5] == "Bajarilmoqda" else "✅" if o[5] == "Bajarildi" else "❌"
        text += (
            f"🆔 ID: {o[0]}\n"
            f"🌐 {o[1]} - {o[2]}\n"
            f"{status_emoji} Holat: {o[5]}\n"
            f"🔗 {o[6]}\n"
            f"📊 {o[3]} ta | 💰 {o[4]} So'm\n"
            f"📅 {o[7][:16]}\n\n"
        )
    
    kb = ReplyKeyboardBuilder()
    kb.button(text="◀️ Orqaga")
    await message.answer(text, reply_markup=kb.as_markup(resize_keyboard=True))

# ===================== HISOBIM =====================
@dp.message(F.text == "👤 Hisobim")
async def my_account(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if not user:
        await message.answer("Foydalanuvchi topilmadi.")
        return
    
    balance = get_balance(user_id)
    orders = get_order_count(user_id)
    refs = get_referral_count(user_id)
    deposited = get_total_deposited(user_id)
    
    text = (
        f"👤 Sizning ID raqamingiz: {user_id}\n\n"
        f"💰 Balansingiz: {balance} So'm\n"
        f"📦 Buyurtmalaringiz: {orders} ta\n"
        f"👥 Referallaringiz: {refs} ta\n"
        f"💵 Kiritgan pullaringiz: {deposited} So'm"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Hisobni to'ldirish", callback_data="topup_start")
    await message.answer(text, reply_markup=kb.as_markup())

# ===================== HISOB TO'LDIRISH =====================
@dp.message(F.text == "💰 Hisob to'ldirish")
async def topup_start_msg(message: types.Message, state: FSMContext):
    await message.answer(
        "💳 Hisobni to'ldirish\n\nTo'ldirish miqdorini kiriting (minimal 1000 So'm):"
    )
    await state.set_state(TopupState.enter_amount)

@dp.callback_query(F.data == "topup_start")
async def topup_start_cb(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "💳 Hisobni to'ldirish\n\nTo'ldirish miqdorini kiriting (minimal 1000 So'm):"
    )
    await state.set_state(TopupState.enter_amount)

@dp.message(TopupState.enter_amount)
async def topup_amount_entered(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except:
        await message.answer("❌ Noto'g'ri miqdor. Qaytadan kiriting:")
        return
    
    if amount < 1000:
        await message.answer("❌ Minimal miqdor 1000 So'm. Qaytadan kiriting:")
        return
    
    await state.update_data(amount=amount)
    
    # Payment instructions
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ To'lovni tasdiqlash", callback_data="topup_paid")
    kb.button(text="❌ Bekor qilish", callback_data="topup_cancel")
    kb.adjust(2)
    
    await message.answer(
        f"💳 To'lov ma'lumotlari:\n\n"
        f"💰 Miqdor: {amount} So'm\n\n"
        f"📱 Click/Payme: +998901234567\n"
        f"👤 Ism: Admin\n\n"
        f"⚠️ To'lovni amalga oshirgach 'Tasdiqlash' tugmasini bosing.\n"
        f"Admin tekshirib, hisobingizni to'ldiradi!",
        reply_markup=kb.as_markup()
    )
    await state.set_state(TopupState.confirm_payment)

@dp.callback_query(F.data == "topup_paid", TopupState.confirm_payment)
async def topup_paid(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount", 0)
    user_id = callback.from_user.id
    
    await state.clear()
    await callback.message.edit_text(
        f"⏳ To'lovingiz adminга yuborildi. Tez orada hisobingiz to'ldiriladi!"
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Tasdiqlash", callback_data=f"admin_topup_ok_{user_id}_{amount}")
            kb.button(text="❌ Rad etish", callback_data=f"admin_topup_no_{user_id}")
            await bot.send_message(
                admin_id,
                f"💳 To'lov so'rovi!\n\n"
                f"👤 Foydalanuvchi ID: {user_id}\n"
                f"💰 Miqdor: {amount} So'm\n\n"
                f"Tasdiqlaysizmi?",
                reply_markup=kb.as_markup()
            )
        except:
            pass

@dp.callback_query(F.data == "topup_cancel")
async def topup_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ To'ldirish bekor qilindi.")

@dp.callback_query(F.data.startswith("admin_topup_ok_"))
async def admin_topup_ok(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    parts = callback.data.split("_")
    user_id = int(parts[3])
    amount = int(parts[4])
    
    update_balance(user_id, amount)
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET total_deposited=total_deposited+? WHERE user_id=?", (amount, user_id))
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?,?,'topup','Hisob to'ldirildi')", (user_id, amount))
    conn.commit()
    conn.close()
    
    await callback.message.edit_text(f"✅ {user_id} foydalanuvchiga {amount} So'm qo'shildi!")
    try:
        await bot.send_message(user_id, f"✅ Hisobingiz {amount} So'm ga to'ldirildi! 🎉")
    except:
        pass

@dp.callback_query(F.data.startswith("admin_topup_no_"))
async def admin_topup_no(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    user_id = int(callback.data.split("_")[3])
    await callback.message.edit_text(f"❌ {user_id} foydalanuvchining to'lovi rad etildi.")
    try:
        await bot.send_message(user_id, "❌ To'lovingiz rad etildi. Iltimos, admin bilan bog'laning.")
    except:
        pass

# ===================== PUL ISHLASH (REFERRAL) =====================
@dp.message(F.text == "💵 Pul ishlash")
async def earn_money(message: types.Message):
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    refs = get_referral_count(user_id)
    
    await message.answer(
        f"🔗 Sizning referal havolangiz:\n\n"
        f"{ref_link}\n\n"
        f"1 ta referal uchun 500 So'm beriladi\n\n"
        f"👥 Referallaringiz: {refs} ta"
    )

# ===================== MUROJAAT =====================
@dp.message(F.text == "🆘 Murojaat")
async def contact_admin(message: types.Message, state: FSMContext):
    await message.answer(
        "📝 Murojaat xabaringizni yozing. Admin ko'rib chiqadi:"
    )
    await state.set_state(ContactState.message)

@dp.message(ContactState.message)
async def contact_message(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"📩 Yangi murojaat!\n\n"
                f"👤 Foydalanuvchi: {message.from_user.full_name} (ID: {user_id})\n"
                f"📝 Xabar:\n{message.text}"
            )
        except:
            pass
    
    await message.answer("✅ Murojaat adminga yuborildi! Tez orada javob beriladi.")

# ===================== QO'LLANMA (FAQ) =====================
@dp.message(F.text == "📚 Qo'llanma")
async def faq_list(message: types.Message):
    faqs = get_faq()
    if not faqs:
        await message.answer("Hozircha qo'llanmalar yo'q.")
        return
    
    kb = InlineKeyboardBuilder()
    for f in faqs:
        kb.button(text=f[1][:30], callback_data=f"faq_{f[0]}")
    kb.adjust(1)
    
    await message.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("faq_"))
async def faq_answer(callback: types.CallbackQuery):
    faq_id = int(callback.data.split("_")[1])
    faqs = get_faq()
    for f in faqs:
        if f[0] == faq_id:
            await callback.message.answer(f"❓ {f[1]}\n\n💬 {f[2]}")
            return
    await callback.answer("Topilmadi!")

# ===================== ADMIN PANEL =====================
@dp.message(F.text == "🖥 Boshqaruv")
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=admin_menu())

@dp.message(F.text == "◀️ Orqaga")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_menu(is_admin))

# --- Admin: Statistika ---
@dp.message(F.text == "📊 Statistika")
async def admin_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    stats = get_stats()
    bot_info = await bot.get_me()
    
    text = (
        f"📊 Statistika\n"
        f"• Obunachilar soni: {stats['total_users']} ta\n"
        f"• Faol obunachilar: {stats['active_users']} ta\n"
        f"• Tark etganlar: {stats['total_users'] - stats['active_users']} ta\n\n"
        f"📈 Obunachilar qo'shilishi\n"
        f"• Oxirgi 24 soat: +{stats['new_24h']} obunachi\n"
        f"• Oxirgi 7 kun: +{stats['new_7d']} obunachi\n"
        f"• Oxirgi 30 kun: +{stats['new_30d']} obunachi\n\n"
        f"📊 Faollik\n"
        f"• Oxirgi 24 soatda faol: {stats['active_24h']} ta\n"
        f"• Oxirgi 7 kun faol: {stats['active_7d']} ta\n"
        f"• Oxirgi 30 kun faol: {stats['active_30d']} ta\n\n"
        f"💰 Pullar Statistikasi\n"
        f"• Puli borlar: {stats['paying']} ta\n"
        f"• Jami pullar: {stats['total_money']} So'm\n\n"
        f"🤖 @{bot_info.username}"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 TOP-50 Balans", callback_data="admin_top50_bal")
    kb.button(text="👥 TOP-50 Referal", callback_data="admin_top50_ref")
    await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin_top50_bal")
async def top50_balance(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, full_name, balance FROM users ORDER BY balance DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    
    text = "💰 TOP-50 Balans:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. {r[1] or r[0]} - {r[2]} So'm\n"
    
    await callback.message.answer(text[:4096])

@dp.callback_query(F.data == "admin_top50_ref")
async def top50_referral(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT u.user_id, u.full_name, COUNT(r.user_id) as ref_count 
                 FROM users u 
                 LEFT JOIN users r ON r.referral_id=u.user_id 
                 GROUP BY u.user_id 
                 ORDER BY ref_count DESC LIMIT 50""")
    rows = c.fetchall()
    conn.close()
    
    text = "👥 TOP-50 Referal:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. {r[1] or r[0]} - {r[2]} ta\n"
    
    await callback.message.answer(text[:4096])

# --- Admin: Foydalanuvchilar ---
@dp.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("👥 Foydalanuvchini boshqarish\n\nFoydalanuvchining ID raqamini yuboring:")
    await state.set_state(AdminState.find_user)

@dp.message(AdminState.find_user)
async def admin_find_user(message: types.Message, state: FSMContext):
    try:
        uid = int(message.text.strip())
    except:
        await message.answer("❌ Noto'g'ri ID. Qaytadan kiriting:")
        return
    
    user = get_user(uid)
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi!")
        await state.clear()
        return
    
    balance = get_balance(uid)
    refs = get_referral_count(uid)
    orders = get_order_count(uid)
    deposited = get_total_deposited(uid)
    
    text = (
        f"✅ Foydalanuvchi topildi!\n\n"
        f"🆔 ID raqami: {uid}\n"
        f"💰 Balansi: {balance} So'm\n"
        f"📦 Buyurtmalari: {orders} ta\n"
        f"👥 Referallari: {refs} ta\n"
        f"💵 Kiritgan pullar: {deposited} So'm"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔔 Banlash", callback_data=f"admin_ban_{uid}")
    kb.button(text="+ Pul qo'shish", callback_data=f"admin_add_money_{uid}")
    kb.button(text="— Pul ayirish", callback_data=f"admin_rem_money_{uid}")
    kb.adjust(1, 2)
    
    await state.clear()
    await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban_user(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    uid = int(callback.data.split("_")[2])
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    if row:
        new_status = 0 if row[0] else 1
        c.execute("UPDATE users SET is_banned=? WHERE user_id=?", (new_status, uid))
        conn.commit()
        status_text = "🔔 Banlandi" if new_status else "✅ Ban olib tashlandi"
        await callback.message.edit_text(f"{status_text}: {uid}")
    conn.close()

@dp.callback_query(F.data.startswith("admin_add_money_"))
async def admin_add_money(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    uid = int(callback.data.split("_")[3])
    await state.update_data(target_uid=uid)
    await callback.message.answer(f"({uid}) ning hisobiga qancha pul qo'shmoqchisiz?")
    await state.set_state(AdminState.add_money_amount)

@dp.message(AdminState.add_money_amount)
async def admin_add_money_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except:
        await message.answer("❌ Noto'g'ri miqdor!")
        return
    
    data = await state.get_data()
    uid = data["target_uid"]
    update_balance(uid, amount)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?,?,'admin_add','Admin qo'shdi')", (uid, amount))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(f"✅ Foydalanuvchi hisobiga {amount} So'm qo'shildi!")
    try:
        await bot.send_message(uid, f"💰 Hisobingizga {amount} So'm qo'shildi!")
    except:
        pass

@dp.callback_query(F.data.startswith("admin_rem_money_"))
async def admin_rem_money(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    uid = int(callback.data.split("_")[3])
    await state.update_data(target_uid=uid)
    await callback.message.answer(f"({uid}) ning hisobidan qancha pul ayirmoqchisiz?")
    await state.set_state(AdminState.remove_money_amount)

@dp.message(AdminState.remove_money_amount)
async def admin_rem_money_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
    except:
        await message.answer("❌ Noto'g'ri miqdor!")
        return
    
    data = await state.get_data()
    uid = data["target_uid"]
    update_balance(uid, -amount)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?,-?,'admin_remove','Admin ayirdi')", (uid, amount))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(f"✅ Foydalanuvchi hisobidan {amount} So'm ayirildi!")

# --- Admin: Buyurtmalar ---
@dp.message(F.text == "📝 Buyurtmalar")
async def admin_orders(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("📝 Kerakli buyurtma ID raqamini kiriting:")
    await state.set_state(AdminState.edit_order_id)

@dp.message(AdminState.edit_order_id)
async def admin_edit_order(message: types.Message, state: FSMContext):
    try:
        order_id = int(message.text.strip())
    except:
        await message.answer("❌ Noto'g'ri ID!")
        return
    
    order = get_order(order_id)
    if not order:
        await message.answer("❌ Buyurtma topilmadi!")
        await state.clear()
        return
    
    text = (
        f"🆔 Buyurtma IDsi: {order[0]}\n\n"
        f"{order[12]} - 👤 {order[13]} [ ⚡-Tezkor ]\n\n"
        f"♻️ Holat: ⏳ {order[6]}\n"
        f"🔗 Havola: {order[3]}\n"
        f"📊 Miqdor: {order[4]} ta\n"
        f"💰 Narxi: {order[5]} So'm\n\n"
        f"📅 Sana: {order[7]}"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Bajarildi", callback_data=f"admin_ord_done_{order_id}")
    kb.button(text="❌ Bekor qilish", callback_data=f"admin_ord_cancel_{order_id}")
    kb.adjust(2)
    
    await state.clear()
    await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("admin_ord_done_"))
async def admin_order_done(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    order_id = int(callback.data.split("_")[3])
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE orders SET status='Bajarildi' WHERE id=?", (order_id,))
    c.execute("SELECT user_id FROM orders WHERE id=?", (order_id,))
    row = c.fetchone()
    conn.commit()
    conn.close()
    
    await callback.message.edit_text(f"✅ Buyurtma #{order_id} bajarildi deb belgilandi!")
    if row:
        try:
            await bot.send_message(row[0], f"✅ Buyurtma #{order_id} bajarildi!")
        except:
            pass

@dp.callback_query(F.data.startswith("admin_ord_cancel_"))
async def admin_order_cancel(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    order_id = int(callback.data.split("_")[3])
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, price FROM orders WHERE id=?", (order_id,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE orders SET status='Bekor qilindi' WHERE id=?", (order_id,))
        # Refund
        c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (row[1], row[0]))
        c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?,?,'refund',?)",
                  (row[0], row[1], f"Buyurtma #{order_id} qaytarildi"))
        conn.commit()
    conn.close()
    
    await callback.message.edit_text(f"❌ Buyurtma #{order_id} bekor qilindi va pul qaytarildi!")
    if row:
        try:
            await bot.send_message(row[0], 
                f"🔴 {order_id} buyurtma bekor qilindi.\n\n"
                f"💰 {row[1]} So'm qaytarildi.")
        except:
            pass

# --- Admin: Tarmoqlar boshqaruv ---
@dp.message(F.text == "🌐 Tarmoqlar")
async def admin_networks(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    networks = get_networks()
    kb = InlineKeyboardBuilder()
    for n in networks:
        kb.button(text=n[1], callback_data=f"admin_net_{n[0]}")
    kb.button(text="➕ Tarmoq qo'shish", callback_data="admin_add_net")
    kb.adjust(2, 1)
    
    await message.answer("🌐 Tarmoqlar:", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin_add_net")
async def admin_add_net(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.answer("Yangi ijtimoiy tarmoq nomini kiriting:")
    await state.set_state(AdminState.add_network)

@dp.message(AdminState.add_network)
async def admin_add_network_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO networks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    await state.clear()
    await message.answer(f"✅ {name} - ijtimoiy tarmoqi muvaffaqiyatli qo'shildi!")

@dp.callback_query(F.data.startswith("admin_net_"))
async def admin_net_detail(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    net_id = int(callback.data.split("_")[2])
    cats = get_categories(net_id)
    
    kb = InlineKeyboardBuilder()
    for cat in cats:
        kb.button(text=cat[2], callback_data=f"admin_cat_{cat[0]}")
    kb.button(text="➕ Bo'lim qo'shish", callback_data=f"admin_add_cat_{net_id}")
    kb.button(text="◀️ Orqaga", callback_data="admin_back_nets")
    kb.adjust(1)
    
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name FROM networks WHERE id=?", (net_id,))
    row = c.fetchone()
    conn.close()
    net_name = row[0] if row else ""
    
    await callback.message.edit_text(f"🌐 {net_name} - bo'limlari:", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin_back_nets")
async def admin_back_nets(callback: types.CallbackQuery):
    networks = get_networks()
    kb = InlineKeyboardBuilder()
    for n in networks:
        kb.button(text=n[1], callback_data=f"admin_net_{n[0]}")
    kb.button(text="➕ Tarmoq qo'shish", callback_data="admin_add_net")
    kb.adjust(2, 1)
    await callback.message.edit_text("🌐 Tarmoqlar:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("admin_add_cat_"))
async def admin_add_cat_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    net_id = int(callback.data.split("_")[3])
    await state.update_data(net_id=net_id)
    await callback.message.answer("Yangi bo'lim nomini kiriting:")
    await state.set_state(AdminState.add_category_name)

@dp.message(AdminState.add_category_name)
async def admin_add_cat_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    net_id = data["net_id"]
    name = message.text.strip()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO categories (network_id, name) VALUES (?,?)", (net_id, name))
    conn.commit()
    conn.close()
    await state.clear()
    await message.answer(f"✅ {name} - bo'limi muvaffaqiyatli qo'shildi!")

@dp.callback_query(F.data.startswith("admin_cat_"))
async def admin_cat_detail(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    cat_id = int(callback.data.split("_")[2])
    services = get_services(cat_id)
    
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, network_id FROM categories WHERE id=?", (cat_id,))
    row = c.fetchone()
    conn.close()
    cat_name = row[0] if row else ""
    net_id = row[1] if row else 0
    
    kb = InlineKeyboardBuilder()
    for srv in services:
        kb.button(text=srv[3], callback_data=f"admin_srv_{srv[0]}")
    kb.button(text="➕ Xizmat qo'shish", callback_data=f"admin_add_srv_{cat_id}")
    kb.button(text="◀️ Orqaga", callback_data=f"admin_net_{net_id}")
    kb.adjust(1)
    
    await callback.message.edit_text(f"📂 {cat_name} - xizmatlari:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("admin_add_srv_"))
async def admin_add_srv_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    cat_id = int(callback.data.split("_")[3])
    await state.update_data(cat_id=cat_id)
    await callback.message.answer("Xizmat IDsini kiriting (API ID):")
    await state.set_state(AdminState.add_service_api)

@dp.message(AdminState.add_service_api)
async def admin_add_srv_api(message: types.Message, state: FSMContext):
    await state.update_data(api_id=message.text.strip())
    await message.answer("Xizmat nomini kiriting:")
    await state.set_state(AdminState.add_service_name)

@dp.message(AdminState.add_service_name)
async def admin_add_srv_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Xizmat narxini kiriting (1000 tasi uchun, So'mda):")
    await state.set_state(AdminState.add_service_price)

@dp.message(AdminState.add_service_price)
async def admin_add_srv_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text.strip())
        await state.update_data(price=price)
        await message.answer("Minimal miqdorni kiriting:")
        await state.set_state(AdminState.add_service_min)
    except:
        await message.answer("❌ Noto'g'ri narx!")

@dp.message(AdminState.add_service_min)
async def admin_add_srv_min(message: types.Message, state: FSMContext):
    try:
        min_qty = int(message.text.strip())
        await state.update_data(min_qty=min_qty)
        await message.answer("Maksimal miqdorni kiriting:")
        await state.set_state(AdminState.add_service_max)
    except:
        await message.answer("❌ Noto'g'ri son!")

@dp.message(AdminState.add_service_max)
async def admin_add_srv_max(message: types.Message, state: FSMContext):
    try:
        max_qty = int(message.text.strip())
        await state.update_data(max_qty=max_qty)
        await message.answer("Xizmat haqida ma'lumot kiriting (yo'q bo'lsa 'Yo'q' deb yozing):")
        await state.set_state(AdminState.add_service_desc)
    except:
        await message.answer("❌ Noto'g'ri son!")

@dp.message(AdminState.add_service_desc)
async def admin_add_srv_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    desc = message.text.strip()
    if desc.lower() in ["yo'q", "yoq", "no", "-"]:
        desc = ""
    
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO services (category_id, api_id, name, price_per_1000, min_qty, max_qty, description) VALUES (?,?,?,?,?,?,?)",
              (data["cat_id"], data["api_id"], data["name"], data["price"], data["min_qty"], data["max_qty"], desc))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(f"✅ {data['name']} - xizmati muvaffaqiyatli qo'shildi!")

# --- Admin: Broadcast ---
@dp.message(F.text == "📢 Xabar yuborish")
async def admin_broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni yozing:")
    await state.set_state(AdminState.broadcast)

@dp.message(AdminState.broadcast)
async def admin_broadcast_send(message: types.Message, state: FSMContext):
    await state.clear()
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = c.fetchall()
    conn.close()
    
    sent = 0
    failed = 0
    for u in users:
        try:
            await bot.send_message(u[0], message.text)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await message.answer(f"✅ Xabar yuborildi!\n\n✅ Muvaffaqiyatli: {sent}\n❌ Xato: {failed}")

# --- Admin: Qo'llanmalar ---
@dp.message(F.text == "📚 Qo'llanmalar")
async def admin_faq(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    faqs = get_faq()
    
    kb = InlineKeyboardBuilder()
    for f in faqs:
        kb.button(text=f"❌ {f[1][:20]}", callback_data=f"admin_del_faq_{f[0]}")
    kb.button(text="➕ Qo'llanma qo'shish", callback_data="admin_add_faq")
    kb.adjust(1)
    
    await message.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=kb.as_markup())

@dp.callback_query(F.data == "admin_add_faq")
async def admin_add_faq_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.answer("Qo'llanma uchun nom kiriting:")
    await state.set_state(AdminState.add_faq_q)

@dp.message(AdminState.add_faq_q)
async def admin_add_faq_q(message: types.Message, state: FSMContext):
    await state.update_data(faq_q=message.text.strip())
    await message.answer("Qo'llanma mazmunini kiriting:")
    await state.set_state(AdminState.add_faq_a)

@dp.message(AdminState.add_faq_a)
async def admin_add_faq_a(message: types.Message, state: FSMContext):
    data = await state.get_data()
    add_faq(data["faq_q"], message.text.strip())
    await state.clear()
    await message.answer("✅ Qo'llanma muvaffaqiyatli qo'shildi!")

@dp.callback_query(F.data.startswith("admin_del_faq_"))
async def admin_del_faq(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    faq_id = int(callback.data.split("_")[3])
    delete_faq(faq_id)
    await callback.message.edit_text("✅ Qo'llanma muvaffaqiyatli o'chirildi!")

# ===================== MAIN =====================
async def main():
    init_db()
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
