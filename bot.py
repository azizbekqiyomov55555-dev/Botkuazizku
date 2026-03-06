import logging
import asyncio
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import os

# ==================== CONFIG ====================
BOT_TOKEN = ("8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o")
ADMIN_IDS  = [int(x) for x in ("ADMIN_IDS", "8537782289").split(",")]
# ================================================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

# ==================== DATABASE ====================
def db():
    return sqlite3.connect("smm.db")

def init_db():
    c = db(); cur = c.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id   INTEGER PRIMARY KEY,
        username  TEXT DEFAULT '',
        full_name TEXT DEFAULT '',
        balance   INTEGER DEFAULT 0,
        total_dep INTEGER DEFAULT 0,
        ref_id    INTEGER DEFAULT NULL,
        banned    INTEGER DEFAULT 0,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS networks (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS categories (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        net_id INTEGER,
        name   TEXT
    );
    CREATE TABLE IF NOT EXISTS services (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_id  INTEGER,
        api_id  TEXT DEFAULT '',
        name    TEXT,
        price   INTEGER DEFAULT 0,
        min_qty INTEGER DEFAULT 100,
        max_qty INTEGER DEFAULT 100000,
        descr   TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS orders (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        service_id INTEGER,
        link       TEXT,
        quantity   INTEGER,
        price      INTEGER,
        status     TEXT DEFAULT 'Bajarilmoqda',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS faq (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer   TEXT
    );
    CREATE TABLE IF NOT EXISTS channels (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        cid   TEXT,
        title TEXT,
        link  TEXT
    );
    CREATE TABLE IF NOT EXISTS payments (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT,
        details TEXT
    );
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        val TEXT
    );
    INSERT OR IGNORE INTO settings VALUES ('ref_bonus','500');
    INSERT OR IGNORE INTO settings VALUES ('min_topup','1000');
    INSERT OR IGNORE INTO settings VALUES ('api_url','');
    INSERT OR IGNORE INTO settings VALUES ('api_key','');
    """)
    for n in ["Telgram", "Instgram", "Tik tok", "Youtube"]:
        cur.execute("INSERT OR IGNORE INTO networks (name) VALUES (?)", (n,))
    c.commit(); c.close()

def cfg(key):
    c = db(); r = c.execute("SELECT val FROM settings WHERE key=?", (key,)).fetchone(); c.close()
    return r[0] if r else ""

def set_cfg(key, val):
    c = db(); c.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, val)); c.commit(); c.close()

def get_user(uid):
    c = db(); r = c.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone(); c.close(); return r

def ensure_user(uid, uname, fname, ref=None):
    if get_user(uid): return
    c = db()
    c.execute("INSERT OR IGNORE INTO users (user_id,username,full_name,ref_id) VALUES (?,?,?,?)", (uid, uname, fname, ref))
    if ref and ref != uid:
        bonus = int(cfg("ref_bonus") or 500)
        c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (bonus, ref))
    c.commit(); c.close()

def bal(uid):
    c = db(); r = c.execute("SELECT balance FROM users WHERE user_id=?", (uid,)).fetchone(); c.close(); return r[0] if r else 0

def add_bal(uid, amt):
    c = db(); c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amt, uid)); c.commit(); c.close()

def ord_cnt(uid):
    c = db(); r = c.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (uid,)).fetchone(); c.close(); return r[0]

def ref_cnt(uid):
    c = db(); r = c.execute("SELECT COUNT(*) FROM users WHERE ref_id=?", (uid,)).fetchone(); c.close(); return r[0]

def get_nets():
    c = db(); r = c.execute("SELECT * FROM networks").fetchall(); c.close(); return r

def get_cats(nid):
    c = db(); r = c.execute("SELECT * FROM categories WHERE net_id=?", (nid,)).fetchall(); c.close(); return r

def get_srvs(cid):
    c = db(); r = c.execute("SELECT * FROM services WHERE cat_id=?", (cid,)).fetchall(); c.close(); return r

def get_srv(sid):
    c = db(); r = c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone(); c.close(); return r

def get_ord(oid):
    c = db()
    r = c.execute("""SELECT o.*,s.name,s.price,n.name,cat.name FROM orders o
        JOIN services s ON o.service_id=s.id
        JOIN categories cat ON s.cat_id=cat.id
        JOIN networks n ON cat.net_id=n.id WHERE o.id=?""", (oid,)).fetchone()
    c.close(); return r

def user_ords(uid):
    c = db()
    r = c.execute("""SELECT o.id,n.name,cat.name,o.quantity,o.price,o.status,o.link,o.created_at
        FROM orders o JOIN services s ON o.service_id=s.id
        JOIN categories cat ON s.cat_id=cat.id
        JOIN networks n ON cat.net_id=n.id
        WHERE o.user_id=? ORDER BY o.id DESC""", (uid,)).fetchall()
    c.close(); return r

def all_ords():
    c = db()
    r = c.execute("""SELECT o.id,o.user_id,n.name,cat.name,o.quantity,o.price,o.status,o.link,o.created_at
        FROM orders o JOIN services s ON o.service_id=s.id
        JOIN categories cat ON s.cat_id=cat.id
        JOIN networks n ON cat.net_id=n.id
        ORDER BY o.id DESC""").fetchall()
    c.close(); return r

def mk_ord(uid, sid, link, qty, price):
    c = db()
    c.execute("INSERT INTO orders (user_id,service_id,link,quantity,price) VALUES (?,?,?,?,?)", (uid,sid,link,qty,price))
    oid = c.lastrowid
    c.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (price, uid))
    c.commit(); c.close(); return oid

def get_chans():
    c = db(); r = c.execute("SELECT * FROM channels").fetchall(); c.close(); return r

def get_pays():
    c = db(); r = c.execute("SELECT * FROM payments").fetchall(); c.close(); return r

def all_uids():
    c = db(); r = c.execute("SELECT user_id FROM users WHERE banned=0").fetchall(); c.close(); return [x[0] for x in r]

def get_stats():
    c = db(); cur = c.cursor()
    tot  = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    act  = cur.execute("SELECT COUNT(*) FROM users WHERE banned=0").fetchone()[0]
    n24  = cur.execute("SELECT COUNT(*) FROM users WHERE joined_at>=datetime('now','-1 day')").fetchone()[0]
    n7   = cur.execute("SELECT COUNT(*) FROM users WHERE joined_at>=datetime('now','-7 days')").fetchone()[0]
    n30  = cur.execute("SELECT COUNT(*) FROM users WHERE joined_at>=datetime('now','-30 days')").fetchone()[0]
    a24  = cur.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE created_at>=datetime('now','-1 day')").fetchone()[0]
    a7   = cur.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE created_at>=datetime('now','-7 days')").fetchone()[0]
    a30  = cur.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE created_at>=datetime('now','-30 days')").fetchone()[0]
    pay  = cur.execute("SELECT COUNT(*) FROM users WHERE balance>0").fetchone()[0]
    mon  = cur.execute("SELECT COALESCE(SUM(total_dep),0) FROM users").fetchone()[0]
    c.close()
    return dict(tot=tot,act=act,n24=n24,n7=n7,n30=n30,a24=a24,a7=a7,a30=a30,pay=pay,mon=mon)

# ==================== KEYBOARDS ====================
def main_kb(is_admin=False):
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
        kb.adjust(1, 2, 2, 2, 1)
    else:
        kb.adjust(1, 2, 2, 2)
    return kb.as_markup(resize_keyboard=True)

def admin_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📊 Statistika");     kb.button(text="🗃 Xabar yuborish")
    kb.button(text="🔐 Majbur obuna kanallar")
    kb.button(text="💳 To'lov tizimlar"); kb.button(text="🔑 API")
    kb.button(text="👤 Foydalanuvchini boshqarish")
    kb.button(text="📚 Qo'llanmalar");   kb.button(text="📈 Buyurtmalar")
    kb.button(text="◀️ Orqaga")
    kb.adjust(2, 1, 2, 1, 2, 1)
    return kb.as_markup(resize_keyboard=True)

# ==================== STATES ====================
class Order(StatesGroup):
    net=State(); cat=State(); srv=State(); qty=State(); link=State()

class Topup(StatesGroup):
    method=State(); amount=State()

class Contact(StatesGroup):
    msg=State()

class Adm(StatesGroup):
    bc_type=State(); bc_msg=State()
    find_uid=State()
    add_m_amt=State(); rem_m_amt=State()
    reply_msg=State()
    ch_id=State(); ch_title=State(); ch_link=State()
    pay_name=State(); pay_detail=State()
    api_url=State(); api_key=State()
    add_net=State()
    cat_net=State(); cat_name=State()
    srv_cat=State(); srv_api=State(); srv_name=State()
    srv_price=State(); srv_min=State(); srv_max=State(); srv_desc=State()
    faq_q=State(); faq_a=State()
    ord_search=State()
    cfg_key=State(); cfg_val=State()
    target_uid = State()

# ==================== SUB CHECK ====================
async def check_sub(uid):
    chans = get_chans()
    if not chans: return True, []
    nj = []
    for ch in chans:
        try:
            m = await bot.get_chat_member(ch[1], uid)
            if m.status in ("left","kicked","banned"): nj.append(ch)
        except: nj.append(ch)
    return len(nj)==0, nj

def sub_kb(chans):
    kb = InlineKeyboardBuilder()
    for ch in chans:
        kb.button(text=f"📢 {ch[2]}", url=ch[3])
    kb.button(text="✅ Tekshirish", callback_data="chksub")
    kb.adjust(1)
    return kb.as_markup()

# ==================== /start ====================
@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    ref = None
    args = msg.text.split()
    if len(args)>1:
        try: ref = int(args[1])
        except: pass
    ensure_user(uid, msg.from_user.username or "", msg.from_user.full_name or "", ref)
    u = get_user(uid)
    if u and u[6]:
        await msg.answer("🚫 Siz bloklangansiz."); return
    ok, chans = await check_sub(uid)
    if not ok:
        txt = "\n".join(f"• {c[2]}" for c in chans)
        await msg.answer(f"❗ Botdan foydalanish uchun obuna bo'ling:\n\n{txt}", reply_markup=sub_kb(chans)); return
    await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(uid in ADMIN_IDS))

@dp.callback_query(F.data=="chksub")
async def cb_chksub(call: types.CallbackQuery):
    uid = call.from_user.id
    ok, chans = await check_sub(uid)
    if ok:
        await call.message.delete()
        await call.message.answer("✅ Obuna tasdiqlandi!\n🖥 Asosiy menyudasiz!", reply_markup=main_kb(uid in ADMIN_IDS))
    else:
        await call.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)

# ==================== BUYURTMA ====================
@dp.message(F.text=="🛒 Buyurtma berish")
async def order_start(msg: types.Message, state: FSMContext):
    await state.clear()
    ok, chans = await check_sub(msg.from_user.id)
    if not ok:
        await msg.answer("❗ Avval obuna bo'ling:", reply_markup=sub_kb(chans)); return
    nets = get_nets()
    if not nets:
        await msg.answer("Tarmoqlar yo'q."); return
    kb = InlineKeyboardBuilder()
    for n in nets: kb.button(text=n[1], callback_data=f"on_{n[0]}")
    kb.adjust(2)
    await msg.answer("Quyidagi ijtimoiy tarmoqlardan birini tanlang.", reply_markup=kb.as_markup())
    await state.set_state(Order.net)

@dp.callback_query(F.data.startswith("on_"))
async def o_net(call: types.CallbackQuery, state: FSMContext):
    nid = int(call.data[3:])
    await state.update_data(nid=nid)
    cats = get_cats(nid)
    if not cats: await call.answer("Bo'lim yo'q!", show_alert=True); return
    kb = InlineKeyboardBuilder()
    for c in cats: kb.button(text=c[2], callback_data=f"oc_{c[0]}")
    kb.button(text="◀️ Orqaga", callback_data="obn")
    kb.adjust(1)
    await call.message.edit_text("Quyidagi bo'limlardan birini tanlang.\n(Narxlar 1000 tasi uchun berilgan)", reply_markup=kb.as_markup())
    await state.set_state(Order.cat)

@dp.callback_query(F.data=="obn")
async def o_back_nets(call: types.CallbackQuery, state: FSMContext):
    nets = get_nets()
    kb = InlineKeyboardBuilder()
    for n in nets: kb.button(text=n[1], callback_data=f"on_{n[0]}")
    kb.adjust(2)
    await call.message.edit_text("Quyidagi ijtimoiy tarmoqlardan birini tanlang.", reply_markup=kb.as_markup())
    await state.set_state(Order.net)

@dp.callback_query(F.data.startswith("oc_"))
async def o_cat(call: types.CallbackQuery, state: FSMContext):
    cid = int(call.data[3:])
    await state.update_data(cid=cid)
    srvs = get_srvs(cid)
    if not srvs: await call.answer("Xizmat yo'q!", show_alert=True); return
    data = await state.get_data()
    kb = InlineKeyboardBuilder()
    for s in srvs: kb.button(text=s[3], callback_data=f"os_{s[0]}")
    kb.button(text="◀️ Orqaga", callback_data=f"obc_{data.get('nid',0)}")
    kb.adjust(1)
    await call.message.edit_text("Xizmat APIni tanlang:", reply_markup=kb.as_markup())
    await state.set_state(Order.srv)

@dp.callback_query(F.data.startswith("obc_"))
async def o_back_cats(call: types.CallbackQuery, state: FSMContext):
    nid = int(call.data[4:])
    cats = get_cats(nid)
    kb = InlineKeyboardBuilder()
    for c in cats: kb.button(text=c[2], callback_data=f"oc_{c[0]}")
    kb.button(text="◀️ Orqaga", callback_data="obn")
    kb.adjust(1)
    await call.message.edit_text("Quyidagi bo'limlardan birini tanlang.", reply_markup=kb.as_markup())
    await state.set_state(Order.cat)

@dp.callback_query(F.data.startswith("os_"))
async def o_srv(call: types.CallbackQuery, state: FSMContext):
    sid = int(call.data[3:])
    s = get_srv(sid)
    if not s: await call.answer("Topilmadi!"); return
    await state.update_data(sid=sid)
    c = db()
    row = c.execute("SELECT n.name,cat.name FROM categories cat JOIN networks n ON cat.net_id=n.id WHERE cat.id=?", (s[1],)).fetchone()
    c.close()
    nn = row[0] if row else ""; cn = row[1] if row else ""
    await state.update_data(nname=nn, catname=cn)
    speed = "⚡-Tezkor" if s[4]>=10000 else "🐢-Sekin"
    desc = s[7] if s[7] else "Yo'q 💬"
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Buyurtma berish", callback_data=f"oconf_{sid}")
    kb.button(text="◀️ Orqaga", callback_data=f"obs_{s[1]}")
    kb.adjust(1)
    await call.message.edit_text(
        f"{nn} - 👤 {cn} [ {speed} ]\n\n"
        f"💰 Narxi (1000x): {s[4]} So'm\n\n"
        f"| {desc}\n\n"
        f"⬇️ Minimal: {s[5]} ta\n⬆️ Maksimal: {s[6]} ta",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("obs_"))
async def o_back_srvs(call: types.CallbackQuery, state: FSMContext):
    cid = int(call.data[4:])
    data = await state.get_data(); nid = data.get("nid", 0)
    srvs = get_srvs(cid)
    kb = InlineKeyboardBuilder()
    for s in srvs: kb.button(text=s[3], callback_data=f"os_{s[0]}")
    kb.button(text="◀️ Orqaga", callback_data=f"obc_{nid}")
    kb.adjust(1)
    await call.message.edit_text("Xizmat APIni tanlang:", reply_markup=kb.as_markup())
    await state.set_state(Order.srv)

@dp.callback_query(F.data.startswith("oconf_"))
async def o_confirm(call: types.CallbackQuery, state: FSMContext):
    sid = int(call.data[6:])
    s = get_srv(sid)
    await call.message.edit_text(
        f"📊 Buyurtma miqdorini kiriting:\n\n⬇️ Minimal: {s[5]} ta\n⬆️ Maksimal: {s[6]} ta"
    )
    await state.set_state(Order.qty)

@dp.message(Order.qty)
async def o_qty(msg: types.Message, state: FSMContext):
    try: qty = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri son. Qaytadan kiriting:"); return
    data = await state.get_data()
    s = get_srv(data["sid"])
    if qty < s[5] or qty > s[6]:
        await msg.answer(f"❌ Miqdor {s[5]} dan {s[6]} gacha bo'lishi kerak!"); return
    price = int(qty * s[4] / 1000)
    b = bal(msg.from_user.id)
    if b < price:
        kb = InlineKeyboardBuilder()
        kb.button(text="💳 Hisobni to'ldirish", callback_data="goto_topup")
        await msg.answer(
            f"⚠️ Hisobingizda yetarli mablag' mavjut emas!\n\n"
            f"💰 Narxi: {price} So'm\n📊 Miqdor: {qty} ta\n\nBoshqa miqdor kiritib ko'ring:",
            reply_markup=kb.as_markup()
        ); return
    await state.update_data(qty=qty, price=price)
    await msg.answer("🔗 Havola (link) ni kiriting:")
    await state.set_state(Order.link)

@dp.message(Order.link)
async def o_link(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    link = msg.text.strip()
    await state.update_data(link=link)
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data="o_ok")
    kb.button(text="❌ Bekor", callback_data="o_no")
    kb.adjust(2)
    await msg.answer(
        f"📋 Buyurtma ma'lumotlari:\n\n"
        f"🌐 Tarmoq: {data['nname']}\n📂 Bo'lim: {data['catname']}\n"
        f"🔗 Havola: {link}\n📊 Miqdor: {data['qty']} ta\n💰 Narxi: {data['price']} So'm\n\nTasdiqlaysizmi?",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data=="o_ok")
async def o_ok(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data(); uid = call.from_user.id
    oid = mk_ord(uid, data["sid"], data["link"], data["qty"], data["price"])
    await state.clear()
    await call.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n\n🆔 Buyurtma ID si: {oid}\n\n"
        f"⏳ To'lovingiz 5 daqiqadan 24 soatgacha bo'lgan vaqt ichida amalga oshiriladi!"
    )
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid,
                f"🆕 Yangi buyurtma!\n🆔 ID: {oid} | 👤 {uid}\n"
                f"🌐 {data['nname']} - {data['catname']}\n"
                f"🔗 {data['link']}\n📊 {data['qty']} ta | 💰 {data['price']} So'm"
            )
        except: pass
    # External API
    api_url = cfg("api_url"); api_key = cfg("api_key")
    if api_url and api_key:
        s = get_srv(data["sid"])
        try:
            async with aiohttp.ClientSession() as sess:
                await sess.post(api_url, data={"key":api_key,"action":"add","service":s[2],"link":data["link"],"quantity":data["qty"]})
        except: pass

@dp.callback_query(F.data=="o_no")
async def o_no(call: types.CallbackQuery, state: FSMContext):
    await state.clear(); await call.message.edit_text("❌ Buyurtma bekor qilindi.")

@dp.callback_query(F.data=="goto_topup")
async def goto_topup(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    pays = get_pays()
    if not pays:
        await call.message.answer("💳 To'lov tizimi sozlanmagan."); return
    kb = InlineKeyboardBuilder()
    for p in pays: kb.button(text=p[1], callback_data=f"ps_{p[0]}")
    kb.adjust(1)
    await call.message.answer("💳 To'lov tizimini tanlang:", reply_markup=kb.as_markup())
    await state.set_state(Topup.method)

# ==================== BUYURTMALAR ====================
@dp.message(F.text=="📦 Buyurtmalar")
async def my_orders(msg: types.Message):
    orders = user_ords(msg.from_user.id)
    if not orders: await msg.answer("📦 Sizda hali buyurtmalar yo'q."); return
    await _show_user_ord(msg, orders, 0, send=True)

async def _show_user_ord(msg, orders, idx, send=False):
    o = orders[idx]; total = len(orders)
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[5],"❓")
    text = (
        f"📦 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]}\n"
        f"🗂 Xizmat: 👤 {o[2]} [ ⚡-Tezkor ]\n"
        f"♻️ Holat: {se} {o[5]}\n"
        f"📅 Sana: {o[7][:19]}\n{'─'*22}"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text=str(o[0]), callback_data="np")
    if total > 1:
        prev = idx-1 if idx>0 else total-1
        nxt  = idx+1 if idx<total-1 else 0
        kb.button(text="◀️", callback_data=f"uop_{prev}_{msg.from_user.id}")
        kb.button(text=f"{idx+1}/{total}", callback_data="np")
        kb.button(text="▶️", callback_data=f"uop_{nxt}_{msg.from_user.id}")
        kb.adjust(1, 3)
    else:
        kb.adjust(1)
    kb.button(text="🔍 Qidirish", callback_data=f"uosearch_{msg.from_user.id}")
    if send:
        await msg.answer(text, reply_markup=kb.as_markup())
    else:
        await msg.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("uop_"))
async def uop(call: types.CallbackQuery):
    parts = call.data.split("_"); idx=int(parts[1]); uid=int(parts[2])
    orders = user_ords(uid)
    if not orders: return
    idx = max(0, min(idx, len(orders)-1))
    o = orders[idx]; total = len(orders)
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[5],"❓")
    text = (
        f"📦 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]}\n"
        f"🗂 Xizmat: 👤 {o[2]} [ ⚡-Tezkor ]\n"
        f"♻️ Holat: {se} {o[5]}\n"
        f"📅 Sana: {o[7][:19]}\n{'─'*22}"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text=str(o[0]), callback_data="np")
    if total > 1:
        prev = idx-1 if idx>0 else total-1
        nxt  = idx+1 if idx<total-1 else 0
        kb.button(text="◀️", callback_data=f"uop_{prev}_{uid}")
        kb.button(text=f"{idx+1}/{total}", callback_data="np")
        kb.button(text="▶️", callback_data=f"uop_{nxt}_{uid}")
        kb.adjust(1, 3)
    else:
        kb.adjust(1)
    kb.button(text="🔍 Qidirish", callback_data=f"uosearch_{uid}")
    await call.message.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data=="np")
async def np(call: types.CallbackQuery): await call.answer()

# ==================== HISOBIM ====================
@dp.message(F.text=="👤 Hisobim")
async def hisobim(msg: types.Message):
    uid = msg.from_user.id; u = get_user(uid)
    if not u: return
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Hisobni to'ldirish", callback_data="goto_topup")
    await msg.answer(
        f"👤 Sizning ID raqamingiz: {uid}\n\n"
        f"💰 Balansingiz: {u[3]} So'm\n"
        f"📦 Buyurtmalaringiz: {ord_cnt(uid)} ta\n"
        f"👥 Referallaringiz: {ref_cnt(uid)} ta\n"
        f"💵 Kiritgan pullaringiz: {u[4]} So'm",
        reply_markup=kb.as_markup()
    )

# ==================== HISOB TO'LDIRISH ====================
@dp.message(F.text=="💰 Hisob to'ldirish")
async def topup_start(msg: types.Message, state: FSMContext):
    pays = get_pays()
    if not pays: await msg.answer("💳 To'lov tizimi sozlanmagan."); return
    kb = InlineKeyboardBuilder()
    for p in pays: kb.button(text=p[1], callback_data=f"ps_{p[0]}")
    kb.adjust(1)
    await msg.answer("💳 To'lov tizimini tanlang:", reply_markup=kb.as_markup())
    await state.set_state(Topup.method)

@dp.callback_query(F.data.startswith("ps_"))
async def ps(call: types.CallbackQuery, state: FSMContext):
    pid = int(call.data[3:])
    c = db(); p = c.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone(); c.close()
    if not p: await call.answer("Topilmadi!"); return
    await state.update_data(pay_name=p[1], pay_det=p[2])
    min_t = cfg("min_topup") or "1000"
    await call.message.edit_text(f"💰 To'lov miqdorini kiriting:\n\nMinimal: {min_t} so'm")
    await state.set_state(Topup.amount)

@dp.message(Topup.amount)
async def topup_amt(msg: types.Message, state: FSMContext):
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri miqdor!"); return
    min_t = int(cfg("min_topup") or 1000)
    if amt < min_t:
        await msg.answer(f"❌ To'lov qilishda xatolik yuz berdi.\nIltimos, qayta urinib ko'ring."); return
    data = await state.get_data(); await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ To'lovni tasdiqlash", callback_data=f"pd_{msg.from_user.id}_{amt}")
    kb.button(text="❌ Bekor", callback_data="pcancel"); kb.adjust(1)
    await msg.answer(
        f"💳 To'lov ma'lumotlari:\n\n💰 Miqdor: {amt} So'm\n🏦 Tizim: {data['pay_name']}\n\n"
        f"{data['pay_det']}\n\n⚠️ To'lovni amalga oshirgach 'Tasdiqlash' tugmasini bosing!",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("pd_"))
async def pd(call: types.CallbackQuery):
    parts = call.data.split("_"); uid=int(parts[1]); amt=int(parts[2])
    await call.message.edit_text("⏳ To'lovingiz adminга yuborildi!")
    for aid in ADMIN_IDS:
        try:
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Tasdiqlash", callback_data=f"apo_{uid}_{amt}")
            kb.button(text="❌ Rad etish", callback_data=f"apn_{uid}"); kb.adjust(2)
            await bot.send_message(aid, f"💳 To'lov so'rovi!\n\n👤 User: {uid}\n💰 Miqdor: {amt} So'm", reply_markup=kb.as_markup())
        except: pass

@dp.callback_query(F.data=="pcancel")
async def pcancel(call: types.CallbackQuery): await call.message.edit_text("❌ Bekor qilindi.")

@dp.callback_query(F.data.startswith("apo_"))
async def apo(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    parts = call.data.split("_"); uid=int(parts[1]); amt=int(parts[2])
    c = db(); c.execute("UPDATE users SET balance=balance+?,total_dep=total_dep+? WHERE user_id=?", (amt,amt,uid)); c.commit(); c.close()
    await call.message.edit_text(f"✅ {uid} ga {amt} So'm qo'shildi!")
    try: await bot.send_message(uid, f"✅ Hisobingiz {amt} So'm ga to'ldirildi! 🎉")
    except: pass

@dp.callback_query(F.data.startswith("apn_"))
async def apn(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[4:])
    await call.message.edit_text(f"❌ {uid} ning to'lovi rad etildi.")
    try: await bot.send_message(uid, "❌ To'lovingiz rad etildi.")
    except: pass

# ==================== PUL ISHLASH ====================
@dp.message(F.text=="💵 Pul ishlash")
async def earn(msg: types.Message):
    uid = msg.from_user.id
    binfo = await bot.get_me()
    link = f"https://t.me/{binfo.username}?start={uid}"
    bonus = cfg("ref_bonus") or "500"
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data="back_cb")
    await msg.answer(
        f"🔗 Sizning referal havolangiz:\n\n{link}\n\n"
        f"1 ta referal uchun {bonus} So'm beriladi\n\n"
        f"👥 Referallaringiz: {ref_cnt(uid)} ta",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data=="back_cb")
async def back_cb(call: types.CallbackQuery): await call.message.delete()

# ==================== MUROJAAT ====================
@dp.message(F.text=="🆘 Murojaat")
async def contact_start(msg: types.Message, state: FSMContext):
    await msg.answer("📝 Murojaat matnini yozib yuboring.")
    await state.set_state(Contact.msg)

@dp.message(Contact.msg)
async def contact_msg(msg: types.Message, state: FSMContext):
    await state.clear(); uid = msg.from_user.id
    await msg.answer("⏳ Murojaatingiz qabul qilindi!\n\nTez orada murojaatingizni ko'rib chiqamiz.")
    for aid in ADMIN_IDS:
        try:
            kb = InlineKeyboardBuilder()
            kb.button(text="📝 Javob yozish", callback_data=f"ar_{uid}")
            await bot.send_message(aid,
                f"📩 Yangi murojaat!\n👤 {msg.from_user.full_name} (ID: {uid})\n\n{msg.text}",
                reply_markup=kb.as_markup()
            )
        except: pass

@dp.callback_query(F.data.startswith("ar_"))
async def admin_reply_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[3:])
    await state.update_data(reply_uid=uid)
    await call.message.answer(f"{uid} Foydalanuvchiga yuborilادigan xabaringizni kiriting.")
    await state.set_state(Adm.reply_msg)

@dp.message(Adm.reply_msg)
async def admin_reply_send(msg: types.Message, state: FSMContext):
    data = await state.get_data(); uid = data["reply_uid"]; await state.clear()
    try:
        await bot.send_message(uid, f"📩 Admin javobi:\n\n{msg.text}")
        await msg.answer("✅ Xabar foydalanuvchiga yuborildi!")
    except: await msg.answer("❌ Yuborib bo'lmadi.")

# ==================== QO'LLANMA ====================
@dp.message(F.text=="📚 Qo'llanma")
async def faq(msg: types.Message):
    c = db(); faqs = c.execute("SELECT * FROM faq").fetchall(); c.close()
    if not faqs: await msg.answer("Hozircha qo'llanmalar yo'q."); return
    kb = InlineKeyboardBuilder()
    for f in faqs: kb.button(text=f[1][:35], callback_data=f"fq_{f[0]}")
    kb.adjust(1)
    await msg.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("fq_"))
async def fq_show(call: types.CallbackQuery):
    fid = int(call.data[3:])
    c = db(); f = c.execute("SELECT * FROM faq WHERE id=?", (fid,)).fetchone(); c.close()
    if f: await call.message.answer(f"❓ {f[1]}\n\n💬 {f[2]}")

# ==================== ORQAGA ====================
@dp.message(F.text=="◀️ Orqaga")
async def back_main(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=main_kb(msg.from_user.id in ADMIN_IDS))

# ==================== ADMIN ====================
@dp.message(F.text=="🖥 Boshqaruv")
async def admin_panel(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=admin_kb())

# --- Statistika ---
@dp.message(F.text=="📊 Statistika")
async def admin_stats(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    s = get_stats(); binfo = await bot.get_me()
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 TOP-50 Balans", callback_data="t50b")
    kb.button(text="👥 TOP-50 Referal", callback_data="t50r"); kb.adjust(2)
    await msg.answer(
        f"📊 Statistika\n• Obunachilar soni: {s['tot']} ta\n• Faol obunachilar: {s['act']} ta\n"
        f"• Tark etganlar: {s['tot']-s['act']} ta\n\n📈 Obunachilar qo'shilishi\n"
        f"• Oxirgi 24 soat: +{s['n24']} obunachi\n• Oxirgi 7 kun: +{s['n7']} obunachi\n"
        f"• Oxirgi 30 kun: +{s['n30']} obunachi\n\n📊 Faollik\n"
        f"• Oxirgi 24 soatda faol: {s['a24']} ta\n• Oxirgi 7 kun faol: {s['a7']} ta\n"
        f"• Oxirgi 30 kun faol: {s['a30']} ta\n\n💰 Pullar Statistikasi\n"
        f"• Puli borlar: {s['pay']} ta\n• Jami pullar: {s['mon']} So'm\n\n🤖 @{binfo.username}",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data=="t50b")
async def t50b(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    c = db(); rows = c.execute("SELECT user_id,full_name,balance FROM users ORDER BY balance DESC LIMIT 50").fetchall(); c.close()
    text = "💰 TOP-50 Balans:\n\n"
    for i,r in enumerate(rows,1): text += f"{i}. {r[1] or r[0]} — {r[2]} So'm\n"
    await call.message.answer(text[:4096])

@dp.callback_query(F.data=="t50r")
async def t50r(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    c = db()
    rows = c.execute("SELECT u.user_id,u.full_name,COUNT(r.user_id) rc FROM users u LEFT JOIN users r ON r.ref_id=u.user_id GROUP BY u.user_id ORDER BY rc DESC LIMIT 50").fetchall()
    c.close()
    text = "👥 TOP-50 Referal:\n\n"
    for i,r in enumerate(rows,1): text += f"{i}. {r[1] or r[0]} — {r[2]} ta\n"
    await call.message.answer(text[:4096])

# --- Broadcast ---
@dp.message(F.text=="🗃 Xabar yuborish")
async def bc_start(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Oddiy", callback_data="bc_n")
    kb.button(text="📤 Forward", callback_data="bc_f"); kb.adjust(2)
    await msg.answer("Foydalanuvchilarga yuboradigan xabar turini tanlang.", reply_markup=kb.as_markup())
    await state.set_state(Adm.bc_type)

@dp.callback_query(F.data.startswith("bc_"), Adm.bc_type)
async def bc_type(call: types.CallbackQuery, state: FSMContext):
    btype = call.data[3:]
    await state.update_data(btype=btype)
    await call.message.answer("Yubormoqchi bo'lgan xabarni yozing:")
    await state.set_state(Adm.bc_msg)

@dp.message(Adm.bc_msg)
async def bc_send(msg: types.Message, state: FSMContext):
    data = await state.get_data(); await state.clear()
    uids = all_uids(); ok=fail=0
    for uid in uids:
        try:
            if data.get("btype")=="f": await msg.forward(uid)
            else: await bot.send_message(uid, msg.text or msg.caption or "")
            ok+=1; await asyncio.sleep(0.03)
        except: fail+=1
    await msg.answer(f"✅ Yuborildi: {ok}\n❌ Xato: {fail}")

# --- Majbur obuna kanallar ---
@dp.message(F.text=="🔐 Majbur obuna kanallar")
async def adm_chans(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    chans = get_chans()
    kb = InlineKeyboardBuilder()
    for ch in chans: kb.button(text=f"🗑 {ch[2]}", callback_data=f"dch_{ch[0]}")
    kb.button(text="➕ Kanal qo'shish", callback_data="ach")
    kb.button(text="📋 Ro'yxatni ko'rish", callback_data="lch")
    kb.button(text="🗑 Kanalni o'chirish", callback_data="dch_menu")
    kb.button(text="◀️ Orqaga", callback_data="back_adm"); kb.adjust(1)
    await msg.answer(
        "🔐 Majburiy obuna turini tanlang:\n\n"
        "Quyida majburiy obunani qo'shishning 3 ta turi mavjud:\n\n"
        "◆ Ommaviy / Shaxsiy (Kanal · Guruh) 💬\nHar qanday kanal yoki guruhni (ommaviy yoki shaxsiy) majburiy obunaga ulash.\n\n"
        "◆ Shaxsiy / So'rovli havola\nShaxsiy yoki so'rovli kanal/guruh havolasi orqali o'tganlarni kuzatish.\n\n"
        "◆ 🌐 Oddiy havola\nMajburiy tekshiruvsiz oddiy havolani ko'rsatish.",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data=="ach")
async def ach(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Kanal ID'sini kiriting (@kanal yoki -100...):")
    await state.set_state(Adm.ch_id)

@dp.message(Adm.ch_id)
async def ach_id(msg: types.Message, state: FSMContext):
    await state.update_data(ch_id=msg.text.strip())
    await msg.answer("Kanal nomini kiriting:")
    await state.set_state(Adm.ch_title)

@dp.message(Adm.ch_title)
async def ach_title(msg: types.Message, state: FSMContext):
    await state.update_data(ch_title=msg.text.strip())
    await msg.answer("Kanal havolasini kiriting (https://t.me/...):")
    await state.set_state(Adm.ch_link)

@dp.message(Adm.ch_link)
async def ach_link(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    c = db(); c.execute("INSERT INTO channels (cid,title,link) VALUES (?,?,?)", (data["ch_id"],data["ch_title"],msg.text.strip())); c.commit(); c.close()
    await state.clear()
    await msg.answer(f"✅ {data['ch_title']} kanali qo'shildi!")

@dp.callback_query(F.data.startswith("dch_"))
async def dch(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    part = call.data[4:]
    if part == "menu": await call.answer("Yuqoridagi ro'yxatdan tanlab o'chiring."); return
    cid = int(part)
    c = db(); c.execute("DELETE FROM channels WHERE id=?", (cid,)); c.commit(); c.close()
    await call.message.edit_text("✅ Kanal o'chirildi!")

@dp.callback_query(F.data=="lch")
async def lch(call: types.CallbackQuery):
    chans = get_chans()
    if not chans: await call.answer("Kanallar yo'q!", show_alert=True); return
    text = "📋 Kanallar:\n\n"
    for ch in chans: text += f"• {ch[2]} | {ch[1]} | {ch[3]}\n"
    await call.message.answer(text)

# --- To'lov tizimlari ---
@dp.message(F.text=="💳 To'lov tizimlar")
async def adm_pays(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    pays = get_pays()
    kb = InlineKeyboardBuilder()
    for p in pays: kb.button(text=f"🗑 {p[1]}", callback_data=f"dp_{p[0]}")
    kb.button(text="➕ To'lov tizimi qo'shish", callback_data="ap")
    kb.button(text="◀️ Orqaga", callback_data="back_adm"); kb.adjust(1)
    await msg.answer(f"💳 To'lov tizimlari: {len(pays)} ta", reply_markup=kb.as_markup())

@dp.callback_query(F.data=="ap")
async def ap(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("To'lov tizimi nomini kiriting (Click, Payme, Uzcart...):")
    await state.set_state(Adm.pay_name)

@dp.message(Adm.pay_name)
async def ap_name(msg: types.Message, state: FSMContext):
    await state.update_data(pay_name=msg.text.strip())
    await msg.answer("To'lov ma'lumotlarini kiriting (karta raqami, ism va h.k.):")
    await state.set_state(Adm.pay_detail)

@dp.message(Adm.pay_detail)
async def ap_detail(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    c = db(); c.execute("INSERT INTO payments (name,details) VALUES (?,?)", (data["pay_name"],msg.text.strip())); c.commit(); c.close()
    await state.clear()
    await msg.answer(f"✅ {data['pay_name']} to'lov tizimi qo'shildi!")

@dp.callback_query(F.data.startswith("dp_"))
async def dp_(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    pid = int(call.data[3:])
    c = db(); c.execute("DELETE FROM payments WHERE id=?", (pid,)); c.commit(); c.close()
    await call.message.edit_text("✅ To'lov tizimi o'chirildi!")

# --- API ---
@dp.message(F.text=="🔑 API")
async def adm_api(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    cur = cfg("api_url") or "(belgilanmagan)"
    await msg.answer(f"🔑 API manzilini kiriting:\n\nNamuna: https://capitalsmmapi.uz/api/v2\n\nHozirgi: {cur}")
    await state.set_state(Adm.api_url)

@dp.message(Adm.api_url)
async def adm_api_url(msg: types.Message, state: FSMContext):
    set_cfg("api_url", msg.text.strip())
    await msg.answer("✅ API manzili saqlandi!\n\nAPI kalitini kiriting:")
    await state.set_state(Adm.api_key)

@dp.message(Adm.api_key)
async def adm_api_key(msg: types.Message, state: FSMContext):
    set_cfg("api_key", msg.text.strip())
    await state.clear()
    await msg.answer("✅ API kaliti saqlandi!")

# --- Foydalanuvchini boshqarish ---
@dp.message(F.text=="👤 Foydalanuvchini boshqarish")
async def adm_users(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("👤 Foydalanuvchining ID raqamini yuboring:")
    await state.set_state(Adm.find_uid)

@dp.message(Adm.find_uid)
async def adm_find(msg: types.Message, state: FSMContext):
    try: uid = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri ID!"); return
    u = get_user(uid)
    if not u: await msg.answer("❌ Foydalanuvchi topilmadi!"); await state.clear(); return
    await state.clear()
    ban_txt = "🔕 Banlash" if not u[6] else "✅ Bandan chiqarish"
    kb = InlineKeyboardBuilder()
    kb.button(text=f"🔔 {ban_txt}", callback_data=f"ban_{uid}")
    kb.button(text="+ Pul qo'shish", callback_data=f"am_{uid}")
    kb.button(text="— Pul ayirish", callback_data=f"rm_{uid}")
    kb.adjust(1, 2)
    await msg.answer(
        f"✅ Foydalanuvchi topildi!\n\n"
        f"🆔 ID raqami: {uid}\n💰 Balansi: {u[3]} So'm\n"
        f"📦 Buyurtmalari: {ord_cnt(uid)} ta\n"
        f"👥 Referallari: {ref_cnt(uid)} ta\n"
        f"💵 Kiritgan pullar: {u[4]} So'm",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("ban_"))
async def ban_u(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[4:])
    c = db(); cur_ban = c.execute("SELECT banned FROM users WHERE user_id=?", (uid,)).fetchone()[0]
    new = 0 if cur_ban else 1
    c.execute("UPDATE users SET banned=? WHERE user_id=?", (new, uid)); c.commit(); c.close()
    status = "🔕 Banlandi" if new else "✅ Ban olib tashlandi"
    await call.message.edit_text(f"{status}: {uid}")

@dp.callback_query(F.data.startswith("am_"))
async def am_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[3:])
    await state.update_data(target_uid=uid)
    await call.message.answer(f"({uid}) ning hisobiga qancha pul qo'shmoqchisiz?")
    await state.set_state(Adm.add_m_amt)

@dp.message(Adm.add_m_amt)
async def am_do(msg: types.Message, state: FSMContext):
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    data = await state.get_data(); uid = data["target_uid"]
    c = db(); c.execute("UPDATE users SET balance=balance+?,total_dep=total_dep+? WHERE user_id=?", (amt,amt,uid)); c.commit(); c.close()
    await state.clear()
    await msg.answer(f"✅ Foydalanuvchi hisobiga {amt} So'm qo'shildi!")
    try: await bot.send_message(uid, f"💰 Hisobingizga {amt} So'm qo'shildi!")
    except: pass

@dp.callback_query(F.data.startswith("rm_"))
async def rm_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[3:])
    await state.update_data(target_uid=uid)
    await call.message.answer(f"({uid}) ning hisobidan qancha pul ayirmoqchisiz?")
    await state.set_state(Adm.rem_m_amt)

@dp.message(Adm.rem_m_amt)
async def rm_do(msg: types.Message, state: FSMContext):
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    data = await state.get_data(); uid = data["target_uid"]
    c = db(); c.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (amt,uid)); c.commit(); c.close()
    await state.clear()
    await msg.answer(f"✅ Foydalanuvchi hisobidan {amt} So'm ayirildi!")

# --- Qo'llanmalar (admin) ---
@dp.message(F.text=="📚 Qo'llanmalar")
async def adm_faq(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    c = db(); faqs = c.execute("SELECT * FROM faq").fetchall(); c.close()
    kb = InlineKeyboardBuilder()
    for f in faqs: kb.button(text=f"🗑 {f[1][:25]}", callback_data=f"dfq_{f[0]}")
    kb.button(text="➕ Qo'llanma qo'shish", callback_data="afq"); kb.adjust(1)
    await msg.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=kb.as_markup())

@dp.callback_query(F.data=="afq")
async def afq_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Qo'llanma nomini kiriting:")
    await state.set_state(Adm.faq_q)

@dp.message(Adm.faq_q)
async def afq_q(msg: types.Message, state: FSMContext):
    await state.update_data(faq_q=msg.text.strip())
    await msg.answer("Qo'llanma mazmunini kiriting:")
    await state.set_state(Adm.faq_a)

@dp.message(Adm.faq_a)
async def afq_a(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    c = db(); c.execute("INSERT INTO faq (question,answer) VALUES (?,?)", (data["faq_q"],msg.text.strip())); c.commit(); c.close()
    await state.clear(); await msg.answer("✅ Qo'llanma qo'shildi!")

@dp.callback_query(F.data.startswith("dfq_"))
async def dfq(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    fid = int(call.data[4:])
    c = db(); c.execute("DELETE FROM faq WHERE id=?", (fid,)); c.commit(); c.close()
    await call.message.edit_text("✅ Qo'llanma o'chirildi!")

# --- Buyurtmalar (admin) ---
@dp.message(F.text=="📈 Buyurtmalar")
async def adm_orders(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    orders = all_ords()
    if not orders: await msg.answer("Buyurtmalar yo'q."); return
    await _show_adm_ord(msg, orders, 0, send=True)

async def _show_adm_ord(msg, orders, idx, send=False):
    o = orders[idx]; total = len(orders)
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[6],"❓")
    text = (
        f"📈 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]} | 👤 User: {o[1]}\n"
        f"🌐 {o[2]} - {o[3]}\n"
        f"♻️ Holat: {se} {o[6]}\n"
        f"🔗 {o[7]}\n📊 {o[4]} ta | 💰 {o[5]} So'm\n"
        f"📅 {o[8][:19]}\n{'─'*22}"
    )
    kb = InlineKeyboardBuilder()
    if total > 1:
        prev = idx-1 if idx>0 else total-1
        nxt  = idx+1 if idx<total-1 else 0
        kb.button(text="◀️", callback_data=f"aop_{prev}")
        kb.button(text=f"{idx+1}/{total}", callback_data="np")
        kb.button(text="▶️", callback_data=f"aop_{nxt}")
        kb.adjust(3)
    kb.button(text="✅ Bajarildi", callback_data=f"odone_{o[0]}")
    kb.button(text="❌ Bekor qilish", callback_data=f"ocancel_{o[0]}")
    kb.button(text="🔍 Qidirish", callback_data="adm_osrch")
    kb.adjust(3 if total>1 else 0, 2, 1)
    if send: await msg.answer(text, reply_markup=kb.as_markup())
    else:    await msg.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("aop_"))
async def aop(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    idx = int(call.data[4:])
    orders = all_ords()
    if not orders: return
    idx = max(0, min(idx, len(orders)-1))
    o = orders[idx]; total = len(orders)
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[6],"❓")
    text = (
        f"📈 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]} | 👤 User: {o[1]}\n"
        f"🌐 {o[2]} - {o[3]}\n"
        f"♻️ Holat: {se} {o[6]}\n"
        f"🔗 {o[7]}\n📊 {o[4]} ta | 💰 {o[5]} So'm\n"
        f"📅 {o[8][:19]}\n{'─'*22}"
    )
    kb = InlineKeyboardBuilder()
    if total > 1:
        prev = idx-1 if idx>0 else total-1
        nxt  = idx+1 if idx<total-1 else 0
        kb.button(text="◀️", callback_data=f"aop_{prev}")
        kb.button(text=f"{idx+1}/{total}", callback_data="np")
        kb.button(text="▶️", callback_data=f"aop_{nxt}")
        kb.adjust(3)
    kb.button(text="✅ Bajarildi", callback_data=f"odone_{o[0]}")
    kb.button(text="❌ Bekor qilish", callback_data=f"ocancel_{o[0]}")
    kb.button(text="🔍 Qidirish", callback_data="adm_osrch")
    await call.message.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("odone_"))
async def odone(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[6:])
    c = db()
    c.execute("UPDATE orders SET status='Bajarildi' WHERE id=?", (oid,))
    row = c.execute("SELECT user_id FROM orders WHERE id=?", (oid,)).fetchone()
    c.commit(); c.close()
    await call.message.edit_text(f"✅ Buyurtma #{oid} bajarildi!")
    if row:
        try: await bot.send_message(row[0], f"✅ Buyurtma #{oid} bajarildi!")
        except: pass

@dp.callback_query(F.data.startswith("ocancel_"))
async def ocancel(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[8:])
    c = db()
    row = c.execute("SELECT user_id,price FROM orders WHERE id=?", (oid,)).fetchone()
    if row:
        c.execute("UPDATE orders SET status='Bekor qilindi' WHERE id=?", (oid,))
        c.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (row[1],row[0]))
        c.commit()
    c.close()
    await call.message.edit_text(f"❌ Buyurtma #{oid} bekor qilindi, pul qaytarildi!")
    if row:
        try: await bot.send_message(row[0], f"🔴 {oid} buyurtma bekor qilindi.\n\n💰 {row[1]} So'm qaytarildi.")
        except: pass

@dp.callback_query(F.data=="adm_osrch")
async def adm_osrch(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("🔍 Kerakli buyurtma ID raqamini kiriting:")
    await state.set_state(Adm.ord_search)

@dp.message(Adm.ord_search)
async def adm_osrch_result(msg: types.Message, state: FSMContext):
    try: oid = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri ID!"); return
    await state.clear()
    o = get_ord(oid)
    if not o: await msg.answer("❌ Buyurtma topilmadi!"); return
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[6],"❓")
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Bajarildi", callback_data=f"odone_{oid}")
    kb.button(text="❌ Bekor qilish", callback_data=f"ocancel_{oid}"); kb.adjust(2)
    await msg.answer(
        f"🆔 Buyurtma IDsi: {o[0]}\n\n{o[12]} - 👤 {o[13]}\n\n"
        f"♻️ Holat: {se} {o[6]}\n🔗 Havola: {o[3]}\n"
        f"📊 Miqdor: {o[4]} ta\n💰 Narxi: {o[5]} So'm\n📅 Sana: {o[7][:19]}",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data=="back_adm")
async def back_adm(call: types.CallbackQuery):
    await call.message.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=admin_kb())

# ==================== MAIN ====================
async def main():
    init_db()
    log.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
