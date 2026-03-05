import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ================= SOZLAMALAR =================
BOT_TOKEN = "8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o"
ADMIN_ID = 8537782289 # O'ZINGIZNING TELEGRAM ID RAQAMINGIZNI YOZING
MIN_DEPOSIT = 1000
REF_BONUS = 100

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ================= BAZA SOZLAMALARI (SQLite) =================
conn = sqlite3.connect('nakrutka_bot.db', check_same_thread=False)
cursor = conn.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, ref_count INTEGER DEFAULT 0, 
    total_deposit INTEGER DEFAULT 0, inviter INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, card_number TEXT, details TEXT
);
CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id TEXT, url TEXT
);
CREATE TABLE IF NOT EXISTS guides (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, text TEXT
);
''')
conn.commit()

# ================= TUGMALAR (KEYBOARDS) =================
def user_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Buyurtma berish")],
            [KeyboardButton(text="👤 Hisobim"), KeyboardButton(text="💸 Pul ishlash")],[KeyboardButton(text="📩 Murojaat"), KeyboardButton(text="📖 Qo'llanma")]
        ], resize_keyboard=True
    )

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚙️ Asosiy sozlamalar")],[KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📣 Xabar yuborish")],[KeyboardButton(text="🔗 Majburiy obuna kanallar")],[KeyboardButton(text="💳 To'lov tizimlar"), KeyboardButton(text="🔑 API")],
            [KeyboardButton(text="👥 Foydalanuvchini boshqarish")],
            [KeyboardButton(text="📖 Qo'llanmalar"), KeyboardButton(text="📦 Buyurtmalar")]
        ], resize_keyboard=True
    )

cancel_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⏪ Orqaga")]], resize_keyboard=True)

# ================= HOLATLAR (STATES) =================
class DepositState(StatesGroup):
    amount = State()
    receipt = State()

class AdminUserState(StatesGroup):
    get_id = State()
    add_money = State()
    sub_money = State()

class AdminPaymentState(StatesGroup):
    name = State()
    card = State()
    details = State()

class AdminGuideState(StatesGroup):
    title = State()
    text = State()

class SupportState(StatesGroup):
    text = State()
    reply = State()

class BroadcastState(StatesGroup):
    text = State()

# ================= FOYDALANUVCHI BO'LIMI =================
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        inviter = 0
        args = message.text.split()
        if len(args) > 1 and args[1].isdigit() and int(args[1]) != user_id:
            inviter = int(args[1])
            cursor.execute("UPDATE users SET ref_count = ref_count + 1, balance = balance + ? WHERE id = ?", (REF_BONUS, inviter))
            await bot.send_message(inviter, f"🎉 Yangi referal qo'shildi! Sizga {REF_BONUS} so'm berildi.")
        cursor.execute("INSERT INTO users (id, inviter) VALUES (?, ?)", (user_id, inviter))
        conn.commit()
    
    if user_id == ADMIN_ID:
        await message.answer("👨‍💻 Admin paneliga xush kelibsiz!", reply_markup=admin_menu())
    else:
        await message.answer("Asosiy menyudasiz!", reply_markup=user_menu())

@dp.message(F.text == "⏪ Orqaga")
async def back_handler(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=admin_menu())
    else:
        await message.answer("Asosiy menyudasiz!", reply_markup=user_menu())

@dp.message(F.text == "👤 Hisobim")
async def my_account(message: Message):
    cursor.execute("SELECT balance, ref_count, total_deposit FROM users WHERE id = ?", (message.from_user.id,))
    user = cursor.fetchone()
    if user:
        text = f"👤 Sizning ID raqamingiz: <code>{message.from_user.id}</code>\n" \
               f"💰 Balansingiz: {user[0]} so'm\n" \
               f"📦 Buyurtmalaringiz: 0 ta\n" \
               f"👥 Referallaringiz: {user[1]} ta\n" \
               f"💳 Kiritgan pullaringiz: {user[2]} so'm"
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="add_funds")]
        ])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.message(F.text == "💸 Pul ishlash")
async def earn_money(message: Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    text = f"🔗 Sizning referal havolangiz:\n{ref_link}\n\n" \
           f"1 ta referal uchun {REF_BONUS} so'm beriladi!"
    await message.answer(text)

@dp.message(F.text == "📩 Murojaat")
async def support_msg(message: Message, state: FSMContext):
    await message.answer("Murojaat matnini yozib yuboring:", reply_markup=cancel_btn)
    await state.set_state(SupportState.text)

@dp.message(SupportState.text)
async def send_support(message: Message, state: FSMContext):
    if message.text == "⏪ Orqaga": return await back_handler(message, state)
    text = f"📩 Yangi murojaat!\nFoydalanuvchi: @{message.from_user.username} (<code>{message.from_user.id}</code>)\n\nXabar: {message.text}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Javob yozish", callback_data=f"reply_supp_{message.from_user.id}")]])
    await bot.send_message(ADMIN_ID, text, reply_markup=kb, parse_mode="HTML")
    await message.answer("Murojaatingiz qabul qilindi! Tez orada ko'rib chiqamiz.", reply_markup=user_menu())
    await state.clear()

@dp.message(F.text == "📖 Qo'llanma")
async def show_guides(message: Message):
    cursor.execute("SELECT title, text FROM guides")
    guides = cursor.fetchall()
    if not guides:
        await message.answer("Qo'llanmalar mavjud emas.")
    else:
        for g in guides:
            await message.answer(f"📌 <b>{g[0]}</b>\n\n{g[1]}", parse_mode="HTML")

@dp.message(F.text == "📦 Buyurtma berish")
async def new_order(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📷 Instagram", callback_data="order_ig"), InlineKeyboardButton(text="✈️ Telegram", callback_data="order_tg")],[InlineKeyboardButton(text="▶️ YouTube", callback_data="order_yt"), InlineKeyboardButton(text="🎵 TikTok", callback_data="order_tt")]
    ])
    await message.answer("Quyidagi ijtimoiy tarmoqlardan birini tanlang:", reply_markup=kb)

# --- HISOB TO'LDIRISH (To'lov cheki yuborish) ---
@dp.callback_query(F.data == "add_funds")
async def select_payment(call: CallbackQuery):
    cursor.execute("SELECT id, name FROM payments")
    payments = cursor.fetchall()
    if not payments:
        await call.message.answer("⚠️ To'lov tizimlari mavjud emas!")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=p[1], callback_data=f"pay_{p[0]}")] for p in payments
    ])
    await call.message.edit_text("Quyidagilardan birini tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("pay_"))
async def pay_amount(call: CallbackQuery, state: FSMContext):
    pay_id = call.data.split("_")[1]
    cursor.execute("SELECT name, card_number, details FROM payments WHERE id = ?", (pay_id,))
    pay_info = cursor.fetchone()
    
    text = f"💳 To'lov tizimi: {pay_info[0]}\n" \
           f"Karta: <code>{pay_info[1]}</code>\n" \
           f"Ma'lumot: {pay_info[2]}\n\n" \
           f"💳 To'lov qilib bo'lgach, to'lov miqdorini kiriting:\nMinimal: {MIN_DEPOSIT} so'm"
    await call.message.answer(text, parse_mode="HTML", reply_markup=cancel_btn)
    await state.update_data(pay_system=pay_info[0])
    await state.set_state(DepositState.amount)

@dp.message(DepositState.amount)
async def wait_receipt(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < MIN_DEPOSIT:
        return await message.answer(f"Xato! Minimal summa {MIN_DEPOSIT} so'm.")
    await state.update_data(amount=int(message.text))
    await message.answer("Muvaffaqiyatli! Endi to'lov chekini rasmga olib yuboring:")
    await state.set_state(DepositState.receipt)

@dp.message(DepositState.receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    pay_sys = data['pay_system']
    
    # Adminga yuborish
    caption = f"Foydalanuvchi hisobini to'ldirmoqchi!\n\n" \
              f"👤 Foydalanuvchi: <code>{message.from_user.id}</code>\n" \
              f"💳 Tizim: {pay_sys}\n" \
              f"💰 Miqdor: {amount} so'm"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_dep_{message.from_user.id}_{amount}"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"reject_dep_{message.from_user.id}")]
    ])
    await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode="HTML", reply_markup=kb)
    await message.answer("To'lovingiz 5-10 daqiqa ichida tekshirilib tasdiqlanadi.", reply_markup=user_menu())
    await state.clear()


# ================= ADMIN BO'LIMI =================
@dp.message(F.text == "📊 Statistika", F.from_user.id == ADMIN_ID)
async def admin_stats(message: Message):
    cursor.execute("SELECT COUNT(*), SUM(balance), SUM(total_deposit) FROM users")
    stats = cursor.fetchone()
    text = f"📊 <b>Statistika</b>\n\n" \
           f"👥 Obunachilar soni: {stats[0]} ta\n" \
           f"💰 Jami pullar (kiritilgan): {stats[2] or 0} so'm\n" \
           f"💳 Foydalanuvchilar balansi: {stats[1] or 0} so'm"
    await message.answer(text, parse_mode="HTML")

# --- XABAR YUBORISH ---
@dp.message(F.text == "📣 Xabar yuborish", F.from_user.id == ADMIN_ID)
async def ask_broadcast(message: Message, state: FSMContext):
    await message.answer("Yuboriladigan xabarni yozing (rasm/video ham bo'lishi mumkin):", reply_markup=cancel_btn)
    await state.set_state(BroadcastState.text)

@dp.message(BroadcastState.text, F.from_user.id == ADMIN_ID)
async def send_broadcast(message: Message, state: FSMContext):
    if message.text == "⏪ Orqaga": return await back_handler(message, state)
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    sent = 0
    await message.answer(f"Xabar yuborish boshlandi. Jami obunachilar: {len(users)} ta", reply_markup=admin_menu())
    for u in users:
        try:
            await message.copy_to(u[0])
            sent += 1
            await asyncio.sleep(0.05)
        except: pass
    await message.answer(f"✅ Xabar muvaffaqiyatli yuborildi!\nYetib bordi: {sent} ta")
    await state.clear()

# --- FOYDALANUVCHINI BOSHQARISH ---
@dp.message(F.text == "👥 Foydalanuvchini boshqarish", F.from_user.id == ADMIN_ID)
async def ask_user_id(message: Message, state: FSMContext):
    await message.answer("Foydalanuvchi ID raqamini yuboring:", reply_markup=cancel_btn)
    await state.set_state(AdminUserState.get_id)

@dp.message(AdminUserState.get_id, F.from_user.id == ADMIN_ID)
async def find_user(message: Message, state: FSMContext):
    if message.text == "⏪ Orqaga": return await back_handler(message, state)
    target_id = int(message.text)
    cursor.execute("SELECT balance, total_deposit, ref_count FROM users WHERE id = ?", (target_id,))
    user = cursor.fetchone()
    if not user:
        return await message.answer("Bunday foydalanuvchi topilmadi!")
    
    text = f"✅ Foydalanuvchi topildi!\n\nID: <code>{target_id}</code>\nBalansi: {user[0]} so'm\n" \
           f"Kiritgan pullar: {user[1]} so'm\nReferallari: {user[2]}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ Pul qo'shish", callback_data=f"addm_{target_id}"),
         InlineKeyboardButton(text="➖ Pul ayirish", callback_data=f"subm_{target_id}")]
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=kb)
    await state.clear()

@dp.callback_query(F.data.startswith("addm_") | F.data.startswith("subm_"))
async def mod_money_callback(call: CallbackQuery, state: FSMContext):
    action, uid = call.data.split("_")
    await state.update_data(target_id=int(uid))
    if action == "addm":
        await call.message.answer("Qancha pul qo'shmoqchisiz? Miqdor kiriting:", reply_markup=cancel_btn)
        await state.set_state(AdminUserState.add_money)
    else:
        await call.message.answer("Qancha pul ayirmoqchisiz? Miqdor kiriting:", reply_markup=cancel_btn)
        await state.set_state(AdminUserState.sub_money)

@dp.message(AdminUserState.add_money)
async def add_money_exec(message: Message, state: FSMContext):
    if message.text == "⏪ Orqaga": return await back_handler(message, state)
    data = await state.get_data()
    uid = data['target_id']
    amount = int(message.text)
    cursor.execute("UPDATE users SET balance = balance + ?, total_deposit = total_deposit + ? WHERE id = ?", (amount, amount, uid))
    conn.commit()
    await message.answer(f"✅ {uid} hisobiga {amount} so'm qo'shildi!", reply_markup=admin_menu())
    try: await bot.send_message(uid, f"Hisobingiz admin tomonidan {amount} so'mga to'ldirildi.")
    except: pass
    await state.clear()

# --- TO'LOV CHEKINI TASDIQLASH (Inline tugmalar orqali) ---
@dp.callback_query(F.data.startswith("accept_dep_") | F.data.startswith("reject_dep_"))
async def handle_deposit_decision(call: CallbackQuery):
    parts = call.data.split("_")
    action = parts[0]
    uid = int(parts[2])
    
    if action == "accept":
        amount = int(parts[3])
        cursor.execute("UPDATE users SET balance = balance + ?, total_deposit = total_deposit + ? WHERE id = ?", (amount, amount, uid))
        conn.commit()
        await call.message.edit_caption(caption=call.message.caption + "\n\n✅ <b>Tasdiqlandi!</b>", parse_mode="HTML")
        try: await bot.send_message(uid, f"✅ To'lovingiz tasdiqlandi!\nHisobingiz {amount} so'mga to'ldirildi.")
        except: pass
    elif action == "reject":
        await call.message.edit_caption(caption=call.message.caption + "\n\n❌ <b>Bekor qilindi!</b>", parse_mode="HTML")
        try: await bot.send_message(uid, "❌ To'lovingiz admin tomonidan rad etildi.")
        except: pass

# --- TO'LOV TIZIMI QO'SHISH ---
@dp.message(F.text == "💳 To'lov tizimlar", F.from_user.id == ADMIN_ID)
async def admin_payments(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="➕ To'lov tizimi qo'shish", callback_data="add_pay_sys")]])
    await message.answer("To'lov tizimlari bo'limi:", reply_markup=kb)

@dp.callback_query(F.data == "add_pay_sys")
async def add_pay_sys(call: CallbackQuery, state: FSMContext):
    await call.message.answer("To'lov tizimi nomini kiriting (Masalan: Uzcard):", reply_markup=cancel_btn)
    await state.set_state(AdminPaymentState.name)

@dp.message(AdminPaymentState.name)
async def add_pay_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Karta raqamini kiriting:")
    await state.set_state(AdminPaymentState.card)

@dp.message(AdminPaymentState.card)
async def add_pay_card(message: Message, state: FSMContext):
    await state.update_data(card=message.text)
    await message.answer("To'lov malumotini kiriting (Ism Familiya yoki izoh):")
    await state.set_state(AdminPaymentState.details)

@dp.message(AdminPaymentState.details)
async def add_pay_details(message: Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT INTO payments (name, card_number, details) VALUES (?, ?, ?)", (data['name'], data['card'], message.text))
    conn.commit()
    await message.answer("✅ To'lov tizimi muvaffaqiyatli qo'shildi!", reply_markup=admin_menu())
    await state.clear()

# --- QO'LLANMA QO'SHISH ---
@dp.message(F.text == "📖 Qo'llanmalar", F.from_user.id == ADMIN_ID)
async def admin_guides(message: Message, state: FSMContext):
    await message.answer("Yangi qo'llanma nomini kiriting:", reply_markup=cancel_btn)
    await state.set_state(AdminGuideState.title)

@dp.message(AdminGuideState.title)
async def admin_guide_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Qo'llanma xabarini kiriting:")
    await state.set_state(AdminGuideState.text)

@dp.message(AdminGuideState.text)
async def admin_guide_text(message: Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT INTO guides (title, text) VALUES (?, ?)", (data['title'], message.text))
    conn.commit()
    await message.answer("✅ Qo'llanma muvaffaqiyatli qo'shildi!", reply_markup=admin_menu())
    await state.clear()

# ================= ASOSIY START =================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
