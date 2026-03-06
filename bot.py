"""
Nakrutka SMM Bot — videodagi aynan bir xil
"""
import asyncio, logging, sqlite3, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ─── CONFIG ───────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "TOKEN_BU_YERGA")
ADMIN_IDS  = [int(x) for x in os.getenv("ADMIN_IDS", "8537782289").split(",")]
# ─────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())


# ═══════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════
def db():
    return sqlite3.connect("bot.db")

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id        INTEGER PRIMARY KEY,
        username  TEXT DEFAULT '',
        name      TEXT DEFAULT '',
        balance   INTEGER DEFAULT 0,
        deposited INTEGER DEFAULT 0,
        ref_id    INTEGER,
        banned    INTEGER DEFAULT 0,
        joined    TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS networks(
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS sections(
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        net_id INTEGER,
        name   TEXT
    );
    CREATE TABLE IF NOT EXISTS services(
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        sec_id INTEGER,
        api_id TEXT DEFAULT '',
        name   TEXT DEFAULT '',
        price  INTEGER DEFAULT 0,
        min_q  INTEGER DEFAULT 100,
        max_q  INTEGER DEFAULT 100000,
        info   TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS orders(
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        uid    INTEGER,
        srv_id INTEGER,
        link   TEXT,
        qty    INTEGER,
        price  INTEGER,
        status TEXT DEFAULT 'Bajarilmoqda',
        at     TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS faqs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        q  TEXT,
        a  TEXT
    );
    CREATE TABLE IF NOT EXISTS channels(
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        cid   TEXT,
        title TEXT,
        url   TEXT
    );
    CREATE TABLE IF NOT EXISTS pay_methods(
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT,
        details TEXT
    );
    CREATE TABLE IF NOT EXISTS cfg(
        k TEXT PRIMARY KEY,
        v TEXT
    );
    INSERT OR IGNORE INTO cfg VALUES('ref_bonus','500');
    INSERT OR IGNORE INTO cfg VALUES('min_dep','1000');
    INSERT OR IGNORE INTO cfg VALUES('api_url','');
    INSERT OR IGNORE INTO cfg VALUES('api_key','');
    INSERT OR IGNORE INTO cfg VALUES('currency','So''m');
    INSERT OR IGNORE INTO cfg VALUES('service_active','1');
    INSERT OR IGNORE INTO cfg VALUES('premium_emoji','1');
    """)
    c.commit(); c.close()

def gcfg(k):
    c = db(); r = c.execute("SELECT v FROM cfg WHERE k=?", (k,)).fetchone(); c.close()
    return r[0] if r else ""

def scfg(k, v):
    c = db(); c.execute("INSERT OR REPLACE INTO cfg VALUES(?,?)", (k,v)); c.commit(); c.close()

def guser(uid):
    c = db(); r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone(); c.close(); return r

def ensure_user(uid, uname, fname, ref=None):
    if guser(uid): return
    c = db()
    c.execute("INSERT OR IGNORE INTO users(id,username,name,ref_id) VALUES(?,?,?,?)", (uid,uname,fname,ref))
    if ref and ref != uid:
        bonus = int(gcfg("ref_bonus") or 500)
        c.execute("UPDATE users SET balance=balance+? WHERE id=?", (bonus, ref))
    c.commit(); c.close()

def ord_cnt(uid):
    c = db(); r = c.execute("SELECT COUNT(*) FROM orders WHERE uid=?", (uid,)).fetchone(); c.close(); return r[0]

def ref_cnt(uid):
    c = db(); r = c.execute("SELECT COUNT(*) FROM users WHERE ref_id=?", (uid,)).fetchone(); c.close(); return r[0]

def gnets():
    c = db(); r = c.execute("SELECT * FROM networks").fetchall(); c.close(); return r

def gsecs(net_id):
    c = db(); r = c.execute("SELECT * FROM sections WHERE net_id=?", (net_id,)).fetchall(); c.close(); return r

def gsrvs(sec_id):
    c = db(); r = c.execute("SELECT * FROM services WHERE sec_id=?", (sec_id,)).fetchall(); c.close(); return r

def gsrv(sid):
    c = db(); r = c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone(); c.close(); return r

def sec_names(sec_id):
    """Returns (sec_name, net_name, net_id)"""
    c = db()
    r = c.execute(
        "SELECT s.name, n.name, n.id FROM sections s JOIN networks n ON s.net_id=n.id WHERE s.id=?",
        (sec_id,)
    ).fetchone(); c.close(); return r

def mk_order(uid, srv_id, link, qty, price):
    c = db()
    c.execute("INSERT INTO orders(uid,srv_id,link,qty,price) VALUES(?,?,?,?,?)", (uid,srv_id,link,qty,price))
    oid = c.lastrowid
    c.execute("UPDATE users SET balance=balance-? WHERE id=?", (price,uid))
    c.commit(); c.close(); return oid

def gorder(oid):
    c = db()
    r = c.execute("""
        SELECT o.*, s.name, n.name, sec.name
        FROM orders o
        JOIN services s   ON o.srv_id=s.id
        JOIN sections sec ON s.sec_id=sec.id
        JOIN networks n   ON sec.net_id=n.id
        WHERE o.id=?""", (oid,)).fetchone()
    c.close(); return r

def user_ords(uid):
    c = db()
    r = c.execute("""
        SELECT o.id, n.name, sec.name, o.qty, o.price, o.status, o.link, o.at
        FROM orders o
        JOIN services s   ON o.srv_id=s.id
        JOIN sections sec ON s.sec_id=sec.id
        JOIN networks n   ON sec.net_id=n.id
        WHERE o.uid=?
        ORDER BY o.id DESC""", (uid,)).fetchall()
    c.close(); return r

def all_ords():
    c = db()
    r = c.execute("""
        SELECT o.id, o.uid, n.name, sec.name, o.qty, o.price, o.status, o.link, o.at
        FROM orders o
        JOIN services s   ON o.srv_id=s.id
        JOIN sections sec ON s.sec_id=sec.id
        JOIN networks n   ON sec.net_id=n.id
        ORDER BY o.id DESC""").fetchall()
    c.close(); return r

def stats():
    c = db(); cur = c.cursor()
    tot = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    act = cur.execute("SELECT COUNT(*) FROM users WHERE banned=0").fetchone()[0]
    n24 = cur.execute("SELECT COUNT(*) FROM users WHERE joined>=datetime('now','-1 day')").fetchone()[0]
    n7  = cur.execute("SELECT COUNT(*) FROM users WHERE joined>=datetime('now','-7 days')").fetchone()[0]
    n30 = cur.execute("SELECT COUNT(*) FROM users WHERE joined>=datetime('now','-30 days')").fetchone()[0]
    a24 = cur.execute("SELECT COUNT(DISTINCT uid) FROM orders WHERE at>=datetime('now','-1 day')").fetchone()[0]
    a7  = cur.execute("SELECT COUNT(DISTINCT uid) FROM orders WHERE at>=datetime('now','-7 days')").fetchone()[0]
    a30 = cur.execute("SELECT COUNT(DISTINCT uid) FROM orders WHERE at>=datetime('now','-30 days')").fetchone()[0]
    pay = cur.execute("SELECT COUNT(*) FROM users WHERE balance>0").fetchone()[0]
    mon = cur.execute("SELECT COALESCE(SUM(deposited),0) FROM users").fetchone()[0]
    c.close()
    return tot,act,n24,n7,n30,a24,a7,a30,pay,mon

def all_uids():
    c = db(); r = c.execute("SELECT id FROM users WHERE banned=0").fetchall(); c.close()
    return [x[0] for x in r]


# ═══════════════════════════════════════════════════════
#  REPLY KEYBOARDS
# ═══════════════════════════════════════════════════════

def kb_main(is_admin=False):
    b = ReplyKeyboardBuilder()
    b.button(text="Buyurtma berish")
    b.button(text="Buyurtmalar"); b.button(text="Hisobim")
    b.button(text="Pul ishlash"); b.button(text="Hisob to'ldirish")
    b.button(text="Murojaat");    b.button(text="Qo'llanma")
    if is_admin:
        b.button(text="🖥 Boshqaruv")
        b.adjust(1, 2, 2, 2, 1)
    else:
        b.adjust(1, 2, 2, 2)
    return b.as_markup(resize_keyboard=True)

def kb_admin():
    b = ReplyKeyboardBuilder()
    b.button(text="⚙️ Asosiy sozlamalar")
    b.button(text="📊 Statistika");            b.button(text="📨 Xabar yuborish")
    b.button(text="🔐 Majbur obuna kanallar")
    b.button(text="💳 To'lov tizimlar");       b.button(text="🔑 API")
    b.button(text="👤 Foydalanuvchini boshqarish")
    b.button(text="📚 Qo'llanmalar");          b.button(text="📈 Buyurtmalar")
    b.button(text="◀️ Orqaga")
    b.adjust(1, 2, 1, 2, 1, 2, 1)
    return b.as_markup(resize_keyboard=True)


# ═══════════════════════════════════════════════════════
#  STATES
# ═══════════════════════════════════════════════════════
class Ord(StatesGroup):
    qty  = State()
    link = State()

class Top(StatesGroup):
    method = State()
    amount = State()

class Sup(StatesGroup):
    msg = State()

class Adm(StatesGroup):
    # Broadcast
    bc_type = State(); bc_msg = State()
    # Tarmoq / bo'lim / xizmat qo'shish
    net_name  = State()
    sec_name  = State()
    srv_api   = State(); srv_name = State(); srv_price = State(); srv_info = State()
    # FAQ
    faq_q = State(); faq_a = State()
    # Kanal
    ch_id = State(); ch_title = State(); ch_url = State()
    # To'lov
    pay_name = State(); pay_det = State()
    # API
    api_url = State(); api_key = State()
    # Cfg
    cfg_val = State()
    # Foydalanuvchi
    find_uid    = State()
    add_m_amt   = State()
    rem_m_amt   = State()
    reply_msg   = State()
    ord_search  = State()
    target_uid  = State()   # helper


# ═══════════════════════════════════════════════════════
#  SUBSCRIPTION CHECK
# ═══════════════════════════════════════════════════════
async def check_sub(uid):
    chans = db().execute("SELECT * FROM channels").fetchall()
    nj = []
    for ch in chans:
        try:
            m = await bot.get_chat_member(ch[1], uid)
            if m.status in ("left","kicked","banned"): nj.append(ch)
        except: nj.append(ch)
    return not nj, nj

def kb_sub(nj):
    b = InlineKeyboardBuilder()
    for ch in nj: b.button(text=f"📢 {ch[2]}", url=ch[3])
    b.button(text="✅ Tekshirish", callback_data="chk_sub")
    b.adjust(1)
    return b.as_markup()


# ═══════════════════════════════════════════════════════
#  /start
# ═══════════════════════════════════════════════════════
@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    ref = None
    args = msg.text.split()
    if len(args) > 1:
        try: ref = int(args[1])
        except: pass
    ensure_user(uid, msg.from_user.username or "", msg.from_user.full_name or "", ref)
    u = guser(uid)
    if u and u[6]:
        await msg.answer("🚫 Siz bloklangansiz."); return
    ok, nj = await check_sub(uid)
    if not ok:
        txt = "\n".join(f"• {c[2]}" for c in nj)
        await msg.answer(f"❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n\n{txt}",
                         reply_markup=kb_sub(nj)); return
    await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(uid in ADMIN_IDS))

@dp.callback_query(F.data == "chk_sub")
async def cb_chk_sub(call: types.CallbackQuery):
    uid = call.from_user.id
    ok, nj = await check_sub(uid)
    if ok:
        await call.message.delete()
        await call.message.answer("✅ Obuna tasdiqlandi!\n🖥 Asosiy menyudasiz!",
                                  reply_markup=kb_main(uid in ADMIN_IDS))
    else:
        await call.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)


# ═══════════════════════════════════════════════════════
#  BUYURTMA BERISH
#  Oqim (aynan videodek):
#  1. "Buyurtma berish" → inline tarmoqlar + "➕ Qo'shish"
#  2. Tarmoq → inline bo'limlar + "◀️ Orqaga"
#  3. Bo'lim → xizmat kartasi (matn + "✅ Buyurtma berish" | "◀️ Orqaga")
#  4. "✅ Buyurtma berish" → "📊 Buyurtma miqdorini kiriting: ..."
#  5. Miqdor → agar balanssiz: xato + "💳 Hisobni to'ldirish"
#             agar balans yetarli: "💰 To'lov miqdorini kiriting: ..."
#  6. To'lov miqdori → "🔗 Havola kiriting"   ← BU VIDEODA YO'Q!
#     (videoda to'lov miqdori so'ralgan, keyin havola so'ralgan)
#     Aslida videoni qayta ko'rsam:
#       - Miqdor (qty) → balanssiz bo'lsa to'ldirish
#       - To'lov miqdori → foydalanuvchi to'laydi, admin tasdiqlaydi
#       - Keyin buyurtma link → havola so'raladi
#     Lekin bu "Hisob to'ldirish" jarayoni. Buyurtma berish alohida.
#     Qayta tekshiraman...
#     XULOSA: Buyurtma berish:
#       miqdor → agar balanssiz → xato
#                agar yetarli → havola → "✅ Buyurtma qabul qilindi!"
# ═══════════════════════════════════════════════════════

def kb_nets(nets, is_adm):
    b = InlineKeyboardBuilder()
    for n in nets: b.button(text=n[1], callback_data=f"N:{n[0]}")
    if is_adm: b.button(text="+ Qo'shish", callback_data="N:add")
    b.adjust(2)
    return b.as_markup()

def kb_secs(secs, net_id):
    b = InlineKeyboardBuilder()
    for s in secs: b.button(text=s[2], callback_data=f"S:{s[0]}")
    b.button(text="◀️ Orqaga", callback_data=f"NB:{net_id}")
    b.adjust(1)
    return b.as_markup()

def kb_srv_card(srv_id, sec_id):
    b = InlineKeyboardBuilder()
    b.button(text="✅ Buyurtma berish", callback_data=f"BUY:{srv_id}")
    b.button(text="◀️ Orqaga",          callback_data=f"SB:{sec_id}")
    b.adjust(1)
    return b.as_markup()


@dp.message(F.text == "Buyurtma berish")
async def h_order(msg: types.Message, state: FSMContext):
    await state.clear()
    ok, nj = await check_sub(msg.from_user.id)
    if not ok:
        await msg.answer("❗ Avval kanallarga obuna bo'ling:", reply_markup=kb_sub(nj)); return
    nets   = gnets()
    is_adm = msg.from_user.id in ADMIN_IDS
    if not nets and not is_adm:
        await msg.answer("Hozircha tarmoqlar yo'q."); return
    await msg.answer("Quyidagi ijtimoiy tarmoqlardan birini tanlang.",
                     reply_markup=kb_nets(nets, is_adm))

# ── Tarmoq callback ──────────────────────────────────────────
@dp.callback_query(F.data.startswith("N:"))
async def cb_net(call: types.CallbackQuery, state: FSMContext):
    val = call.data[2:]
    if val == "add":
        if call.from_user.id not in ADMIN_IDS: return
        await call.message.answer("📝 Yangi ijtimoiy tarmoq nomini kiriting:")
        await state.set_state(Adm.net_name); return
    net_id = int(val)
    await state.update_data(net_id=net_id)
    secs = gsecs(net_id)
    if not secs:
        if call.from_user.id in ADMIN_IDS:
            await state.update_data(sec_net_id=net_id)
            await call.message.answer("📝 Yangi bo'lim nomini kiriting:")
            await state.set_state(Adm.sec_name)
        else:
            await call.answer("Bu tarmoqda bo'lim yo'q!", show_alert=True)
        return
    await call.message.edit_text(
        "Quyidagi bo'limlardan birini tanlang.\nNarxlar 1000 tasi uchun berilgan",
        reply_markup=kb_secs(secs, net_id))

# ── Tarmoqga orqaga ──────────────────────────────────────────
@dp.callback_query(F.data.startswith("NB:"))
async def cb_net_back(call: types.CallbackQuery):
    nets = gnets()
    is_adm = call.from_user.id in ADMIN_IDS
    await call.message.edit_text("Quyidagi ijtimoiy tarmoqlardan birini tanlang.",
                                 reply_markup=kb_nets(nets, is_adm))

# ── Bo'lim callback ──────────────────────────────────────────
@dp.callback_query(F.data.startswith("S:"))
async def cb_sec(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data[2:])
    await state.update_data(sec_id=sec_id)
    srvs = gsrvs(sec_id)
    info = sec_names(sec_id)
    net_id = info[2] if info else 0
    if not srvs:
        if call.from_user.id in ADMIN_IDS:
            await state.update_data(srv_sec_id=sec_id)
            await call.message.answer("🆔 Xizmat IDsini kiriting:")
            await state.set_state(Adm.srv_api)
        else:
            await call.answer("Bu bo'limda xizmat yo'q!", show_alert=True)
        return
    # Xizmat ro'yxati — videodagi kabi raqamli tugmalar
    b = InlineKeyboardBuilder()
    for i, s in enumerate(srvs, 1):
        b.button(text=str(i), callback_data=f"SRV:{s[0]}")
    b.button(text="◀️ Orqaga", callback_data=f"NB:{net_id}")
    b.adjust(5)
    lines = "\n".join(f"{i}. {s[2] or s[3]}" for i, s in enumerate(srvs, 1))
    await call.message.edit_text(f"📋 Xizmat APIsini tanlang:\n\n{lines}", reply_markup=b.as_markup())

# ── Bo'limga orqaga ──────────────────────────────────────────
@dp.callback_query(F.data.startswith("SB:"))
async def cb_sec_back(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data[3:])
    srvs   = gsrvs(sec_id)
    info   = sec_names(sec_id)
    net_id = info[2] if info else 0
    b = InlineKeyboardBuilder()
    for i, s in enumerate(srvs, 1):
        b.button(text=str(i), callback_data=f"SRV:{s[0]}")
    b.button(text="◀️ Orqaga", callback_data=f"NB:{net_id}")
    b.adjust(5)
    lines = "\n".join(f"{i}. {s[2] or s[3]}" for i, s in enumerate(srvs, 1))
    await call.message.edit_text(f"📋 Xizmat APIsini tanlang:\n\n{lines}", reply_markup=b.as_markup())

# ── Xizmat kartasi ───────────────────────────────────────────
@dp.callback_query(F.data.startswith("SRV:"))
async def cb_srv(call: types.CallbackQuery, state: FSMContext):
    srv_id = int(call.data[4:])
    s = gsrv(srv_id)
    if not s: await call.answer("Topilmadi!"); return
    await state.update_data(srv_id=srv_id)
    info   = sec_names(s[1])
    net_nm = info[1] if info else ""
    sec_nm = info[0] if info else ""
    desc   = s[7] if s[7] else "Yo'q 💬"
    await call.message.edit_text(
        f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
        f"💰 Narxi (1000x): {s[4]} So'm\n\n"
        f"| {desc}\n\n"
        f"⬇️ Minimal: {s[5]} ta\n"
        f"⬆️ Maksimal: {s[6]} ta",
        reply_markup=kb_srv_card(srv_id, s[1]))

# ── "✅ Buyurtma berish" → miqdor so'ra ──────────────────────
@dp.callback_query(F.data.startswith("BUY:"))
async def cb_buy(call: types.CallbackQuery, state: FSMContext):
    srv_id = int(call.data[4:])
    s = gsrv(srv_id)
    await state.update_data(srv_id=srv_id)
    info   = sec_names(s[1])
    net_nm = info[1] if info else ""
    sec_nm = info[0] if info else ""
    await call.message.edit_text(
        f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
        f"📊 Buyurtma miqdorini kiriting:\n\n"
        f"⬇️ Minimal: {s[5]} ta\n"
        f"⬆️ Maksimal: {s[6]} ta")
    await state.set_state(Ord.qty)

# ── Miqdor kiritish ──────────────────────────────────────────
@dp.message(Ord.qty)
async def h_ord_qty(msg: types.Message, state: FSMContext):
    try: qty = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri son kiriting:"); return
    data = await state.get_data()
    s    = gsrv(data["srv_id"])
    if qty < s[5] or qty > s[6]:
        await msg.answer(f"❌ Miqdor {s[5]} dan {s[6]} gacha bo'lishi kerak!"); return
    price = int(qty * s[4] / 1000)
    bal   = guser(msg.from_user.id)[3]
    if bal < price:
        b = InlineKeyboardBuilder()
        b.button(text="💳 Hisobni to'ldirish", callback_data="go_top")
        await msg.answer(
            f"⚠️ Hisobingizda yetarli mablag' mavjut emas!\n\n"
            f"💰 Narxi: {price} So'm\n"
            f"📊 Miqdor: {qty} ta\n\n"
            f"Boshqa miqdor kiritib ko'ring:",
            reply_markup=b.as_markup()); return
    await state.update_data(qty=qty, price=price)
    # Videoda "💰 To'lov miqdorini kiriting" emas — bu Hisob to'ldirish.
    # Buyurtmada balans yetarli bo'lsa havola so'raladi.
    await msg.answer("🔗 Havola (link) ni kiriting:")
    await state.set_state(Ord.link)

# ── Havola kiritish ──────────────────────────────────────────
@dp.message(Ord.link)
async def h_ord_link(msg: types.Message, state: FSMContext):
    data  = await state.get_data()
    link  = msg.text.strip()
    oid   = mk_order(msg.from_user.id, data["srv_id"], link, data["qty"], data["price"])
    await state.clear()
    await msg.answer(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"🆔 Buyurtma ID si: {oid}")
    for aid in ADMIN_IDS:
        try:
            o = gorder(oid)
            await bot.send_message(aid,
                f"🆕 Yangi buyurtma!\n"
                f"🆔 ID: {oid} | 👤 {msg.from_user.id}\n"
                f"🌐 {o[10]} - {o[11]}\n"
                f"🔗 {link}\n"
                f"📊 {data['qty']} ta | 💰 {data['price']} So'm")
        except: pass

@dp.callback_query(F.data == "go_top")
async def cb_go_top(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    pays = db().execute("SELECT * FROM pay_methods").fetchall()
    if not pays:
        await call.message.answer("💳 To'lov tizimi sozlanmagan."); return
    b = InlineKeyboardBuilder()
    for p in pays: b.button(text=p[1], callback_data=f"PM:{p[0]}")
    b.adjust(1)
    await call.message.answer("To'lov tizimini tanlang:", reply_markup=b.as_markup())
    await state.set_state(Top.method)


# ═══════════════════════════════════════════════════════
#  ADMIN → TARMOQ / BO'LIM / XIZMAT QO'SHISH
# ═══════════════════════════════════════════════════════

# Tarmoq nomi
@dp.message(Adm.net_name)
async def adm_net_name(msg: types.Message, state: FSMContext):
    name = msg.text.strip()
    c = db(); c.execute("INSERT OR IGNORE INTO networks(name) VALUES(?)", (name,)); c.commit(); c.close()
    b = InlineKeyboardBuilder()
    b.button(text="+ Yana qo'shish", callback_data="NET_MORE")
    await msg.answer(f"✅ {name} - ijtimoiy tarmoqi muvaffaqiyatli qo'shildi!", reply_markup=b.as_markup())
    await state.clear()

@dp.callback_query(F.data == "NET_MORE")
async def cb_net_more(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📝 Yangi ijtimoiy tarmoq nomini kiriting:")
    await state.set_state(Adm.net_name)

# Bo'lim nomi
@dp.message(Adm.sec_name)
async def adm_sec_name(msg: types.Message, state: FSMContext):
    name = msg.text.strip()
    data = await state.get_data()
    net_id = data.get("sec_net_id") or data.get("net_id")
    c = db(); c.execute("INSERT INTO sections(net_id,name) VALUES(?,?)", (net_id, name)); c.commit(); c.close()
    b = InlineKeyboardBuilder()
    b.button(text="+ Yana bo'lim qo'shish", callback_data=f"SEC_MORE:{net_id}")
    await msg.answer(f"✅ {name} - bo'limi muvaffaqiyatli qo'shildi!", reply_markup=b.as_markup())
    await state.clear()

@dp.callback_query(F.data.startswith("SEC_MORE:"))
async def cb_sec_more(call: types.CallbackQuery, state: FSMContext):
    net_id = int(call.data[9:])
    await state.update_data(sec_net_id=net_id)
    await call.message.answer("📝 Yangi bo'lim nomini kiriting:")
    await state.set_state(Adm.sec_name)

# Xizmat: API ID
@dp.message(Adm.srv_api)
async def adm_srv_api(msg: types.Message, state: FSMContext):
    await state.update_data(srv_api=msg.text.strip())
    await msg.answer("💰 Xizmat narxini kiriting (1000 tasi uchun So'mda):")
    await state.set_state(Adm.srv_price)

# Xizmat: narx
@dp.message(Adm.srv_price)
async def adm_srv_price(msg: types.Message, state: FSMContext):
    try: price = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    await state.update_data(srv_price=price)
    await msg.answer("📝 Xizmat haqida ma'lumot kiriting:")
    await state.set_state(Adm.srv_info)

# Xizmat: ma'lumot
@dp.message(Adm.srv_info)
async def adm_srv_info(msg: types.Message, state: FSMContext):
    info = msg.text.strip()
    data = await state.get_data()
    sec_id = data.get("srv_sec_id")
    api_id = data.get("srv_api", "")
    c = db()
    c.execute("INSERT INTO services(sec_id,api_id,name,price,info) VALUES(?,?,?,?,?)",
              (sec_id, api_id, api_id, data["srv_price"], info))
    c.commit(); c.close()
    await state.clear()
    await msg.answer("✅ Xizmat muvaffaqiyatli qo'shildi!")


# ═══════════════════════════════════════════════════════
#  BUYURTMALAR (foydalanuvchi)
# ═══════════════════════════════════════════════════════

def ord_card(o):
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[5],"❓")
    return (
        f"📊 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]}\n"
        f"🗂 Xizmat: 👤 {o[2]} [ ⚡-Tezkor ]\n"
        f"♻️ Holat: {se} {o[5]}\n"
        f"📅 Sana: {o[7][:19]}\n"
        f"{'─'*24}"
    )

def ord_detail(o):
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[5],"❓")
    return (
        f"🆔 Buyurtma IDsi: {o[0]}\n\n"
        f"{o[1]} - 👤 {o[2]} [ ⚡-Tezkor ]\n\n"
        f"♻️ Holat: {se} {o[5]}\n"
        f"🔗 Havola: {o[6]}\n"
        f"📊 Miqdor: {o[3]} ta\n"
        f"💰 Narxi: {o[4]} So'm\n\n"
        f"📅 Sana: {o[7][:19]}"
    )

def kb_ord_list(ords, idx, uid):
    total = len(ords)
    b = InlineKeyboardBuilder()
    b.button(text=str(ords[idx][0]), callback_data=f"ORD_DET:{idx}:{uid}")
    if total > 1:
        prev = (idx-1) % total; nxt = (idx+1) % total
        b.button(text="⏪", callback_data=f"ORD_P:{prev}:{uid}")
        b.button(text=f"{idx+1}/{total}", callback_data="NOP")
        b.button(text="⏩", callback_data=f"ORD_P:{nxt}:{uid}")
        b.adjust(1, 3)
    else:
        b.adjust(1)
    b.button(text="🔍 Qidirish", callback_data=f"ORD_SRCH:{uid}")
    return b.as_markup()

@dp.message(F.text == "Buyurtmalar")
async def h_buyurtmalar(msg: types.Message):
    ords = user_ords(msg.from_user.id)
    if not ords: await msg.answer("📦 Sizda hali buyurtmalar yo'q."); return
    await msg.answer(ord_card(ords[0]), reply_markup=kb_ord_list(ords, 0, msg.from_user.id))

@dp.callback_query(F.data.startswith("ORD_P:"))
async def cb_ord_page(call: types.CallbackQuery):
    _, idx_s, uid_s = call.data.split(":")
    idx = int(idx_s); uid = int(uid_s)
    ords = user_ords(uid)
    idx  = idx % len(ords)
    await call.message.edit_text(ord_card(ords[idx]),
                                 reply_markup=kb_ord_list(ords, idx, uid))

@dp.callback_query(F.data.startswith("ORD_DET:"))
async def cb_ord_det(call: types.CallbackQuery):
    _, idx_s, uid_s = call.data.split(":")
    idx = int(idx_s); uid = int(uid_s)
    ords = user_ords(uid)
    idx  = idx % len(ords); o = ords[idx]
    b = InlineKeyboardBuilder()
    b.button(text="◀️ Orqaga", callback_data=f"ORD_BACK:{idx}:{uid}")
    await call.message.edit_text(ord_detail(o), reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("ORD_BACK:"))
async def cb_ord_back(call: types.CallbackQuery):
    _, idx_s, uid_s = call.data.split(":")
    idx = int(idx_s); uid = int(uid_s)
    ords = user_ords(uid)
    idx  = idx % len(ords)
    await call.message.edit_text(ord_card(ords[idx]),
                                 reply_markup=kb_ord_list(ords, idx, uid))

@dp.callback_query(F.data.startswith("ORD_SRCH:"))
async def cb_ord_srch(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🔍 Buyurtma ID raqamini kiriting:")
    await state.set_state(Adm.ord_search)
    await state.update_data(srch_mode="user")

@dp.callback_query(F.data == "NOP")
async def cb_nop(call: types.CallbackQuery): await call.answer()


# ═══════════════════════════════════════════════════════
#  HISOBIM
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "Hisobim")
async def h_hisobim(msg: types.Message):
    uid = msg.from_user.id; u = guser(uid)
    if not u: return
    b = InlineKeyboardBuilder()
    b.button(text="Hisobni to'ldirish", callback_data="go_top")
    await msg.answer(
        f"👤 Sizning ID raqamingiz: {uid}\n\n"
        f"💰 Balansingiz: {u[3]} So'm\n"
        f"📦 Buyurtmalaringiz: {ord_cnt(uid)} ta\n"
        f"👥 Referallaringiz: {ref_cnt(uid)} ta\n"
        f"💵 Kiritgan pullaringiz: {u[4]} So'm",
        reply_markup=b.as_markup())


# ═══════════════════════════════════════════════════════
#  HISOB TO'LDIRISH
#  Videodagi oqim:
#  1. Tizim tanlash (Payme/Click, Uzcart, Orqaga)
#  2. "💰 To'lov miqdorini kiriting: Minimal: 1 000 so'm"
#  3. Miqdor kiritilsa → "⏳ Qabul qilindi! To'lovingiz 5 daqiqadan..."
#  4. Admin tasdiqlaydi → "✅ To'lovingiz tastiqlandi! Hisobingiz X So'm ga to'ldirildi."
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "Hisob to'ldirish")
async def h_topup(msg: types.Message, state: FSMContext):
    pays = db().execute("SELECT * FROM pay_methods").fetchall()
    if not pays: await msg.answer("💳 To'lov tizimi hali sozlanmagan."); return
    b = InlineKeyboardBuilder()
    for p in pays: b.button(text=p[1], callback_data=f"PM:{p[0]}")
    b.adjust(1)
    await msg.answer("To'lov tizimini tanlang:", reply_markup=b.as_markup())
    await state.set_state(Top.method)

@dp.callback_query(F.data.startswith("PM:"), Top.method)
async def cb_pay_method(call: types.CallbackQuery, state: FSMContext):
    pid = int(call.data[3:])
    p   = db().execute("SELECT * FROM pay_methods WHERE id=?", (pid,)).fetchone()
    if not p: await call.answer("Topilmadi!"); return
    await state.update_data(pay_name=p[1], pay_det=p[2])
    min_d = gcfg("min_dep") or "1000"
    await call.message.edit_text(
        f"💰 To'lov miqdorini kiriting:\n\nMinimal: {min_d} So'm")
    await state.set_state(Top.amount)

@dp.message(Top.amount)
async def h_topup_amt(msg: types.Message, state: FSMContext):
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri miqdor!"); return
    min_d = int(gcfg("min_dep") or 1000)
    if amt < min_d:
        await msg.answer(
            f"❌ To'lov qilishda xatolik yuz berdi.\n"
            f"Iltimos, qayta urinib ko'ring."); return
    data = await state.get_data(); await state.clear()
    uid  = msg.from_user.id
    b = InlineKeyboardBuilder()
    b.button(text="✅ To'lovni tasdiqlash", callback_data=f"PAY_OK:{uid}:{amt}")
    b.button(text="❌ Bekor",               callback_data="PAY_CANCEL"); b.adjust(1)
    await msg.answer(
        f"💳 To'lov ma'lumotlari:\n\n"
        f"💰 Miqdor: {amt} So'm\n"
        f"🏦 Tizim: {data['pay_name']}\n\n"
        f"{data['pay_det']}\n\n"
        f"⚠️ To'lovni amalga oshirgach 'Tasdiqlash' tugmasini bosing!",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("PAY_OK:"))
async def cb_pay_ok(call: types.CallbackQuery):
    _, uid_s, amt_s = call.data.split(":")
    uid = int(uid_s); amt = int(amt_s)
    await call.message.edit_text(
        "⏳ Qabul qilindi!\n\n"
        "To'lovingiz 5 daqiqadan 24 soatgacha bo'lgan vaqt ichida amalga oshiriladi!")
    for aid in ADMIN_IDS:
        try:
            b = InlineKeyboardBuilder()
            b.button(text="✅ Tasdiqlash", callback_data=f"ADM_POK:{uid}:{amt}")
            b.button(text="❌ Rad etish",  callback_data=f"ADM_PNO:{uid}"); b.adjust(2)
            await bot.send_message(aid,
                f"💳 To'lov so'rovi!\n\n👤 User ID: {uid}\n💰 Miqdor: {amt} So'm",
                reply_markup=b.as_markup())
        except: pass

@dp.callback_query(F.data == "PAY_CANCEL")
async def cb_pay_cancel(call: types.CallbackQuery):
    await call.message.edit_text("❌ Bekor qilindi.")

@dp.callback_query(F.data.startswith("ADM_POK:"))
async def cb_adm_pok(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    _, uid_s, amt_s = call.data.split(":")
    uid = int(uid_s); amt = int(amt_s)
    c = db()
    c.execute("UPDATE users SET balance=balance+?,deposited=deposited+? WHERE id=?", (amt,amt,uid))
    c.commit(); c.close()
    await call.message.edit_text(f"✅ {uid} ga {amt} So'm qo'shildi!")
    try:
        await bot.send_message(uid,
            f"✅ To'lovingiz tastiqlandi!\n\n"
            f"Hisobingiz {amt} So'm ga to'ldirildi.")
    except: pass

@dp.callback_query(F.data.startswith("ADM_PNO:"))
async def cb_adm_pno(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[8:])
    await call.message.edit_text(f"❌ {uid} ning to'lovi rad etildi.")
    try: await bot.send_message(uid, "❌ To'lovingiz rad etildi.")
    except: pass


# ═══════════════════════════════════════════════════════
#  PUL ISHLASH (referal)
#  Videodagi ko'rinish:
#  "1 ta referal uchun 500 So'm beriladi
#   👥 Referallaringiz: 0 ta"
#  [◀️ Orqaga]
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "Pul ishlash")
async def h_earn(msg: types.Message):
    uid   = msg.from_user.id
    binfo = await bot.get_me()
    link  = f"https://t.me/{binfo.username}?start={uid}"
    bonus = gcfg("ref_bonus") or "500"
    b = InlineKeyboardBuilder()
    b.button(text="◀️ Orqaga", callback_data="EARN_BACK")
    await msg.answer(
        f"🔗 Sizning referal havolangiz:\n\n{link}\n\n"
        f"1 ta referal uchun {bonus} So'm beriladi\n\n"
        f"👥 Referallaringiz: {ref_cnt(uid)} ta",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "EARN_BACK")
async def cb_earn_back(call: types.CallbackQuery): await call.message.delete()


# ═══════════════════════════════════════════════════════
#  MUROJAAT
#  Videodagi oqim:
#  "📝 Murojaat matnini yozib yuboring."
#  Xabar → "⏳ Murojaatingiz qabul qilindi!..."
#  Admin: foydalanuvchi nomi + [📝 Javob yozish]
#  Admin "Javob yozish" → "XID Foydalanuvchiga yuboriladigan xabaringizni kiriting."
#  Javob yuborilsa → "✅ Xabar foydalanuvchiga yuborildi!"
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "Murojaat")
async def h_murojaat(msg: types.Message, state: FSMContext):
    await msg.answer("📝 Murojaat matnini yozib yuboring.")
    await state.set_state(Sup.msg)

@dp.message(Sup.msg)
async def h_sup_msg(msg: types.Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    await msg.answer(
        "⏳ Murojaatingiz qabul qilindi!\n\n"
        "Tez orada murojaatingizni ko'rib chiqamiz.")
    for aid in ADMIN_IDS:
        try:
            b = InlineKeyboardBuilder()
            b.button(text="📝 Javob yozish", callback_data=f"REP:{uid}")
            await bot.send_message(aid,
                f"📩 Yangi murojaat!\n"
                f"👤 {msg.from_user.full_name} (ID: {uid})\n\n"
                f"{msg.text}",
                reply_markup=b.as_markup())
        except: pass

@dp.callback_query(F.data.startswith("REP:"))
async def cb_rep(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[4:])
    await state.update_data(target_uid=uid)
    await call.message.answer(
        f"{uid} Foydalanuvchiga yuboriladigan xabaringizni kiriting.")
    await state.set_state(Adm.reply_msg)

@dp.message(Adm.reply_msg)
async def adm_rep_send(msg: types.Message, state: FSMContext):
    uid = (await state.get_data())["target_uid"]; await state.clear()
    try:
        await bot.send_message(uid, f"📩 Admin javobi:\n\n{msg.text}")
        await msg.answer("✅ Xabar foydalanuvchiga yuborildi!")
    except: await msg.answer("❌ Yuborib bo'lmadi.")


# ═══════════════════════════════════════════════════════
#  QO'LLANMA
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "Qo'llanma")
async def h_faq(msg: types.Message):
    faqs = db().execute("SELECT * FROM faqs").fetchall()
    if not faqs: await msg.answer("Hozircha qo'llanmalar yo'q."); return
    b = InlineKeyboardBuilder()
    for f in faqs: b.button(text=f[1][:35], callback_data=f"FAQ:{f[0]}")
    b.adjust(1)
    await msg.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("FAQ:"))
async def cb_faq(call: types.CallbackQuery):
    fid = int(call.data[4:])
    f   = db().execute("SELECT * FROM faqs WHERE id=?", (fid,)).fetchone()
    if f: await call.message.answer(f"❓ {f[1]}\n\n💬 {f[2]}")


# ═══════════════════════════════════════════════════════
#  ORQAGA
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "◀️ Orqaga")
async def h_back(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS))


# ═══════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════
@dp.message(F.text == "🖥 Boshqaruv")
async def h_admin(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin())

# ── Asosiy sozlamalar ────────────────────────────────────────
# Videoda ko'rindi: Referal, Valyuta, Xizmat bajarilish vaqti, Premium emoji
@dp.message(F.text == "⚙️ Asosiy sozlamalar")
async def h_adm_cfg(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    ref  = gcfg("ref_bonus")
    cur  = gcfg("currency")
    svc  = "✅ Faol" if gcfg("service_active")=="1" else "❌ Nofaol"
    prem = "✅ Faol" if gcfg("premium_emoji")=="1"  else "❌ Nofaol"
    b = InlineKeyboardBuilder()
    b.button(text=f"💵 Referal o'zgartirish",    callback_data="CFG:ref_bonus")
    b.button(text=f"💱 Valyuta o'zgartirish",    callback_data="CFG:currency")
    b.button(text=f"⏱ Xizmat vaqti: {svc}",     callback_data="CFG:svc_toggle")
    b.button(text=f"✨ Premium emoji: {prem}",   callback_data="CFG:prem_toggle")
    b.adjust(1)
    await msg.answer(
        f"⚙️ Asosiy sozlamalar:\n\n"
        f"◆ Referal: {ref} So'm\n"
        f"◆ Valyuta: {cur}\n"
        f"◆ Xizmat bajarilish vaqti: {svc}\n"
        f"◆ Premium emoji: {prem}\n\n"
        f"Premium emoji faqat Telegramda premium obunasi bor foydalanuvchi botlarida ishlaydi.",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("CFG:"))
async def cb_cfg(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    key = call.data[4:]
    if key == "svc_toggle":
        cur = gcfg("service_active"); scfg("service_active", "0" if cur=="1" else "1")
        await call.answer("✅ O'zgartirildi!", show_alert=True)
        await h_adm_cfg.__wrapped__(call.message) if hasattr(h_adm_cfg, '__wrapped__') else None
        return
    if key == "prem_toggle":
        cur = gcfg("premium_emoji"); scfg("premium_emoji", "0" if cur=="1" else "1")
        await call.answer("✅ O'zgartirildi!", show_alert=True); return
    labels = {"ref_bonus": "Yangi referal bonus miqdorini kiriting (So'mda):",
              "currency":  "Yangi valyuta nomini kiriting (masalan: So'm):"}
    await state.update_data(cfg_key=key)
    await call.message.answer(labels.get(key, "Yangi qiymat kiriting:"))
    await state.set_state(Adm.cfg_val)

@dp.message(Adm.cfg_val)
async def adm_cfg_val(msg: types.Message, state: FSMContext):
    key = (await state.get_data())["cfg_key"]; await state.clear()
    scfg(key, msg.text.strip())
    await msg.answer("✅ Saqlandi!")

# ── Statistika ───────────────────────────────────────────────
@dp.message(F.text == "📊 Statistika")
async def h_stats(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    tot,act,n24,n7,n30,a24,a7,a30,pay,mon = stats()
    binfo = await bot.get_me()
    b = InlineKeyboardBuilder()
    b.button(text="💰 TOP-50 Balans",  callback_data="T50:bal")
    b.button(text="👥 TOP-50 Referal", callback_data="T50:ref"); b.adjust(2)
    await msg.answer(
        f"📊 Statistika\n"
        f"• Obunachilar soni: {tot} ta\n"
        f"• Faol obunachilar: {act} ta\n"
        f"• Tark etganlar: {tot-act} ta\n\n"
        f"📈 Obunachilar qo'shilishi\n"
        f"• Oxirgi 24 soat: +{n24} obunachi\n"
        f"• Oxirgi 7 kun: +{n7} obunachi\n"
        f"• Oxirgi 30 kun: +{n30} obunachi\n\n"
        f"📊 Faollik\n"
        f"• Oxirgi 24 soatda faol: {a24} ta\n"
        f"• Oxirgi 7 kun faol: {a7} ta\n"
        f"• Oxirgi 30 kun faol: {a30} ta\n\n"
        f"💰 Pullar Statistikasi\n"
        f"• Puli borlar: {pay} ta\n"
        f"• Jami pullar: {mon} So'm\n\n"
        f"🤖 @{binfo.username}",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "T50:bal")
async def cb_t50_bal(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    rows = db().execute("SELECT id,name,balance FROM users ORDER BY balance DESC LIMIT 50").fetchall()
    t = "💰 TOP-50 Balans:\n\n"
    for i,r in enumerate(rows,1): t += f"{i}. {r[1] or r[0]} — {r[2]} So'm\n"
    await call.message.answer(t[:4096])

@dp.callback_query(F.data == "T50:ref")
async def cb_t50_ref(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    rows = db().execute(
        "SELECT u.id,u.name,COUNT(r.id) rc FROM users u LEFT JOIN users r ON r.ref_id=u.id "
        "GROUP BY u.id ORDER BY rc DESC LIMIT 50").fetchall()
    t = "👥 TOP-50 Referal:\n\n"
    for i,r in enumerate(rows,1): t += f"{i}. {r[1] or r[0]} — {r[2]} ta\n"
    await call.message.answer(t[:4096])

# ── Xabar yuborish ───────────────────────────────────────────
@dp.message(F.text == "📨 Xabar yuborish")
async def h_bc(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="💬 Oddiy",   callback_data="BC:n")
    b.button(text="📤 Forward", callback_data="BC:f"); b.adjust(2)
    await msg.answer("Foydalanuvchilarga yuboradigan xabar turini tanlang.", reply_markup=b.as_markup())
    await state.set_state(Adm.bc_type)

@dp.callback_query(F.data.startswith("BC:"), Adm.bc_type)
async def cb_bc_type(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(bc_type=call.data[3:])
    await call.message.answer("Xabarni yozing:")
    await state.set_state(Adm.bc_msg)

@dp.message(Adm.bc_msg)
async def adm_bc_send(msg: types.Message, state: FSMContext):
    data = await state.get_data(); await state.clear()
    uids = all_uids(); ok = fail = 0
    for uid in uids:
        try:
            if data["bc_type"]=="f": await msg.forward(uid)
            else: await bot.send_message(uid, msg.text or "")
            ok+=1; await asyncio.sleep(0.03)
        except: fail+=1
    await msg.answer(f"✅ Yuborildi: {ok}\n❌ Xato: {fail}")

# ── Majbur obuna kanallar ────────────────────────────────────
# Videodagi tugmalar: + Kanal qo'shish | 📋 Ro'yxatni ko'rish | 🗑 Kanalni o'chirish
@dp.message(F.text == "🔐 Majbur obuna kanallar")
async def h_chans(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="+ Kanal qo'shish",    callback_data="CH:add")
    b.button(text="📋 Ro'yxatni ko'rish", callback_data="CH:list")
    b.button(text="🗑 Kanalni o'chirish",  callback_data="CH:del_list")
    b.adjust(1)
    await msg.answer("🔐 Majbur obuna kanallar:", reply_markup=b.as_markup())

@dp.callback_query(F.data == "CH:add")
async def cb_ch_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Kanal ID'sini kiriting (@kanal yoki -100...):")
    await state.set_state(Adm.ch_id)

@dp.message(Adm.ch_id)
async def adm_ch_id(msg: types.Message, state: FSMContext):
    await state.update_data(ch_id=msg.text.strip())
    await msg.answer("Kanal nomini kiriting:")
    await state.set_state(Adm.ch_title)

@dp.message(Adm.ch_title)
async def adm_ch_title(msg: types.Message, state: FSMContext):
    await state.update_data(ch_title=msg.text.strip())
    await msg.answer("Kanal havolasini kiriting (https://t.me/...):")
    await state.set_state(Adm.ch_url)

@dp.message(Adm.ch_url)
async def adm_ch_url(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    c = db(); c.execute("INSERT INTO channels(cid,title,url) VALUES(?,?,?)",
                        (data["ch_id"],data["ch_title"],msg.text.strip())); c.commit(); c.close()
    await state.clear()
    await msg.answer(f"✅ {data['ch_title']} kanali qo'shildi!")

@dp.callback_query(F.data == "CH:list")
async def cb_ch_list(call: types.CallbackQuery):
    chans = db().execute("SELECT * FROM channels").fetchall()
    if not chans: await call.answer("Kanallar yo'q!", show_alert=True); return
    t = "📋 Kanallar:\n\n"
    for ch in chans: t += f"• {ch[2]} | {ch[1]}\n"
    await call.message.answer(t)

@dp.callback_query(F.data == "CH:del_list")
async def cb_ch_del_list(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    chans = db().execute("SELECT * FROM channels").fetchall()
    if not chans: await call.answer("Kanallar yo'q!", show_alert=True); return
    b = InlineKeyboardBuilder()
    for ch in chans: b.button(text=f"🗑 {ch[2]}", callback_data=f"CH:del:{ch[0]}")
    b.adjust(1)
    await call.message.answer("Qaysi kanalni o'chirmoqchisiz?", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("CH:del:"))
async def cb_ch_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    cid = int(call.data[7:])
    c = db(); c.execute("DELETE FROM channels WHERE id=?", (cid,)); c.commit(); c.close()
    await call.message.edit_text("✅ Kanal o'chirildi!")

# ── To'lov tizimlari ─────────────────────────────────────────
# Videoda: "💳 To'lov tizimlari: 1 ta" + [Uzcart] + [+ To'lov tizimi qo'shish] + [◀️ Orqaga]
@dp.message(F.text == "💳 To'lov tizimlar")
async def h_pays(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    pays = db().execute("SELECT * FROM pay_methods").fetchall()
    b = InlineKeyboardBuilder()
    for p in pays: b.button(text=p[1], callback_data=f"PAYM:del:{p[0]}")
    b.button(text="+ To'lov tizimi qo'shish", callback_data="PAYM:add")
    b.button(text="◀️ Orqaga",                callback_data="ADM_BACK"); b.adjust(1)
    await msg.answer(f"💳 To'lov tizimlari: {len(pays)} ta", reply_markup=b.as_markup())

@dp.callback_query(F.data == "PAYM:add")
async def cb_pay_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("To'lov tizimi nomini kiriting (Click, Payme, Uzcart...):")
    await state.set_state(Adm.pay_name)

@dp.message(Adm.pay_name)
async def adm_pay_name(msg: types.Message, state: FSMContext):
    await state.update_data(pay_name=msg.text.strip())
    await msg.answer("To'lov ma'lumotlarini kiriting (karta raqami va boshqalar):")
    await state.set_state(Adm.pay_det)

@dp.message(Adm.pay_det)
async def adm_pay_det(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    c = db(); c.execute("INSERT INTO pay_methods(name,details) VALUES(?,?)",
                        (data["pay_name"],msg.text.strip())); c.commit(); c.close()
    await state.clear()
    await msg.answer(f"✅ {data['pay_name']} to'lov tizimi qo'shildi!")

@dp.callback_query(F.data.startswith("PAYM:del:"))
async def cb_pay_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    pid = int(call.data[9:])
    c = db(); c.execute("DELETE FROM pay_methods WHERE id=?", (pid,)); c.commit(); c.close()
    await call.message.edit_text("✅ To'lov tizimi o'chirildi!")

@dp.callback_query(F.data == "ADM_BACK")
async def cb_adm_back(call: types.CallbackQuery):
    await call.message.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin())

# ── API ──────────────────────────────────────────────────────
@dp.message(F.text == "🔑 API")
async def h_api(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    cur = gcfg("api_url") or "(belgilanmagan)"
    await msg.answer(
        f"🔑 API manzilini kiriting:\n\n"
        f"Namuna: https://capitalsmmapi.uz/api/v2\n\n"
        f"Hozirgi: {cur}")
    await state.set_state(Adm.api_url)

@dp.message(Adm.api_url)
async def adm_api_url(msg: types.Message, state: FSMContext):
    scfg("api_url", msg.text.strip())
    await msg.answer("✅ API manzili saqlandi!\n\nAPI kalitini kiriting:")
    await state.set_state(Adm.api_key)

@dp.message(Adm.api_key)
async def adm_api_key(msg: types.Message, state: FSMContext):
    scfg("api_key", msg.text.strip()); await state.clear()
    await msg.answer("✅ API kaliti saqlandi!")

# ── Foydalanuvchini boshqarish ───────────────────────────────
@dp.message(F.text == "👤 Foydalanuvchini boshqarish")
async def h_adm_user(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("👤 Foydalanuvchining ID raqamini yuboring:")
    await state.set_state(Adm.find_uid)

@dp.message(Adm.find_uid)
async def adm_find_uid(msg: types.Message, state: FSMContext):
    try: uid = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri ID!"); return
    u = guser(uid)
    if not u: await msg.answer("❌ Foydalanuvchi topilmadi!"); await state.clear(); return
    await state.clear()
    ban_txt = "🔕 Banlash" if not u[6] else "✅ Bandan chiqarish"
    b = InlineKeyboardBuilder()
    b.button(text=f"🔔 {ban_txt}",     callback_data=f"U:ban:{uid}")
    b.button(text="+ Pul qo'shish",    callback_data=f"U:add:{uid}")
    b.button(text="— Pul ayirish",     callback_data=f"U:rem:{uid}")
    b.adjust(1, 2)
    await msg.answer(
        f"✅ Foydalanuvchi topildi!\n\n"
        f"🆔 ID raqami: {uid}\n"
        f"💰 Balansi: {u[3]} So'm\n"
        f"📦 Buyurtmalari: {ord_cnt(uid)} ta\n"
        f"👥 Referallari: {ref_cnt(uid)} ta\n"
        f"💵 Kiritgan pullar: {u[4]} So'm",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("U:ban:"))
async def cb_u_ban(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[6:])
    c = db()
    cur = c.execute("SELECT banned FROM users WHERE id=?", (uid,)).fetchone()[0]
    nw  = 0 if cur else 1
    c.execute("UPDATE users SET banned=? WHERE id=?", (nw,uid)); c.commit(); c.close()
    txt = "🔕 Banlandi" if nw else "✅ Ban olib tashlandi"
    await call.message.edit_text(f"{txt}: {uid}")

@dp.callback_query(F.data.startswith("U:add:"))
async def cb_u_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[6:])
    await state.update_data(target_uid=uid)
    await call.message.answer(f"({uid}) ning hisobiga qancha pul qo'shmoqchisiz?")
    await state.set_state(Adm.add_m_amt)

@dp.message(Adm.add_m_amt)
async def adm_add_m(msg: types.Message, state: FSMContext):
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    uid = (await state.get_data())["target_uid"]; await state.clear()
    c = db()
    c.execute("UPDATE users SET balance=balance+?,deposited=deposited+? WHERE id=?", (amt,amt,uid))
    c.commit(); c.close()
    await msg.answer(f"✅ Foydalanuvchi hisobiga {amt} So'm qo'shildi!")
    try: await bot.send_message(uid, f"💰 Hisobingizga {amt} So'm qo'shildi!")
    except: pass

@dp.callback_query(F.data.startswith("U:rem:"))
async def cb_u_rem(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[6:])
    await state.update_data(target_uid=uid)
    await call.message.answer(f"({uid}) ning hisobidan qancha pul ayirmoqchisiz?")
    await state.set_state(Adm.rem_m_amt)

@dp.message(Adm.rem_m_amt)
async def adm_rem_m(msg: types.Message, state: FSMContext):
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    uid = (await state.get_data())["target_uid"]; await state.clear()
    c = db(); c.execute("UPDATE users SET balance=balance-? WHERE id=?", (amt,uid)); c.commit(); c.close()
    await msg.answer(f"✅ Foydalanuvchi hisobidan {amt} So'm ayirildi!")

# ── Qo'llanmalar ─────────────────────────────────────────────
@dp.message(F.text == "📚 Qo'llanmalar")
async def h_adm_faq(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    faqs = db().execute("SELECT * FROM faqs").fetchall()
    b = InlineKeyboardBuilder()
    for f in faqs: b.button(text=f"🗑 {f[1][:25]}", callback_data=f"AFAQ:del:{f[0]}")
    b.button(text="➕ Qo'llanma qo'shish", callback_data="AFAQ:add"); b.adjust(1)
    await msg.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=b.as_markup())

@dp.callback_query(F.data == "AFAQ:add")
async def cb_afaq_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Qo'llanma nomini kiriting:")
    await state.set_state(Adm.faq_q)

@dp.message(Adm.faq_q)
async def adm_faq_q(msg: types.Message, state: FSMContext):
    await state.update_data(faq_q=msg.text.strip())
    await msg.answer("Qo'llanma mazmunini kiriting:")
    await state.set_state(Adm.faq_a)

@dp.message(Adm.faq_a)
async def adm_faq_a(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    c = db(); c.execute("INSERT INTO faqs(q,a) VALUES(?,?)", (data["faq_q"],msg.text.strip())); c.commit(); c.close()
    await state.clear(); await msg.answer("✅ Qo'llanma qo'shildi!")

@dp.callback_query(F.data.startswith("AFAQ:del:"))
async def cb_afaq_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    fid = int(call.data[9:])
    c = db(); c.execute("DELETE FROM faqs WHERE id=?", (fid,)); c.commit(); c.close()
    await call.message.edit_text("✅ Qo'llanma o'chirildi!")

# ── Admin: Buyurtmalar ───────────────────────────────────────
def adm_ord_card(o):
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[6],"❓")
    return (
        f"📈 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]} | 👤 User: {o[1]}\n"
        f"🌐 {o[2]} - {o[3]}\n"
        f"♻️ Holat: {se} {o[6]}\n"
        f"🔗 {o[7]}\n"
        f"📊 {o[4]} ta | 💰 {o[5]} So'm\n"
        f"📅 {o[8][:19]}\n"
        f"{'─'*24}")

def kb_adm_ords(ords, idx):
    total = len(ords)
    b = InlineKeyboardBuilder()
    if total > 1:
        prev = (idx-1)%total; nxt = (idx+1)%total
        b.button(text="⏪", callback_data=f"AOP:{prev}")
        b.button(text=f"{idx+1}/{total}", callback_data="NOP")
        b.button(text="⏩", callback_data=f"AOP:{nxt}")
        b.adjust(3)
    b.button(text="✅ Bajarildi",    callback_data=f"ADONE:{ords[idx][0]}")
    b.button(text="❌ Bekor qilish", callback_data=f"ACANCEL:{ords[idx][0]}")
    b.button(text="🔍 Qidirish",     callback_data="ASRCH")
    b.adjust(3 if total>1 else 0, 2, 1)
    return b.as_markup()

@dp.message(F.text == "📈 Buyurtmalar")
async def h_adm_ords(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    ords = all_ords()
    if not ords: await msg.answer("Buyurtmalar yo'q."); return
    await msg.answer(adm_ord_card(ords[0]), reply_markup=kb_adm_ords(ords, 0))

@dp.callback_query(F.data.startswith("AOP:"))
async def cb_aop(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    idx  = int(call.data[4:])
    ords = all_ords()
    if not ords: return
    idx  = idx % len(ords)
    await call.message.edit_text(adm_ord_card(ords[idx]), reply_markup=kb_adm_ords(ords, idx))

@dp.callback_query(F.data.startswith("ADONE:"))
async def cb_adone(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[6:])
    c = db()
    c.execute("UPDATE orders SET status='Bajarildi' WHERE id=?", (oid,))
    row = c.execute("SELECT uid FROM orders WHERE id=?", (oid,)).fetchone()
    c.commit(); c.close()
    await call.message.edit_text(f"✅ Buyurtma #{oid} bajarildi!")
    if row:
        try: await bot.send_message(row[0], f"✅ Buyurtma #{oid} bajarildi!")
        except: pass

@dp.callback_query(F.data.startswith("ACANCEL:"))
async def cb_acancel(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[8:])
    c = db()
    row = c.execute("SELECT uid,price FROM orders WHERE id=?", (oid,)).fetchone()
    if row:
        c.execute("UPDATE orders SET status='Bekor qilindi' WHERE id=?", (oid,))
        c.execute("UPDATE users SET balance=balance+? WHERE id=?", (row[1],row[0]))
        c.commit()
    c.close()
    await call.message.edit_text(f"❌ Buyurtma #{oid} bekor qilindi, pul qaytarildi!")
    if row:
        try:
            await bot.send_message(row[0],
                f"🔴 {oid} buyurtma bekor qilindi.\n\n"
                f"💰 {row[1]} So'm qaytarildi.")
        except: pass

@dp.callback_query(F.data == "ASRCH")
async def cb_asrch(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("🔍 Kerakli buyurtma ID raqamini kiriting:")
    await state.set_state(Adm.ord_search)

@dp.message(Adm.ord_search)
async def adm_ord_search(msg: types.Message, state: FSMContext):
    try: oid = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri ID!"); return
    await state.clear()
    o = gorder(oid)
    if not o: await msg.answer("❌ Buyurtma topilmadi!"); return
    se = {"Bajarilmoqda":"⏳","Bajarildi":"✅","Bekor qilindi":"❌"}.get(o[6],"❓")
    b = InlineKeyboardBuilder()
    b.button(text="✅ Bajarildi",    callback_data=f"ADONE:{oid}")
    b.button(text="❌ Bekor qilish", callback_data=f"ACANCEL:{oid}"); b.adjust(2)
    await msg.answer(
        f"🆔 Buyurtma IDsi: {oid}\n\n"
        f"{o[11]} - 👤 {o[12]}\n\n"
        f"♻️ Holat: {se} {o[6]}\n"
        f"🔗 Havola: {o[3]}\n"
        f"📊 Miqdor: {o[4]} ta\n"
        f"💰 Narxi: {o[5]} So'm\n"
        f"📅 Sana: {o[7][:19]}",
        reply_markup=b.as_markup())


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════
async def main():
    init_db()
    logging.info("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
