import logging
import asyncio
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ========================
# SOZLAMALAR
# ========================
BOT_TOKEN = "8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o"   # @BotFather dan oling
ADMIN_ID  = 8537782289                # Sizning Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

# ========================
# DATABASE
# ========================
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id   INTEGER PRIMARY KEY,
        username  TEXT,
        full_name TEXT,
        balance   REAL DEFAULT 0,
        joined_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS social_networks (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        name       TEXT,
        added_at   TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        network    TEXT,
        service    TEXT,
        quantity   INTEGER,
        price      REAL,
        status     TEXT DEFAULT 'pending',
        created_at TEXT
    )""")
    conn.commit()
    conn.close()

def reg_user(user_id, username, full_name):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id,username,full_name,balance,joined_at) VALUES(?,?,?,0,?)",
              (user_id, username or "", full_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone(); conn.close()
    return row[0] if row else 0

def add_balance(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
    conn.commit(); conn.close()

def get_networks(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM social_networks WHERE user_id=?", (user_id,))
    rows = c.fetchall(); conn.close()
    return rows

def add_network(user_id, name):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO social_networks (user_id,name,added_at) VALUES(?,?,?)",
              (user_id, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

def get_orders(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall(); conn.close()
    return rows

def create_order(user_id, network, service, quantity, price):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id,network,service,quantity,price,status,created_at) VALUES(?,?,?,?,?,'pending',?)",
              (user_id, network, service, quantity, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    oid = c.lastrowid; conn.commit(); conn.close()
    return oid

def get_all_users():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall(); conn.close()
    return rows

# ========================
# STATES
# ========================
class AddNetwork(StatesGroup):
    entering_name = State()

class OrderFlow(StatesGroup):
    choosing_network = State()
    choosing_service = State()
    entering_quantity = State()
    confirming       = State()

class TopUp(StatesGroup):
    entering_amount  = State()
    sending_receipt  = State()

class Broadcast(StatesGroup):
    entering_message = State()

# ========================
# XIZMATLAR
# ========================
SERVICES = {
    "Instagram": {
        "Followers": {"price": 5000,  "min": 100,  "max": 10000},
        "Likes":     {"price": 2000,  "min": 50,   "max": 5000},
        "Views":     {"price": 1000,  "min": 100,  "max": 50000},
    },
    "YouTube": {
        "Subscribers": {"price": 10000, "min": 100,  "max": 5000},
        "Views":       {"price": 3000,  "min": 500,  "max": 100000},
        "Likes":       {"price": 5000,  "min": 50,   "max": 5000},
    },
    "Telegram": {
        "Members":    {"price": 8000,  "min": 100,  "max": 10000},
        "Post Views": {"price": 1500,  "min": 100,  "max": 50000},
    },
    "TikTok": {
        "Followers":  {"price": 7000,  "min": 100,  "max": 10000},
        "Likes":      {"price": 3000,  "min": 100,  "max": 10000},
        "Views":      {"price": 1500,  "min": 1000, "max": 100000},
    },
}

# ========================
# KLAVIATURALAR
# ========================
def main_kb(user_id=None):
    b = ReplyKeyboardBuilder()
    b.button(text="Buyurtma berish")
    b.button(text="Buyurtmalar");      b.button(text="Hisobim")
    b.button(text="Pul ishlash");      b.button(text="Hisob to'ldirish")
    b.button(text="Murojaat");         b.button(text="Qo'llanma")
    if user_id and user_id == ADMIN_ID:
        b.button(text="🖥 Boshqaruv")
    b.adjust(1, 2, 2, 1, 1)
    return b.as_markup(resize_keyboard=True)

def back_kb():
    b = ReplyKeyboardBuilder()
    b.button(text="Orqaga")
    return b.as_markup(resize_keyboard=True)

def networks_inline_kb(user_id):
    networks = get_networks(user_id)
    b = InlineKeyboardBuilder()
    for nid, name in networks:
        b.button(text=name, callback_data=f"net_{nid}_{name}")
    b.button(text="➕ Qo'shish", callback_data="add_network")
    b.adjust(2)
    return b.as_markup(), networks

def services_kb(platform):
    b = ReplyKeyboardBuilder()
    for svc in SERVICES.get(platform, {}).keys():
        b.button(text=svc)
    b.button(text="Orqaga")
    b.adjust(2)
    return b.as_markup(resize_keyboard=True)

def confirm_kb():
    b = InlineKeyboardBuilder()
    b.button(text="✅ Tasdiqlash",   callback_data="order_confirm")
    b.button(text="❌ Bekor qilish", callback_data="order_cancel")
    b.adjust(2)
    return b.as_markup()

def admin_kb():
    b = ReplyKeyboardBuilder()
    b.button(text="👥 Foydalanuvchilar"); b.button(text="📊 Statistika")
    b.button(text="📢 Xabar yuborish");   b.button(text="Orqaga")
    b.adjust(2, 1, 1)
    return b.as_markup(resize_keyboard=True)

# ========================
# /start
# ========================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    u = message.from_user
    reg_user(u.id, u.username, u.full_name)
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(u.id))

# ========================
# BUYURTMA BERISH
# ========================
@dp.message(F.text == "Buyurtma berish")
async def order_start(message: types.Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    kb, networks = networks_inline_kb(uid)

    if not networks:
        # Videodagi kabi: "Ijtimoiy tarmoqlar mavjud emas!" + "➕ Qo'shish" tugmasi
        b = InlineKeyboardBuilder()
        b.button(text="➕ Qo'shish", callback_data="add_network")
        await message.answer(
            "⚠️ Ijtimoiy tarmoqlar mavjud emas!",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer("Yangi tarmoq qo'shish:", reply_markup=b.as_markup())
    else:
        await message.answer(
            "📱 Ijtimoiy tarmoqni tanlang:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer("Tarmoqlar:", reply_markup=kb)

    await state.set_state(OrderFlow.choosing_network)

# ========================
# TARMOQ QO'SHISH
# ========================
@dp.callback_query(F.data == "add_network")
async def cb_add_network(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "✏️ Yangi ijtimoiy tarmoq nomini kiriting:",
        reply_markup=back_kb()
    )
    await state.set_state(AddNetwork.entering_name)

@dp.message(AddNetwork.entering_name)
async def add_network_name(message: types.Message, state: FSMContext):
    if message.text == "Orqaga":
        await state.clear()
        await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(message.from_user.id))
        return

    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Nom bo'sh bo'lmasin!")
        return

    add_network(message.from_user.id, name)
    await message.answer(f"✅ «{name}» qo'shildi!", reply_markup=main_kb(message.from_user.id))
    await state.clear()

# ========================
# TARMOQ TANLASH
# ========================
@dp.callback_query(F.data.startswith("net_"), OrderFlow.choosing_network)
async def cb_network_chosen(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    parts = callback.data.split("_", 2)
    name  = parts[2]

    if name in SERVICES:
        await state.update_data(network=name)
        await callback.message.answer(
            f"⚙️ *{name}* uchun xizmat tanlang:",
            parse_mode="Markdown",
            reply_markup=services_kb(name)
        )
        await state.set_state(OrderFlow.choosing_service)
    else:
        await callback.message.answer(
            f"⚠️ *{name}* uchun hozircha xizmatlar mavjud emas.\n"
            "Admin bilan bog'laning: @admin_username",
            parse_mode="Markdown",
            reply_markup=main_kb(callback.from_user.id)
        )
        await state.clear()

# ========================
# XIZMAT TANLASH
# ========================
@dp.message(OrderFlow.choosing_service)
async def choose_service(message: types.Message, state: FSMContext):
    if message.text == "Orqaga":
        await state.clear()
        await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(message.from_user.id))
        return

    data    = await state.get_data()
    network = data.get("network")

    if message.text not in SERVICES.get(network, {}):
        await message.answer("⚠️ Ro'yxatdan xizmat tanlang!")
        return

    info = SERVICES[network][message.text]
    await state.update_data(service=message.text)

    await message.answer(
        f"🔢 Miqdorni kiriting:\n\n"
        f"Min: {info['min']:,}  |  Max: {info['max']:,}\n"
        f"💰 Narx: {info['price']:,} so'm / 1000 ta",
        reply_markup=back_kb()
    )
    await state.set_state(OrderFlow.entering_quantity)

# ========================
# MIQDOR KIRITISH
# ========================
@dp.message(OrderFlow.entering_quantity)
async def enter_quantity(message: types.Message, state: FSMContext):
    if message.text == "Orqaga":
        data = await state.get_data()
        await message.answer("Xizmat tanlang:", reply_markup=services_kb(data.get("network")))
        await state.set_state(OrderFlow.choosing_service)
        return

    try:
        qty = int(message.text.replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("⚠️ Faqat raqam kiriting!")
        return

    data    = await state.get_data()
    network = data.get("network")
    service = data.get("service")
    info    = SERVICES[network][service]

    if qty < info["min"] or qty > info["max"]:
        await message.answer(f"⚠️ {info['min']:,} – {info['max']:,} oralig'ida kiriting!")
        return

    price   = (qty / 1000) * info["price"]
    balance = get_balance(message.from_user.id)
    await state.update_data(quantity=qty, price=price)

    text = (
        f"📋 *Buyurtma tafsilotlari:*\n\n"
        f"📱 Tarmoq: {network}\n"
        f"⚙️ Xizmat: {service}\n"
        f"🔢 Miqdor: {qty:,}\n"
        f"💰 Narx: {price:,.0f} so'm\n\n"
        f"💳 Balans: {balance:,.0f} so'm"
    )
    if balance < price:
        text += f"\n\n⚠️ *Mablag' yetarli emas!*\nYetishmaydi: {price - balance:,.0f} so'm"

    await message.answer(text, parse_mode="Markdown", reply_markup=confirm_kb())
    await state.set_state(OrderFlow.confirming)

# ========================
# TASDIQLASH
# ========================
@dp.callback_query(F.data == "order_confirm", OrderFlow.confirming)
async def order_confirm(callback: types.CallbackQuery, state: FSMContext):
    data    = await state.get_data()
    uid     = callback.from_user.id
    balance = get_balance(uid)
    price   = data["price"]

    if balance < price:
        await callback.answer("❌ Mablag' yetarli emas!", show_alert=True)
        return

    add_balance(uid, -price)
    oid = create_order(uid, data["network"], data["service"], data["quantity"], price)

    await callback.message.edit_text(
        f"✅ *Buyurtma qabul qilindi!*\n\n"
        f"🆔 #{oid}  |  {data['network']} — {data['service']}\n"
        f"🔢 {data['quantity']:,} ta  |  💰 {price:,.0f} so'm\n\n"
        f"⏳ Bajarilmoqda...",
        parse_mode="Markdown"
    )
    await state.clear()
    await callback.message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(uid))

    try:
        u = callback.from_user
        await bot.send_message(
            ADMIN_ID,
            f"🆕 *Yangi buyurtma #{oid}*\n"
            f"👤 {u.full_name} (@{u.username or '-'})\n"
            f"📱 {data['network']} — {data['service']}\n"
            f"🔢 {data['quantity']:,}  |  💰 {price:,.0f} so'm",
            parse_mode="Markdown"
        )
    except Exception:
        pass

@dp.callback_query(F.data == "order_cancel", OrderFlow.confirming)
async def order_cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await state.clear()
    await callback.message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(callback.from_user.id))

# ========================
# BUYURTMALAR
# ========================
@dp.message(F.text == "Buyurtmalar")
async def show_orders(message: types.Message):
    orders = get_orders(message.from_user.id)
    if not orders:
        await message.answer("📭 Hali buyurtmalar yo'q.")
        return
    emj = {"pending": "⏳", "processing": "🔄", "completed": "✅", "cancelled": "❌"}
    text = "📋 *Buyurtmalaringiz:*\n\n"
    for o in orders[:10]:
        oid, uid, net, svc, qty, price, status, created = o
        text += f"#{oid} {emj.get(status,'❓')} {net} — {svc}\n{qty:,} ta | {price:,.0f} so'm | {created[:10]}\n\n"
    await message.answer(text, parse_mode="Markdown")

# ========================
# HISOBIM
# ========================
@dp.message(F.text == "Hisobim")
async def show_balance(message: types.Message):
    bal    = get_balance(message.from_user.id)
    orders = get_orders(message.from_user.id)
    spent  = sum(o[5] for o in orders)
    await message.answer(
        f"💰 *Hisobim*\n\n"
        f"💳 Balans: *{bal:,.0f} so'm*\n"
        f"📊 Buyurtmalar: {len(orders)} ta\n"
        f"💸 Jami sarflangan: {spent:,.0f} so'm",
        parse_mode="Markdown"
    )

# ========================
# HISOB TO'LDIRISH
# ========================
@dp.message(F.text == "Hisob to'ldirish")
async def topup_start(message: types.Message, state: FSMContext):
    await message.answer(
        "💳 *Hisob to'ldirish*\n\n"
        "Karta raqami: *8600 1234 5678 9012*\n"
        "Egasi: *Azizbek*\n\n"
        "Qancha to'ldirmoqchisiz? (so'm):",
        parse_mode="Markdown",
        reply_markup=back_kb()
    )
    await state.set_state(TopUp.entering_amount)

@dp.message(TopUp.entering_amount)
async def topup_amount(message: types.Message, state: FSMContext):
    if message.text == "Orqaga":
        await state.clear()
        await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(message.from_user.id))
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
        f"✅ {amount:,} so'm o'tkazing va chek (screenshot) yuboring 👇",
        reply_markup=back_kb()
    )
    await state.set_state(TopUp.sending_receipt)

@dp.message(TopUp.sending_receipt, F.photo)
async def topup_receipt(message: types.Message, state: FSMContext):
    data   = await state.get_data()
    amount = data.get("amount")
    u      = message.from_user
    try:
        await bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=(
                f"💳 *To'lov so'rovi*\n"
                f"👤 {u.full_name} (@{u.username or '-'})\n"
                f"🆔 {u.id}\n"
                f"💰 {amount:,} so'm\n\n"
                f"Tasdiqlash: /topup_{u.id}_{amount}"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await message.answer(
        "✅ Chek qabul qilindi!\n5-30 daqiqa ichida to'ldiriladi.",
        reply_markup=main_kb(u.id)
    )
    await state.clear()

# ========================
# PUL ISHLASH
# ========================
@dp.message(F.text == "Pul ishlash")
async def earn(message: types.Message):
    uid = message.from_user.id
    await message.answer(
        "💸 *Pul ishlash*\n\n"
        "Do'stlaringizni taklif qiling!\n\n"
        f"Sizning havolangiz:\nhttps://t.me/YourBot?start={uid}",
        parse_mode="Markdown"
    )

# ========================
# MUROJAAT
# ========================
@dp.message(F.text == "Murojaat")
async def contact(message: types.Message):
    await message.answer(
        "📞 *Murojaat*\n\n"
        "👤 Admin: @admin_username\n"
        "⏰ 9:00 – 22:00",
        parse_mode="Markdown"
    )

# ========================
# QO'LLANMA
# ========================
@dp.message(F.text == "Qo'llanma")
async def guide(message: types.Message):
    await message.answer(
        "📖 *Qo'llanma*\n\n"
        "1️⃣ Hisob to'ldiring\n"
        "2️⃣ Buyurtma berish → tarmoq tanlang\n"
        "3️⃣ Xizmat va miqdorni kiriting\n"
        "4️⃣ Tasdiqlang — tayyor!\n\n"
        "❓ Savol: @admin_username",
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
        f"🖥 *Admin Panel*\n👥 Foydalanuvchilar: {len(users)} ta",
        parse_mode="Markdown",
        reply_markup=admin_kb()
    )

@dp.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    text  = f"👥 *Foydalanuvchilar ({len(users)} ta):*\n\n"
    for u in users[:20]:
        uid, uname, fname, bal, joined = u
        text += f"👤 {fname} | @{uname or '-'} | 💰 {bal:,.0f} so'm\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "📊 Statistika")
async def admin_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users     = get_all_users()
    total_bal = sum(u[3] for u in users)
    conn      = sqlite3.connect("bot.db")
    c         = conn.cursor()
    c.execute("SELECT COUNT(*), COALESCE(SUM(price),0) FROM orders WHERE status='completed'")
    done = c.fetchone()
    c.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
    pend = c.fetchone()[0]
    conn.close()
    await message.answer(
        f"📊 *Statistika*\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"💰 Jami balanslar: {total_bal:,.0f} so'm\n"
        f"✅ Bajarilgan: {done[0]} ta | {done[1]:,.0f} so'm\n"
        f"⏳ Kutayotgan: {pend} ta",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Xabarni kiriting:", reply_markup=back_kb())
    await state.set_state(Broadcast.entering_message)

@dp.message(Broadcast.entering_message)
async def broadcast_send(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if message.text == "Orqaga":
        await state.clear()
        await message.answer("🖥 Admin panel", reply_markup=admin_kb())
        return
    users = get_all_users()
    sent = failed = 0
    for u in users:
        try:
            await bot.send_message(u[0], message.text)
            sent += 1
        except Exception:
            failed += 1
    await message.answer(f"✅ {sent} yuborildi  ❌ {failed} yuborilmadi", reply_markup=admin_kb())
    await state.clear()

# Admin balans to'ldirish: /topup_USER_ID_AMOUNT
@dp.message(Command("topup"))
async def admin_topup(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split("_")
    if len(parts) != 3:
        await message.answer("Format: /topup_USER_ID_AMOUNT")
        return
    try:
        uid    = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("Xato format!")
        return
    add_balance(uid, amount)
    await message.answer(f"✅ {uid} ga {amount:,} so'm qo'shildi!")
    try:
        await bot.send_message(uid, f"✅ Hisobingizga *{amount:,} so'm* qo'shildi!", parse_mode="Markdown")
    except Exception:
        pass

# ========================
# ORQAGA (universal)
# ========================
@dp.message(F.text == "Orqaga")
async def back_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(message.from_user.id))

# ========================
# MAIN
# ========================
async def main():
    init_db()
    logging.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
