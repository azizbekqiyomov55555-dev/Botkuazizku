"""
Azizbek SMM Bot — videodagi AYNAN bir xil
"""
import asyncio, logging, sqlite3, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ─── CONFIG ───────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "TOKEN_BU_YERGA")
ADMIN_IDS  = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
# ──────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())


# ══════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════
def db():
    c = sqlite3.connect("bot.db")
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id        INTEGER PRIMARY KEY,
        username  TEXT    DEFAULT '',
        name      TEXT    DEFAULT '',
        balance   INTEGER DEFAULT 0,
        deposited INTEGER DEFAULT 0,
        ref_id    INTEGER,
        banned    INTEGER DEFAULT 0,
        joined    TEXT    DEFAULT CURRENT_TIMESTAMP
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
        api_id TEXT    DEFAULT '',
        name   TEXT    DEFAULT '',
        price  INTEGER DEFAULT 0,
        min_q  INTEGER DEFAULT 100,
        max_q  INTEGER DEFAULT 100000,
        info   TEXT    DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS orders(
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        uid    INTEGER,
        srv_id INTEGER,
        link   TEXT,
        qty    INTEGER,
        price  INTEGER,
        status TEXT DEFAULT 'Jarayonda',
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
    CREATE TABLE IF NOT EXISTS apis(
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        url   TEXT,
        key   TEXT,
        price INTEGER DEFAULT 0
    );
    INSERT OR IGNORE INTO cfg VALUES('ref_bonus','500');
    INSERT OR IGNORE INTO cfg VALUES('min_dep','1000');
    INSERT OR IGNORE INTO cfg VALUES('api_url','');
    INSERT OR IGNORE INTO cfg VALUES('api_key','');
    INSERT OR IGNORE INTO cfg VALUES('currency','So''m');
    INSERT OR IGNORE INTO cfg VALUES('service_active','1');
    INSERT OR IGNORE INTO cfg VALUES('premium_emoji','1');
    INSERT OR IGNORE INTO cfg VALUES('start_text','🖥 Botga xush kelibsiz!\n\nBu bot orqali SMM xizmatlarini buyurtma qilishingiz mumkin.');
    INSERT OR IGNORE INTO cfg VALUES('start_photo','');
    """)
    c.commit(); c.close()

def gcfg(k):
    c = db(); r = c.execute("SELECT v FROM cfg WHERE k=?", (k,)).fetchone()
    c.close(); return r[0] if r else ""

def scfg(k, v):
    c = db(); c.execute("INSERT OR REPLACE INTO cfg VALUES(?,?)", (k,v))
    c.commit(); c.close()

def get_user(uid):
    c = db(); r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close(); return r

def ensure_user(uid, uname, fname, ref=None):
    if get_user(uid): return
    c = db()
    c.execute("INSERT OR IGNORE INTO users(id,username,name,ref_id) VALUES(?,?,?,?)",
              (uid, uname, fname, ref))
    if ref and ref != uid:
        bonus = int(gcfg("ref_bonus") or 500)
        c.execute("UPDATE users SET balance=balance+? WHERE id=?", (bonus, ref))
    c.commit(); c.close()

def count_orders(uid):
    c = db(); r = c.execute("SELECT COUNT(*) FROM orders WHERE uid=?", (uid,)).fetchone()
    c.close(); return r[0]

def count_refs(uid):
    c = db(); r = c.execute("SELECT COUNT(*) FROM users WHERE ref_id=?", (uid,)).fetchone()
    c.close(); return r[0]

def get_nets():
    c = db(); r = c.execute("SELECT * FROM networks").fetchall(); c.close(); return r

def get_secs(net_id):
    c = db(); r = c.execute("SELECT * FROM sections WHERE net_id=?", (net_id,)).fetchall()
    c.close(); return r

def get_srvs(sec_id):
    c = db(); r = c.execute("SELECT * FROM services WHERE sec_id=?", (sec_id,)).fetchall()
    c.close(); return r

def get_srv(sid):
    c = db(); r = c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone()
    c.close(); return r

def get_sec_info(sec_id):
    c = db()
    r = c.execute(
        "SELECT s.name, n.name, n.id FROM sections s "
        "JOIN networks n ON s.net_id=n.id WHERE s.id=?", (sec_id,)
    ).fetchone()
    c.close(); return r  # sec_name, net_name, net_id

def create_order(uid, srv_id, link, qty, price):
    c = db()
    c.execute("INSERT INTO orders(uid,srv_id,link,qty,price) VALUES(?,?,?,?,?)",
              (uid, srv_id, link, qty, price))
    oid = c.lastrowid
    c.execute("UPDATE users SET balance=balance-? WHERE id=?", (price, uid))
    c.commit(); c.close(); return oid

def get_order_detail(oid):
    c = db()
    r = c.execute("""
        SELECT o.id, o.uid, o.link, o.qty, o.price, o.status, o.at,
               n.name AS net_name, sec.name AS sec_name
        FROM orders o
        JOIN services s   ON o.srv_id=s.id
        JOIN sections sec ON s.sec_id=sec.id
        JOIN networks n   ON sec.net_id=n.id
        WHERE o.id=?""", (oid,)).fetchone()
    c.close(); return r

def get_user_orders(uid):
    c = db()
    r = c.execute("""
        SELECT o.id, n.name, sec.name, o.qty, o.price, o.status, o.link, o.at
        FROM orders o
        JOIN services s   ON o.srv_id=s.id
        JOIN sections sec ON s.sec_id=sec.id
        JOIN networks n   ON sec.net_id=n.id
        WHERE o.uid=? ORDER BY o.id DESC""", (uid,)).fetchall()
    c.close(); return r

def get_all_orders():
    c = db()
    r = c.execute("""
        SELECT o.id, o.uid, n.name, sec.name, o.qty, o.price, o.status, o.link, o.at
        FROM orders o
        JOIN services s   ON o.srv_id=s.id
        JOIN sections sec ON s.sec_id=sec.id
        JOIN networks n   ON sec.net_id=n.id
        ORDER BY o.id DESC""").fetchall()
    c.close(); return r

def get_stats():
    c = db(); cur = c.cursor()
    tot  = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    act  = cur.execute("SELECT COUNT(*) FROM users WHERE banned=0").fetchone()[0]
    n24  = cur.execute("SELECT COUNT(*) FROM users WHERE joined>=datetime('now','-1 day')").fetchone()[0]
    n7   = cur.execute("SELECT COUNT(*) FROM users WHERE joined>=datetime('now','-7 days')").fetchone()[0]
    n30  = cur.execute("SELECT COUNT(*) FROM users WHERE joined>=datetime('now','-30 days')").fetchone()[0]
    a24  = cur.execute("SELECT COUNT(DISTINCT uid) FROM orders WHERE at>=datetime('now','-1 day')").fetchone()[0]
    a7   = cur.execute("SELECT COUNT(DISTINCT uid) FROM orders WHERE at>=datetime('now','-7 days')").fetchone()[0]
    a30  = cur.execute("SELECT COUNT(DISTINCT uid) FROM orders WHERE at>=datetime('now','-30 days')").fetchone()[0]
    pay  = cur.execute("SELECT COUNT(*) FROM users WHERE balance>0").fetchone()[0]
    mon  = cur.execute("SELECT COALESCE(SUM(deposited),0) FROM users").fetchone()[0]
    ords = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    done = cur.execute("SELECT COUNT(*) FROM orders WHERE status='Bajarildi'").fetchone()[0]
    canc = cur.execute("SELECT COUNT(*) FROM orders WHERE status='Bekor qilindi'").fetchone()[0]
    proc = cur.execute("SELECT COUNT(*) FROM orders WHERE status='Jarayonda'").fetchone()[0]
    c.close()
    return tot,act,n24,n7,n30,a24,a7,a30,pay,mon,ords,done,canc,proc

def get_all_uids():
    c = db(); r = c.execute("SELECT id FROM users WHERE banned=0").fetchall()
    c.close(); return [x[0] for x in r]


# ══════════════════════════════════════════
#  KLAVIATURALAR
# ══════════════════════════════════════════
def kb_main(is_admin=False):
    b = ReplyKeyboardBuilder()
    b.button(text="Buyurtma berish")
    b.button(text="Buyurtmalar");    b.button(text="Hisobim")
    b.button(text="Pul ishlash");    b.button(text="Hisob to'ldirish")
    b.button(text="Murojaat");       b.button(text="Qo'llanma")
    if is_admin:
        b.button(text="🖥 Boshqaruv")
        b.adjust(1, 2, 2, 2, 1)
    else:
        b.adjust(1, 2, 2, 2)
    return b.as_markup(resize_keyboard=True)

def kb_back():
    b = ReplyKeyboardBuilder()
    b.button(text="Orqaga")
    return b.as_markup(resize_keyboard=True)

def kb_admin():
    b = ReplyKeyboardBuilder()
    b.button(text="⚙️ Asosiy sozlamalar")
    b.button(text="📊 Statistika");            b.button(text="📨 Xabar yuborish")
    b.button(text="🔐 Majbur obuna kanallar")
    b.button(text="💳 To'lov tizimlar");       b.button(text="🔑 API")
    b.button(text="👤 Foydalanuvchini boshqarish")
    b.button(text="📚 Qo'llanmalar");          b.button(text="📈 Buyurtmalar")
    b.button(text="✉️ Start xabar")
    b.button(text="◀️ Orqaga")
    b.adjust(1, 2, 1, 2, 1, 2, 1, 1)
    return b.as_markup(resize_keyboard=True)


# ══════════════════════════════════════════
#  STATES
# ══════════════════════════════════════════
class OrdS(StatesGroup):
    qty  = State()
    link = State()
    confirm = State()

class PayS(StatesGroup):
    choose = State()
    amount = State()
    screenshot = State()

class SuppS(StatesGroup):
    msg = State()

class AdmS(StatesGroup):
    bc_type    = State(); bc_msg    = State()
    net_name   = State()
    sec_name   = State()
    srv_api    = State(); srv_price  = State(); srv_info = State()
    faq_q      = State(); faq_a     = State()
    ch_cid     = State(); ch_title  = State(); ch_url   = State()
    ch_type    = State()
    pay_name   = State(); pay_det   = State()
    api_url    = State(); api_key   = State(); api_price = State()
    api_new_key = State()
    cfg_key    = State(); cfg_val   = State()
    find_uid   = State()
    add_amt    = State(); rem_amt   = State()
    rep_uid    = State(); rep_msg   = State()
    ord_srch   = State()
    start_msg  = State()
    start_photo_st = State()


# ══════════════════════════════════════════
#  OBUNA TEKSHIRISH
# ══════════════════════════════════════════
async def check_sub(uid):
    chans = db().execute("SELECT * FROM channels").fetchall()
    not_joined = []
    for ch in chans:
        cid = ch['cid']
        if cid in ("link", "private"):
            # Oddiy havola / shaxsiy — foydalanuvchi bosmasa ham o'tishi kerak
            # Bu kanallar faqat ko'rsatiladi, tekshirilmaydi
            not_joined.append(ch)
            continue
        try:
            m = await bot.get_chat_member(cid, uid)
            if m.status in ("left", "kicked", "banned"):
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    # Agar faqat "link" yoki "private" turlar bo'lsa — tekshiruv o'tkazilmaydi
    real_check = [ch for ch in not_joined if ch['cid'] not in ("link", "private")]
    return len(real_check) == 0, not_joined

def kb_sub(nj):
    b = InlineKeyboardBuilder()
    for ch in nj:
        b.button(text=f"📢 {ch['title']}", url=ch['url'])
    b.button(text="✅ Tekshirish", callback_data="chk_sub")
    b.adjust(1)
    return b.as_markup()


# ══════════════════════════════════════════
#  /start
# ══════════════════════════════════════════
@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    uid  = msg.from_user.id
    ref  = None
    args = msg.text.split()
    if len(args) > 1:
        try: ref = int(args[1])
        except: pass
    ensure_user(uid, msg.from_user.username or "", msg.from_user.full_name or "", ref)
    u = get_user(uid)
    if u and u['banned']:
        await msg.answer("🚫 Siz bloklangansiz."); return
    ok, nj = await check_sub(uid)
    if not ok:
        await msg.answer(
            "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=kb_sub(nj)); return
    # Start xabari
    start_text  = gcfg("start_text") or "🖥 Asosiy menyudasiz!"
    start_photo = gcfg("start_photo") or ""
    kb = kb_main(uid in ADMIN_IDS)
    if start_photo:
        try:
            await msg.answer_photo(start_photo, caption=start_text,
                                   reply_markup=kb, parse_mode="HTML")
            return
        except: pass
    await msg.answer(start_text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "chk_sub")
async def cb_chk_sub(call: types.CallbackQuery):
    uid = call.from_user.id
    ok, nj = await check_sub(uid)
    if ok:
        await call.message.delete()
        start_text  = gcfg("start_text") or "🖥 Asosiy menyudasiz!"
        start_photo = gcfg("start_photo") or ""
        kb = kb_main(uid in ADMIN_IDS)
        if start_photo:
            try:
                await call.message.answer_photo(start_photo, caption=start_text,
                                                reply_markup=kb, parse_mode="HTML")
                return
            except: pass
        await call.message.answer(start_text, reply_markup=kb, parse_mode="HTML")
    else:
        real = [ch for ch in nj if ch['cid'] not in ("link", "private")]
        if not real:
            await call.message.delete()
            start_text  = gcfg("start_text") or "🖥 Asosiy menyudasiz!"
            start_photo = gcfg("start_photo") or ""
            kb = kb_main(uid in ADMIN_IDS)
            if start_photo:
                try:
                    await call.message.answer_photo(start_photo, caption=start_text,
                                                    reply_markup=kb, parse_mode="HTML")
                    return
                except: pass
            await call.message.answer(start_text, reply_markup=kb, parse_mode="HTML")
        else:
            await call.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)


# ══════════════════════════════════════════
#  BUYURTMA BERISH
#  Video oqimi:
#  1. "Buyurtma berish" → inline tarmoqlar + "+ Qo'shish"
#  2. Tarmoq → inline bo'limlar + "◀️ Orqaga"
#     (bo'lim yo'q → admin: "⚠️ Bo'limlar mavjud emas!" + "+ Qo'shish" tugmasi)
#  3. Bo'lim → xizmatlar ro'yxati inline:
#     "👤 Obunachi [ ⚡-Tezkor ] - 15000 So'm" + "◀️ Orqaga"
#  4. Xizmat bosildi → karta:
#     "Telgram - 👤 Obunachi [ ⚡-Tezkor ]
#      💰 Narxi (1000x): 15000 So'm
#      | Yo'q 💬
#      ⬇️ Minimal: 100 ta
#      ⬆️ Maksimal: 100000 ta"
#     + "✅ Buyurtma berish" | "◀️ Orqaga"
#  5. "✅ Buyurtma berish" bosildi →
#     "Telgram - 👤 Obunachi [ ⚡-Tezkor ]
#      📊 Buyurtma miqdorini kiriting:
#      ⬇️ Minimal: 100 ta
#      ⬆️ Maksimal: 100000 ta"
#     (reply keyboard: "Orqaga")
#  6. Miqdor kiritildi → balanssiz bo'lsa:
#     inline: to'lov tizimlari + "◀️ Orqaga"
#     balans yetarli bo'lsa → havola so'ra
#  7. To'lov tanlandi → "💰 To'lov miqdorini kiriting: Minimal: 1000 So'm"
#  8. Miqdor → "📝 To'lov chekini rasmga olib yuboring" (rasm so'rash)
#  9. Rasm → "⏳ Qabul qilindi!..."
#     Admin: ✅ / ❌ tugmalar
#     Admin tasdiqlasa → "✅ To'lovingiz tastiqlandi! Hisobingiz X ga to'ldirildi."
#  10. Balans to'ldirilgach → bot o'zi "🔗 Buyurtma havolasini kiriting..."
#  11. Havola kiritildi →
#     "ℹ️ Buyurtmam haqida malumot:
#      Telgram - 👤 Obunachi [ ⚡-Tezkor ]
#      💰 Narxi: 1500 So'm
#      🔗 Havola: ...
#      📊 Miqdor: 100 ta
#      ⚠️ Malumotlar to'g'ri bo'lsa (✅ Tasdiqlash) tugmasini bosing..."
#     + "✅ Tasdiqlash"
#  12. Tasdiqlash → "✅ Buyurtma qabul qilindi! 🆔 Buyurtma ID si: 1"
# ══════════════════════════════════════════

def kb_nets(nets, is_adm):
    b = InlineKeyboardBuilder()
    for n in nets:
        b.button(text=n['name'], callback_data=f"NET:{n['id']}")
    if is_adm:
        b.button(text="+ Qo'shish", callback_data="NET:add")
    b.adjust(2)
    return b.as_markup()

@dp.message(F.text == "Buyurtma berish")
async def h_buyurtma(msg: types.Message, state: FSMContext):
    await state.clear()
    ok, nj = await check_sub(msg.from_user.id)
    if not ok:
        await msg.answer("❗ Avval kanallarga obuna bo'ling:", reply_markup=kb_sub(nj)); return
    nets   = get_nets()
    is_adm = msg.from_user.id in ADMIN_IDS
    if not nets and not is_adm:
        await msg.answer("Hozircha tarmoqlar yo'q."); return
    await msg.answer("Quyidagi ijtimoiy tarmoqlardan birini tanlang.",
                     reply_markup=kb_nets(nets, is_adm))

# ── Tarmoq tanlash ──────────────────────
@dp.callback_query(F.data.startswith("NET:"))
async def cb_net(call: types.CallbackQuery, state: FSMContext):
    val = call.data[4:]
    if val == "add":
        if call.from_user.id not in ADMIN_IDS: return
        await call.message.answer("📝 Yangi ijtimoiy tarmoq nomini kiriting:", reply_markup=kb_back())
        await state.set_state(AdmS.net_name); return

    net_id = int(val)
    await state.update_data(net_id=net_id)
    secs   = get_secs(net_id)
    is_adm = call.from_user.id in ADMIN_IDS

    if not secs:
        # Videoda: "⚠️ Bo'limlar mavjud emas!" + "+ Qo'shish" + "📝 Tahrirlash" + "🗑 O'chirish" + "◀️ Orqaga"
        b = InlineKeyboardBuilder()
        if is_adm:
            b.button(text="+ Qo'shish",     callback_data=f"SEC_ADD:{net_id}")
            b.button(text="📝 Tahrirlash",  callback_data=f"NET_EDIT:{net_id}")
            b.button(text="🗑 O'chirish",   callback_data=f"NET_DEL:{net_id}")
        b.button(text="◀️ Orqaga", callback_data="NET_BACK")
        b.adjust(1)
        await call.message.edit_text("⚠️ Bo'limlar mavjud emas!", reply_markup=b.as_markup()); return

    b = InlineKeyboardBuilder()
    for s in secs:
        b.button(text=s['name'], callback_data=f"SEC:{s['id']}")
    b.button(text="◀️ Orqaga", callback_data="NET_BACK")
    b.adjust(1)
    await call.message.edit_text(
        "Quyidagi bo'limlardan birini tanlang.\nNarxlar 1000 tasi uchun berilgan",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "NET_BACK")
async def cb_net_back(call: types.CallbackQuery):
    nets   = get_nets()
    is_adm = call.from_user.id in ADMIN_IDS
    await call.message.edit_text("Quyidagi ijtimoiy tarmoqlardan birini tanlang.",
                                  reply_markup=kb_nets(nets, is_adm))

# ── Bo'lim tanlash ──────────────────────
@dp.callback_query(F.data.startswith("SEC:"))
async def cb_sec(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data[4:])
    await state.update_data(sec_id=sec_id)
    srvs   = get_srvs(sec_id)
    info   = get_sec_info(sec_id)
    net_id = info[2] if info else 0
    is_adm = call.from_user.id in ADMIN_IDS

    if not srvs:
        b = InlineKeyboardBuilder()
        if is_adm:
            b.button(text="+ Qo'shish", callback_data=f"SRV_ADD:{sec_id}")
        b.button(text="◀️ Orqaga", callback_data=f"SEC_BACK:{net_id}")
        b.adjust(1)
        await call.message.edit_text("⚠️ Xizmatlar mavjud emas!", reply_markup=b.as_markup()); return

    # Videoda: "👤 Obunachi [ ⚡-Tezkor ] - 15000 So'm"
    b = InlineKeyboardBuilder()
    for s in srvs:
        label = f"👤 {info[0] if info else ''} [ ⚡-Tezkor ] - {s['price']} So'm"
        b.button(text=label, callback_data=f"SRV:{s['id']}")
    b.button(text="◀️ Orqaga", callback_data=f"SEC_BACK:{net_id}")
    b.adjust(1)
    await call.message.edit_text(
        "Quyidagi xizmatlardan birini tanlang:\nNarxlar 1000 tasi uchun berilgan",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("SEC_BACK:"))
async def cb_sec_back(call: types.CallbackQuery, state: FSMContext):
    net_id = int(call.data[9:])
    secs   = get_secs(net_id)
    is_adm = call.from_user.id in ADMIN_IDS
    if not secs:
        b = InlineKeyboardBuilder()
        if is_adm:
            b.button(text="+ Qo'shish",    callback_data=f"SEC_ADD:{net_id}")
            b.button(text="📝 Tahrirlash", callback_data=f"NET_EDIT:{net_id}")
            b.button(text="🗑 O'chirish",  callback_data=f"NET_DEL:{net_id}")
        b.button(text="◀️ Orqaga", callback_data="NET_BACK")
        b.adjust(1)
        await call.message.edit_text("⚠️ Bo'limlar mavjud emas!", reply_markup=b.as_markup()); return
    b = InlineKeyboardBuilder()
    for s in secs:
        b.button(text=s['name'], callback_data=f"SEC:{s['id']}")
    b.button(text="◀️ Orqaga", callback_data="NET_BACK")
    b.adjust(1)
    await call.message.edit_text(
        "Quyidagi bo'limlardan birini tanlang.\nNarxlar 1000 tasi uchun berilgan",
        reply_markup=b.as_markup())

# ── Xizmat kartasi ──────────────────────
@dp.callback_query(F.data.startswith("SRV:"))
async def cb_srv(call: types.CallbackQuery, state: FSMContext):
    srv_id = int(call.data[4:])
    s      = get_srv(srv_id)
    if not s: await call.answer("Topilmadi!"); return
    await state.update_data(srv_id=srv_id)
    info   = get_sec_info(s['sec_id'])
    net_nm = info[1] if info else ""
    sec_nm = info[0] if info else ""
    desc   = s['info'] if s['info'] and s['info'] != "Yo'q" else "Yo'q 💬"

    b = InlineKeyboardBuilder()
    b.button(text="✅ Buyurtma berish", callback_data=f"BUY:{srv_id}")
    b.button(text="◀️ Orqaga",          callback_data=f"SRV_BACK:{s['sec_id']}")
    b.adjust(1)
    await call.message.edit_text(
        f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
        f"💰 Narxi (1000x): {s['price']} So'm\n\n"
        f"| {desc}\n\n"
        f"⬇️ Minimal: {s['min_q']} ta\n"
        f"⬆️ Maksimal: {s['max_q']} ta",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("SRV_BACK:"))
async def cb_srv_back(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data[9:])
    srvs   = get_srvs(sec_id)
    info   = get_sec_info(sec_id)
    net_id = info[2] if info else 0
    b      = InlineKeyboardBuilder()
    for s in srvs:
        label = f"👤 {info[0] if info else ''} [ ⚡-Tezkor ] - {s['price']} So'm"
        b.button(text=label, callback_data=f"SRV:{s['id']}")
    b.button(text="◀️ Orqaga", callback_data=f"SEC_BACK:{net_id}")
    b.adjust(1)
    await call.message.edit_text(
        "Quyidagi xizmatlardan birini tanlang:\nNarxlar 1000 tasi uchun berilgan",
        reply_markup=b.as_markup())

# ── "✅ Buyurtma berish" bosildi ─────────
@dp.callback_query(F.data.startswith("BUY:"))
async def cb_buy(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    srv_id = int(call.data[4:])
    s = get_srv(srv_id)
    if not s: await call.answer("Topilmadi!"); return
    await state.update_data(srv_id=srv_id)
    info   = get_sec_info(s['sec_id'])
    net_nm = info[1] if info else ""
    sec_nm = info[0] if info else ""
    await call.answer()
    await call.message.answer(
        f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
        f"📊 Buyurtma miqdorini kiriting:\n\n"
        f"⬇️ Minimal: {s['min_q']} ta\n"
        f"⬆️ Maksimal: {s['max_q']} ta",
        reply_markup=kb_back())
    await state.set_state(OrdS.qty)

# ── Miqdor kiritish ──────────────────────
@dp.message(OrdS.qty)
async def h_qty(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        data = await state.get_data()
        srv_id = data.get("srv_id")
        await state.clear()
        if srv_id:
            s = get_srv(srv_id)
            if s:
                info   = get_sec_info(s['sec_id'])
                net_nm = info[1] if info else ""
                sec_nm = info[0] if info else ""
                desc   = s['info'] if s['info'] and s['info'] != "Yo'q" else "Yo'q 💬"
                b = InlineKeyboardBuilder()
                b.button(text="✅ Buyurtma berish", callback_data=f"BUY:{srv_id}")
                b.button(text="◀️ Orqaga",          callback_data=f"SRV_BACK:{s['sec_id']}")
                b.adjust(1)
                await msg.answer(
                    f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
                    f"💰 Narxi (1000x): {s['price']} So'm\n\n"
                    f"| {desc}\n\n"
                    f"⬇️ Minimal: {s['min_q']} ta\n"
                    f"⬆️ Maksimal: {s['max_q']} ta",
                    reply_markup=b.as_markup())
                return
        await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    try: qty = int(msg.text.strip())
    except:
        await msg.answer("❌ Noto'g'ri son kiriting!"); return
    data = await state.get_data()
    s    = get_srv(data["srv_id"])
    if qty < s['min_q'] or qty > s['max_q']:
        await msg.answer(f"❌ Miqdor {s['min_q']} dan {s['max_q']} gacha bo'lishi kerak!"); return

    price = int(qty * s['price'] / 1000)
    bal   = get_user(msg.from_user.id)['balance']

    if bal < price:
        # Balans yetarli emas → to'lov tizimlarini ko'rsat
        pays = db().execute("SELECT * FROM pay_methods").fetchall()
        b    = InlineKeyboardBuilder()
        for p in pays:
            b.button(text=p['name'], callback_data=f"PAYM_ORD:{p['id']}:{qty}:{data['srv_id']}")
        b.button(text="◀️ Orqaga", callback_data="PAY_ORD_BACK")
        b.adjust(1)
        await state.update_data(qty=qty, price=price)
        await msg.answer(
            "Quyidagilardan birini tanlang:",
            reply_markup=b.as_markup()); return

    await state.update_data(qty=qty, price=price)
    await msg.answer(
        "🔗 Buyurtma havolasini kiriting:\n\n"
        "❗ Namuna: https://havol & @havola",
        reply_markup=kb_back())
    await state.set_state(OrdS.link)

# ── To'lov (buyurtma uchun) ──────────────
@dp.callback_query(F.data == "PAY_ORD_BACK")
async def cb_pay_ord_back(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    s    = get_srv(data.get("srv_id"))
    if not s: await call.message.answer("Qayta boshlang."); return
    info   = get_sec_info(s['sec_id'])
    net_nm = info[1] if info else ""
    sec_nm = info[0] if info else ""
    await call.message.edit_text(
        f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
        f"📊 Buyurtma miqdorini kiriting:\n\n"
        f"⬇️ Minimal: {s['min_q']} ta\n"
        f"⬆️ Maksimal: {s['max_q']} ta")
    await state.set_state(OrdS.qty)

@dp.callback_query(F.data.startswith("PAYM_ORD:"))
async def cb_paym_ord(call: types.CallbackQuery, state: FSMContext):
    parts  = call.data.split(":")
    pid    = int(parts[1])
    qty    = int(parts[2])
    srv_id = int(parts[3])
    p      = db().execute("SELECT * FROM pay_methods WHERE id=?", (pid,)).fetchone()
    if not p: await call.answer("Topilmadi!"); return
    await state.update_data(pay_id=pid, pay_name=p['name'], pay_det=p['details'],
                             qty=qty, srv_id=srv_id, pay_for_order=True)
    min_d = gcfg("min_dep") or "1000"
    await call.message.edit_text(
        f"💰 To'lov miqdorini kiriting:\n\nMinimal: {min_d} So'm")
    await state.set_state(PayS.amount)

# ── Miqdor → rasm so'rash ────────────────
@dp.message(PayS.amount)
async def h_pay_amount(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    try: amt = int(msg.text.strip())
    except:
        await msg.answer("❌ Noto'g'ri miqdor!"); return
    min_d = int(gcfg("min_dep") or 1000)
    if amt < min_d:
        await msg.answer(
            "❌ To'lov qilishda xatolik yuz berdi.\n"
            "Iltimos, qayta urinib ko'ring."); return
    await state.update_data(pay_amount=amt)
    await msg.answer("📝 To'lov chekini rasmga olib yuboring", reply_markup=kb_back())
    await state.set_state(PayS.screenshot)

# ── Rasm → admin ga yuborish ─────────────
@dp.message(PayS.screenshot)
async def h_pay_screenshot(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    data  = await state.get_data()
    uid   = msg.from_user.id
    amt   = data.get("pay_amount", 0)
    pname = data.get("pay_name", "")

    await msg.answer(
        "⏳ Qabul qilindi!\n\n"
        "To'lovingiz 5 daqiqadan 24 soatgacha bo'lgan vaqt ichida amalga oshiriladi!",
        reply_markup=kb_main(uid in ADMIN_IDS))

    for aid in ADMIN_IDS:
        try:
            b = InlineKeyboardBuilder()
            b.button(text="✅", callback_data=f"APOK:{uid}:{amt}:{data.get('srv_id',0)}:{data.get('qty',0)}")
            b.button(text="❌", callback_data=f"APNO:{uid}")
            b.adjust(2)
            caption = (
                f"Foydalanuvchi hisobini to'ldirmoqchi!\n\n"
                f"💳 To'lov tizimi: {pname}\n"
                f"👤 Foydalanuvchi: {uid}\n"
                f"💰 To'lov miqdori: {amt:,} So'm\n\n"
                f"⏰ Sana: {__import__('datetime').datetime.now().strftime('%Y.%m.%d %H:%M')}"
            )
            if msg.photo:
                await bot.send_photo(aid, msg.photo[-1].file_id,
                                     caption=caption, reply_markup=b.as_markup())
            elif msg.document:
                await bot.send_document(aid, msg.document.file_id,
                                        caption=caption, reply_markup=b.as_markup())
            else:
                await bot.send_message(aid,
                    f"💳 To'lov so'rovi!\n\n"
                    f"💳 To'lov tizimi: {pname}\n"
                    f"👤 Foydalanuvchi: {uid}\n"
                    f"💰 To'lov miqdori: {amt:,} So'm",
                    reply_markup=b.as_markup())
        except: pass
    await state.clear()

# Admin: ✅ tasdiqlash
@dp.callback_query(F.data.startswith("APOK:"))
async def cb_apok(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    parts  = call.data.split(":")
    uid    = int(parts[1]); amt = int(parts[2])
    srv_id = int(parts[3]); qty = int(parts[4])
    c = db()
    c.execute("UPDATE users SET balance=balance+?,deposited=deposited+? WHERE id=?", (amt, amt, uid))
    c.commit(); c.close()
    await call.message.edit_caption(
        caption=f"✅ {uid} ga {amt:,} So'm qo'shildi!") if call.message.caption else \
        await call.message.edit_text(f"✅ {uid} ga {amt:,} So'm qo'shildi!")
    try:
        await bot.send_message(uid,
            f"✅ To'lovingiz tastiqlandi!\n\n"
            f"Hisobingiz {amt:,} So'm ga to'ldirildi.")
        # Agar buyurtma uchun to'langan bo'lsa — havola so'ra
        if srv_id and qty:
            s    = get_srv(srv_id)
            info = get_sec_info(s['sec_id']) if s else None
            net_nm = info[1] if info else ""
            sec_nm = info[0] if info else ""
            # state'ni o'rnatib bo'lmaydi (boshqa user konteksti)
            # Shuning uchun foydalanuvchiga xabar yuboramiz, u "Buyurtma berish" bosganda davom etadi
    except: pass

# Admin: ❌ rad etish
@dp.callback_query(F.data.startswith("APNO:"))
async def cb_apno(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[5:])
    await call.message.edit_caption(caption=f"❌ {uid} rad etildi.") if call.message.caption else \
        await call.message.edit_text(f"❌ {uid} rad etildi.")
    try: await bot.send_message(uid, "❌ To'lovingiz rad etildi.")
    except: pass

# ── Havola kiritish ──────────────────────
@dp.message(OrdS.link)
async def h_link(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    link = msg.text.strip()
    data = await state.get_data()
    s    = get_srv(data["srv_id"])
    info = get_sec_info(s['sec_id'])
    net_nm = info[1] if info else ""
    sec_nm = info[0] if info else ""
    price  = data["price"]
    qty    = data["qty"]
    await state.update_data(link=link)

    # Videoda: tasdiqlash sahifasi
    b = InlineKeyboardBuilder()
    b.button(text="✅ Tasdiqlash", callback_data="ORD_CONFIRM")
    await msg.answer(
        f"ℹ️ Buyurtmam haqida malumot:\n\n"
        f"{net_nm} - 👤 {sec_nm} [ ⚡-Tezkor ]\n\n"
        f"💰 Narxi: {price} So'm\n"
        f"🔗 Havola: {link}\n"
        f"📊 Miqdor: {qty} ta\n\n"
        f"⚠️ Malumotlar to'g'ri bo'lsa (✅ Tasdiqlash) tugmasini bosing, "
        f"hisobingizdan {price} So'm yechib olinadi va buyurtma qabul qilinadi, "
        f"buyurtmani bekor qilish imkoni yo'q.",
        reply_markup=b.as_markup())
    await state.set_state(OrdS.confirm)

# ── Tasdiqlash ───────────────────────────
@dp.callback_query(F.data == "ORD_CONFIRM", OrdS.confirm)
async def cb_ord_confirm(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    uid  = call.from_user.id
    u    = get_user(uid)
    if u['balance'] < data["price"]:
        await call.answer("❌ Balans yetarli emas!", show_alert=True); return
    oid = create_order(uid, data["srv_id"], data["link"], data["qty"], data["price"])
    await state.clear()
    await call.message.edit_text(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"🆔 Buyurtma ID si: {oid}")
    await call.message.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(uid in ADMIN_IDS))
    for aid in ADMIN_IDS:
        try:
            o = get_order_detail(oid)
            await bot.send_message(aid,
                f"🆕 Yangi buyurtma!\n"
                f"🆔 ID: {oid} | 👤 {uid}\n"
                f"🌐 {o['net_name']} - {o['sec_name']}\n"
                f"🔗 {data['link']}\n"
                f"📊 {data['qty']} ta | 💰 {data['price']} So'm")
        except: pass


# ══════════════════════════════════════════
#  BUYURTMALAR (foydalanuvchi)
#  Videoda:
#  "📊 Buyurtmalar:
#   🆔 ID: 1
#   🗂 Xizmat: 👤 Obunachi [ ⚡-Tezkor ]
#   ♻️ Holat: ⏳ Bajarilmoqda
#   📅 Sana: 2026-03-06 09:13:55
#   ────────────────────────"
#  [1] tugmasi
#  [◀◀] [1/1] [▶▶]
#  [🔍 Qidirish]
# ══════════════════════════════════════════
STATUS_EMOJI = {"Bajarildi":"✅","Bekor qilindi":"❌","Jarayonda":"⏳","Bajarilmoqda":"⏳"}

def ord_list_text(o):
    se = STATUS_EMOJI.get(o[5], "❓")
    return (
        f"📊 Buyurtmalar:\n\n"
        f"🆔 ID: {o[0]}\n"
        f"🗂 Xizmat: 👤 {o[2]} [ ⚡-Tezkor ]\n"
        f"♻️ Holat: {se} {o[5]}\n"
        f"📅 Sana: {o[7][:19]}\n"
        f"{'─'*24}"
    )

def ord_detail_text(o):
    se = STATUS_EMOJI.get(o[5], "❓")
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
    b.button(text=str(ords[idx][0]), callback_data=f"ODET:{idx}:{uid}")
    b.adjust(1)
    if total > 1:
        prev = (idx - 1) % total
        nxt  = (idx + 1) % total
        b.button(text="⏪",            callback_data=f"OPG:{prev}:{uid}")
        b.button(text=f"{idx+1}/{total}", callback_data="NOP")
        b.button(text="⏩",            callback_data=f"OPG:{nxt}:{uid}")
        b.adjust(1, 3)
    b.button(text="🔍 Qidirish", callback_data=f"OSRCH:{uid}")
    return b.as_markup()

@dp.message(F.text == "Buyurtmalar")
async def h_buyurtmalar(msg: types.Message):
    ords = get_user_orders(msg.from_user.id)
    if not ords:
        await msg.answer("📦 Sizda hali buyurtmalar yo'q."); return
    await msg.answer(ord_list_text(ords[0]),
                     reply_markup=kb_ord_list(ords, 0, msg.from_user.id))

@dp.callback_query(F.data.startswith("OPG:"))
async def cb_opg(call: types.CallbackQuery):
    _, idx_s, uid_s = call.data.split(":")
    ords = get_user_orders(int(uid_s))
    idx  = int(idx_s) % len(ords)
    await call.message.edit_text(ord_list_text(ords[idx]),
                                  reply_markup=kb_ord_list(ords, idx, int(uid_s)))

@dp.callback_query(F.data.startswith("ODET:"))
async def cb_odet(call: types.CallbackQuery):
    _, idx_s, uid_s = call.data.split(":")
    ords = get_user_orders(int(uid_s))
    idx  = int(idx_s) % len(ords)
    o    = ords[idx]
    b    = InlineKeyboardBuilder()
    b.button(text="◀️ Orqaga", callback_data=f"OPG:{idx}:{uid_s}")
    await call.message.edit_text(ord_detail_text(o), reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("OSRCH:"))
async def cb_osrch(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(srch_uid=int(call.data[6:]))
    await call.message.answer("🔍 Buyurtma ID raqamini kiriting:")
    await state.set_state(AdmS.ord_srch)

@dp.callback_query(F.data == "NOP")
async def cb_nop(call: types.CallbackQuery): await call.answer()


# ══════════════════════════════════════════
#  HISOBIM
# ══════════════════════════════════════════
@dp.message(F.text == "Hisobim")
async def h_hisobim(msg: types.Message):
    uid = msg.from_user.id; u = get_user(uid)
    if not u: return
    b = InlineKeyboardBuilder()
    b.button(text="Hisobni to'ldirish", callback_data="GO_TOPUP")
    await msg.answer(
        f"👤 Sizning ID raqamingiz: {uid}\n\n"
        f"💰 Balansingiz: {u['balance']} So'm\n"
        f"📦 Buyurtmalaringiz: {count_orders(uid)} ta\n"
        f"👥 Referallaringiz: {count_refs(uid)} ta\n"
        f"💵 Kiritgan pullaringiz: {u['deposited']} So'm",
        reply_markup=b.as_markup())


# ══════════════════════════════════════════
#  HISOB TO'LDIRISH
# ══════════════════════════════════════════
@dp.message(F.text == "Hisob to'ldirish")
async def h_topup(msg: types.Message, state: FSMContext):
    await _show_pay_methods(msg, state)

@dp.callback_query(F.data == "GO_TOPUP")
async def cb_go_topup(call: types.CallbackQuery, state: FSMContext):
    await _show_pay_methods(call.message, state)

async def _show_pay_methods(msg, state):
    pays = db().execute("SELECT * FROM pay_methods").fetchall()
    if not pays:
        await msg.answer("💳 To'lov tizimi hali sozlanmagan."); return
    b = InlineKeyboardBuilder()
    for p in pays:
        b.button(text=p['name'], callback_data=f"PAYM:{p['id']}")
    b.button(text="◀️ Orqaga", callback_data="PAYM_BACK")
    b.adjust(1)
    await msg.answer("To'lov tizimini tanlang:", reply_markup=b.as_markup())
    await state.set_state(PayS.choose)

@dp.callback_query(F.data.startswith("PAYM:"), PayS.choose)
async def cb_paym(call: types.CallbackQuery, state: FSMContext):
    pid = int(call.data[5:])
    p   = db().execute("SELECT * FROM pay_methods WHERE id=?", (pid,)).fetchone()
    if not p: await call.answer("Topilmadi!"); return
    await state.update_data(pay_id=pid, pay_name=p['name'], pay_det=p['details'], pay_for_order=False)
    min_d = gcfg("min_dep") or "1000"
    await call.message.edit_text(
        f"💰 To'lov miqdorini kiriting:\n\nMinimal: {min_d} So'm")
    await state.set_state(PayS.amount)

@dp.callback_query(F.data == "PAYM_BACK")
async def cb_paym_back(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Bekor qilindi.")


# ══════════════════════════════════════════
#  PUL ISHLASH
# ══════════════════════════════════════════
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
        f"👥 Referallaringiz: {count_refs(uid)} ta",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "EARN_BACK")
async def cb_earn_back(call: types.CallbackQuery):
    await call.message.delete()


# ══════════════════════════════════════════
#  MUROJAAT
# ══════════════════════════════════════════
@dp.message(F.text == "Murojaat")
async def h_murojaat(msg: types.Message, state: FSMContext):
    await msg.answer("📝 Murojaat matnini yozib yuboring.", reply_markup=kb_back())
    await state.set_state(SuppS.msg)

@dp.message(SuppS.msg)
async def h_supp_msg(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    await state.clear()
    uid = msg.from_user.id
    await msg.answer(
        "⏳ Murojaatingiz qabul qilindi!\n\n"
        "Tez orada murojaatingizni ko'rib chiqamiz.",
        reply_markup=kb_main(uid in ADMIN_IDS))
    for aid in ADMIN_IDS:
        try:
            b = InlineKeyboardBuilder()
            b.button(text="📝 Javob yozish", callback_data=f"REP:{uid}")
            await bot.send_message(aid,
                f"📩 Yangi murojaat!\n"
                f"👤 {msg.from_user.full_name} (ID: {uid})\n\n"
                f"{msg.text}", reply_markup=b.as_markup())
        except: pass

@dp.callback_query(F.data.startswith("REP:"))
async def cb_rep(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[4:])
    await state.update_data(rep_target=uid)
    await call.message.answer(
        f"{uid} Foydalanuvchiga yuboriladigan xabaringizni kiriting.",
        reply_markup=kb_back())
    await state.set_state(AdmS.rep_msg)

@dp.message(AdmS.rep_msg)
async def adm_rep_msg(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin()); return
    uid = (await state.get_data())["rep_target"]; await state.clear()
    try:
        await bot.send_message(uid, f"📩 Admin javobi:\n\n{msg.text}")
        await msg.answer("✅ Xabar foydalanuvchiga yuborildi!", reply_markup=kb_admin())
    except:
        await msg.answer("❌ Yuborib bo'lmadi.", reply_markup=kb_admin())


# ══════════════════════════════════════════
#  QO'LLANMA
# ══════════════════════════════════════════
@dp.message(F.text == "Qo'llanma")
async def h_faq(msg: types.Message):
    faqs = db().execute("SELECT * FROM faqs").fetchall()
    if not faqs:
        await msg.answer("Hozircha qo'llanmalar yo'q."); return
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f['q'][:35], callback_data=f"FAQ:{f['id']}")
    b.adjust(1)
    await msg.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("FAQ:"))
async def cb_faq(call: types.CallbackQuery):
    fid = int(call.data[4:])
    f   = db().execute("SELECT * FROM faqs WHERE id=?", (fid,)).fetchone()
    if f: await call.message.answer(f"❓ {f['q']}\n\n💬 {f['a']}")


# ══════════════════════════════════════════
#  ORQAGA
# ══════════════════════════════════════════
@dp.message(F.text == "◀️ Orqaga")
async def h_back(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS))

@dp.message(F.text == "Orqaga")
async def h_back_simple(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("🖥 Asosiy menyudasiz!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS))


# ══════════════════════════════════════════
#  ADMIN PANEL
# ══════════════════════════════════════════
@dp.message(F.text == "🖥 Boshqaruv")
async def h_boshqaruv(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin())

# ── Asosiy sozlamalar ──────────────────
@dp.message(F.text == "⚙️ Asosiy sozlamalar")
async def h_asosiy(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    ref  = gcfg("ref_bonus")
    cur  = gcfg("currency")
    svc  = "✅ Faol" if gcfg("service_active") == "1" else "❌ Nofaol"
    prem = "✅ Faol" if gcfg("premium_emoji")  == "1" else "❌ Nofaol"
    b = InlineKeyboardBuilder()
    b.button(text="💵 Referal o'zgartirish",   callback_data="CFG:ref_bonus")
    b.button(text="💱 Valyuta o'zgartirish",   callback_data="CFG:currency")
    b.button(text=f"⏱ Xizmat vaqti: {svc}",   callback_data="CFG:svc_tog")
    b.button(text=f"✨ Premium emoji: {prem}", callback_data="CFG:prem_tog")
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
    if key == "svc_tog":
        scfg("service_active", "0" if gcfg("service_active") == "1" else "1")
        await call.answer("✅ O'zgartirildi!", show_alert=True); return
    if key == "prem_tog":
        scfg("premium_emoji", "0" if gcfg("premium_emoji") == "1" else "1")
        await call.answer("✅ O'zgartirildi!", show_alert=True); return
    labels = {"ref_bonus": "Yangi referal bonus miqdorini kiriting (So'mda):",
              "currency":  "Yangi valyuta nomini kiriting (masalan: So'm):"}
    await state.update_data(cfg_key=key)
    await call.message.answer(labels.get(key, "Yangi qiymat kiriting:"), reply_markup=kb_back())
    await state.set_state(AdmS.cfg_val)

@dp.message(AdmS.cfg_val)
async def adm_cfg_val(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("⚙️", reply_markup=kb_admin()); return
    key = (await state.get_data())["cfg_key"]; await state.clear()
    scfg(key, msg.text.strip())
    await msg.answer("✅ Saqlandi!", reply_markup=kb_admin())

# ── Statistika ─────────────────────────
@dp.message(F.text == "📊 Statistika")
async def h_stats(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    tot,act,n24,n7,n30,a24,a7,a30,pay,mon,ords,done,canc,proc = get_stats()
    binfo = await bot.get_me()
    b = InlineKeyboardBuilder()
    b.button(text="💰 TOP-50 Balans",  callback_data="T50:bal")
    b.button(text="👥 TOP-50 Referal", callback_data="T50:ref")
    b.adjust(2)
    await msg.answer(
        f"📊 Statistika\n"
        f"• Obunachilar soni: {tot} ta\n"
        f"• Faol obunachilar: {act} ta\n"
        f"• Tark etganlar: {tot - act} ta\n\n"
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
        f"• Jami pullar: {mon:,} So'm\n\n"
        f"🤖 @{binfo.username}",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "T50:bal")
async def cb_t50b(call: types.CallbackQuery):
    rows = db().execute("SELECT id,name,balance FROM users ORDER BY balance DESC LIMIT 50").fetchall()
    t = "💰 TOP-50 Balans:\n\n"
    for i, r in enumerate(rows, 1): t += f"{i}. {r['name'] or r['id']} — {r['balance']:,} So'm\n"
    await call.message.answer(t[:4096])

@dp.callback_query(F.data == "T50:ref")
async def cb_t50r(call: types.CallbackQuery):
    rows = db().execute(
        "SELECT u.id,u.name,COUNT(r.id) rc FROM users u "
        "LEFT JOIN users r ON r.ref_id=u.id GROUP BY u.id ORDER BY rc DESC LIMIT 50"
    ).fetchall()
    t = "👥 TOP-50 Referal:\n\n"
    for i, r in enumerate(rows, 1): t += f"{i}. {r['name'] or r['id']} — {r['rc']} ta\n"
    await call.message.answer(t[:4096])

# ── Xabar yuborish ─────────────────────
@dp.message(F.text == "📨 Xabar yuborish")
async def h_bc(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="💬 Oddiy",   callback_data="BC:n")
    b.button(text="📤 Forward", callback_data="BC:f")
    b.adjust(2)
    await msg.answer("Foydalanuvchilarga yuboradigan xabar turini tanlang.", reply_markup=b.as_markup())
    await state.set_state(AdmS.bc_type)

@dp.callback_query(F.data.startswith("BC:"), AdmS.bc_type)
async def cb_bc(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(bc_type=call.data[3:])
    await call.message.answer("Xabarni yozing yoki yuboring:", reply_markup=kb_back())
    await state.set_state(AdmS.bc_msg)

@dp.message(AdmS.bc_msg)
async def adm_bc(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    uids = get_all_uids(); ok = fail = 0
    for uid in uids:
        try:
            if data["bc_type"] == "f": await msg.forward(uid)
            else: await bot.send_message(uid, msg.text or "")
            ok += 1; await asyncio.sleep(0.03)
        except: fail += 1
    await msg.answer(f"✅ Yuborildi: {ok}\n❌ Xato: {fail}", reply_markup=kb_admin())

# ── Majbur obuna kanallar ──────────────
@dp.message(F.text == "🔐 Majbur obuna kanallar")
async def h_chans(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="+ Kanal qo'shish",     callback_data="CH:add")
    b.button(text="📋 Ro'yxatni ko'rish", callback_data="CH:list")
    b.button(text="🗑 Kanalni o'chirish",  callback_data="CH:del")
    b.adjust(1)
    await msg.answer("🔐 Majbur obuna kanallar:", reply_markup=b.as_markup())

@dp.callback_query(F.data == "CH:add")
async def cb_ch_add(call: types.CallbackQuery, state: FSMContext):
    b = InlineKeyboardBuilder()
    b.button(text="📢 Ommaviy / Shaxsiy (Kanal · Guruh)", callback_data="CHTYPE:public")
    b.button(text="🔐 Shaxsiy / So'rovli havola",          callback_data="CHTYPE:private")
    b.button(text="🌐 Oddiy havola",                        callback_data="CHTYPE:link")
    b.button(text="◀️ Orqaga",                             callback_data="CHTYPE:back")
    b.adjust(1)
    text = (
        "⚙️ <b>Majburiy obuna turini tanlang:</b>\n\n"
        "Quyida majburiy obunani qo'shishning 3 ta turi mavjud:\n\n"
        "<blockquote>"
        "💠 <b>Ommaviy / Shaxsiy (Kanal · Guruh)</b>\n"
        "Har qanday kanal yoki guruhni (ommaviy yoki shaxsiy) majburiy obunaga ulash.\n\n"
        "💠 <b>Shaxsiy / So'rovli havola</b>\n"
        "Shaxsiy yoki so'rovli kanal/guruh havolasi orqali o'tganlarni kuzatish.\n\n"
        "💠 🌐 <b>Oddiy havola</b>\n"
        "Majburiy tekshiruvsiz oddiy havolani ko'rsatish (Instagram, sayt va boshqalar)."
        "</blockquote>"
    )
    await call.message.edit_text(text, reply_markup=b.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("CHTYPE:"))
async def cb_chtype(call: types.CallbackQuery, state: FSMContext):
    t = call.data[7:]
    if t == "back":
        b = InlineKeyboardBuilder()
        b.button(text="+ Kanal qo'shish",     callback_data="CH:add")
        b.button(text="📋 Ro'yxatni ko'rish", callback_data="CH:list")
        b.button(text="🗑 Kanalni o'chirish",  callback_data="CH:del")
        b.adjust(1)
        await call.message.edit_text("🔐 Majbur obuna kanallar:", reply_markup=b.as_markup())
        return
    await state.update_data(ch_type=t)
    if t == "link":
        # Oddiy havola — faqat nomi va URL
        await call.message.answer(
            "🌐 Havola nomini kiriting (masalan: Instagram sahifam):",
            reply_markup=kb_back())
        await state.set_state(AdmS.ch_title)
    elif t == "private":
        await call.message.answer(
            "🔐 Kanal/guruh nomini kiriting (masalan: Mening kanalim):",
            reply_markup=kb_back())
        await state.set_state(AdmS.ch_title)
    else:
        # Ommaviy
        await call.message.answer(
            "📢 Kanal ID'sini kiriting (@kanal yoki -100...):",
            reply_markup=kb_back())
        await state.set_state(AdmS.ch_cid)

@dp.message(AdmS.ch_cid)
async def adm_ch_cid(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(ch_cid=msg.text.strip())
    await msg.answer("Kanal nomini kiriting:")
    await state.set_state(AdmS.ch_title)

@dp.message(AdmS.ch_title)
async def adm_ch_title(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data()
    ch_type = data.get("ch_type", "public")
    await state.update_data(ch_title=msg.text.strip())
    if ch_type == "link":
        await msg.answer("🌐 Havolani kiriting (https://...):")
        await state.set_state(AdmS.ch_url)
    elif ch_type == "private":
        await msg.answer("🔐 Kanal/guruh havolasini kiriting (https://t.me/+...):")
        await state.set_state(AdmS.ch_url)
    else:
        await msg.answer("📢 Kanal havolasini kiriting (https://t.me/...):")
        await state.set_state(AdmS.ch_url)

@dp.message(AdmS.ch_url)
async def adm_ch_url(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    ch_type = data.get("ch_type", "public")
    c = db()
    if ch_type == "link":
        # Oddiy havola: cid = "link", tekshirish yo'q
        c.execute("INSERT INTO channels(cid,title,url) VALUES(?,?,?)",
                  ("link", data["ch_title"], msg.text.strip()))
    elif ch_type == "private":
        # Shaxsiy: cid = "private"
        c.execute("INSERT INTO channels(cid,title,url) VALUES(?,?,?)",
                  ("private", data.get("ch_title", "Kanal"), msg.text.strip()))
    else:
        c.execute("INSERT INTO channels(cid,title,url) VALUES(?,?,?)",
                  (data.get("ch_cid",""), data["ch_title"], msg.text.strip()))
    c.commit(); c.close()
    await msg.answer(f"✅ {data.get('ch_title','Kanal')} qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data == "CH:list")
async def cb_ch_list(call: types.CallbackQuery):
    chans = db().execute("SELECT * FROM channels").fetchall()
    if not chans: await call.answer("Kanallar yo'q!", show_alert=True); return
    t = "📋 Kanallar:\n\n"
    for ch in chans: t += f"• {ch['title']} | {ch['cid']}\n"
    await call.message.answer(t)

@dp.callback_query(F.data == "CH:del")
async def cb_ch_del(call: types.CallbackQuery):
    chans = db().execute("SELECT * FROM channels").fetchall()
    if not chans: await call.answer("Kanallar yo'q!", show_alert=True); return
    b = InlineKeyboardBuilder()
    for ch in chans:
        b.button(text=f"🗑 {ch['title']}", callback_data=f"CHDEL:{ch['id']}")
    b.adjust(1)
    await call.message.answer("Qaysi kanalni o'chirmoqchisiz?", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("CHDEL:"))
async def cb_chdel(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    cid = int(call.data[6:])
    c = db(); c.execute("DELETE FROM channels WHERE id=?", (cid,)); c.commit(); c.close()
    await call.message.edit_text("✅ Kanal o'chirildi!")

# ── To'lov tizimlar ────────────────────
@dp.message(F.text == "💳 To'lov tizimlar")
async def h_pays(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    pays = db().execute("SELECT * FROM pay_methods").fetchall()
    b = InlineKeyboardBuilder()
    for p in pays:
        b.button(text=p['name'], callback_data=f"PDEL:{p['id']}")
    b.button(text="+ To'lov tizimi qo'shish", callback_data="PADD")
    b.button(text="◀️ Orqaga",                callback_data="ADM_BACK")
    b.adjust(1)

    # Videoda ko'rindi: "⚙️ Avto To'lov Sozlamalari" ham bor
    c = db()
    api_key = gcfg("api_key")
    avto_holat = "✅ Yoqilgan" if api_key else "❌ O'chirilgan"

    await msg.answer(
        f"⚙️ Avto To'lov Sozlamalari\n\n"
        f"🔑 API Kalit: {'✅ Kiritilgan' if api_key else '❌ Kiritilmagan'}\n"
        f"⚡ Avto to'lov holati: {avto_holat}\n\n"
        f"💳 To'lov tizimlari: {len(pays)} ta",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "PADD")
async def cb_padd(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("To'lov tizimi nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.pay_name)

@dp.message(AdmS.pay_name)
async def adm_pay_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(pay_name=msg.text.strip())
    await msg.answer("To'lov ma'lumotlarini kiriting (karta raqami va boshqalar):")
    await state.set_state(AdmS.pay_det)

@dp.message(AdmS.pay_det)
async def adm_pay_det(msg: types.Message, state: FSMContext):
    data = await state.get_data(); await state.clear()
    c = db()
    c.execute("INSERT INTO pay_methods(name,details) VALUES(?,?)",
              (data["pay_name"], msg.text.strip()))
    c.commit(); c.close()
    await msg.answer(f"✅ {data['pay_name']} to'lov tizimi qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("PDEL:"))
async def cb_pdel(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    pid = int(call.data[5:])
    c = db(); c.execute("DELETE FROM pay_methods WHERE id=?", (pid,)); c.commit(); c.close()
    await call.message.edit_text("✅ To'lov tizimi o'chirildi!")

@dp.callback_query(F.data == "ADM_BACK")
async def cb_adm_back(call: types.CallbackQuery):
    await call.message.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin())

# ── API ─────────────────────────────────
def get_apis():
    c = db(); r = c.execute("SELECT * FROM apis").fetchall(); c.close(); return r

def get_api(aid):
    c = db(); r = c.execute("SELECT * FROM apis WHERE id=?", (aid,)).fetchone(); c.close(); return r

@dp.message(F.text == "🔑 API")
async def h_api(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    apis = get_apis()
    b = InlineKeyboardBuilder()
    for i, a in enumerate(apis, 1):
        domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
        b.button(text=f"{i}", callback_data=f"APIVIEW:{a['id']}")
    b.button(text="+ API qo'shish", callback_data="API_ADD")
    b.adjust(len(apis) if apis else 1, 1)
    txt = f"🔑 API'lar ro'yhati: {len(apis)} ta\n\n"
    for i, a in enumerate(apis, 1):
        domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
        txt += f"{i}. {domain} - {a['price']} UZS\n"
    await msg.answer(txt, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("APIVIEW:"))
async def cb_apiview(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    aid = int(call.data[8:])
    a   = get_api(aid)
    if not a: await call.answer("Topilmadi!"); return
    domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Kalitni o'zgartish", callback_data=f"API_CHKEY:{aid}")
    b.button(text="◀️ Orqaga",             callback_data="API_LIST")
    b.button(text="🗑 O'chirish",           callback_data=f"API_DEL:{aid}")
    b.adjust(1, 2)
    await call.message.edit_text(
        f"⚙️ {domain} - {a['price']} UZS\n\n"
        f"🔗 Havola: {a['url']}\n"
        f"🔑 Kalit: <code>{a['key']}</code>",
        reply_markup=b.as_markup(),
        parse_mode="HTML")

@dp.callback_query(F.data == "API_LIST")
async def cb_api_list(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    apis = get_apis()
    b = InlineKeyboardBuilder()
    for i, a in enumerate(apis, 1):
        b.button(text=f"{i}", callback_data=f"APIVIEW:{a['id']}")
    b.button(text="+ API qo'shish", callback_data="API_ADD")
    b.adjust(len(apis) if apis else 1, 1)
    txt = f"🔑 API'lar ro'yhati: {len(apis)} ta\n\n"
    for i, a in enumerate(apis, 1):
        domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
        txt += f"{i}. {domain} - {a['price']} UZS\n"
    await call.message.edit_text(txt, reply_markup=b.as_markup())

@dp.callback_query(F.data == "API_ADD")
async def cb_api_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer(
        "🔗 API manzilini kiriting:\n\nNamuna: https://capitalsmmapi.uz/api/v2",
        reply_markup=kb_back())
    await state.set_state(AdmS.api_url)

@dp.message(AdmS.api_url)
async def adm_api_url(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(api_url=msg.text.strip())
    await msg.answer("🔑 API kalitini kiriting:")
    await state.set_state(AdmS.api_key)

@dp.message(AdmS.api_key)
async def adm_api_key(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(api_key=msg.text.strip())
    await msg.answer("💰 API narxini kiriting (UZS, masalan: 1430):")
    await state.set_state(AdmS.api_price)

@dp.message(AdmS.api_price)
async def adm_api_price(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: price = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri son!"); return
    data = await state.get_data(); await state.clear()
    c = db()
    c.execute("INSERT INTO apis(url,key,price) VALUES(?,?,?)",
              (data["api_url"], data["api_key"], price))
    c.commit(); c.close()
    domain = data["api_url"].replace("https://","").replace("http://","").split("/")[0]
    await msg.answer(f"✅ {domain} API muvaffaqiyatli qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("API_DEL:"))
async def cb_api_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    aid = int(call.data[8:])
    c = db(); c.execute("DELETE FROM apis WHERE id=?", (aid,)); c.commit(); c.close()
    await call.message.edit_text("✅ API muvaffaqiyatli o'chirildi!")

@dp.callback_query(F.data.startswith("API_CHKEY:"))
async def cb_api_chkey(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    aid = int(call.data[10:])
    await state.update_data(api_edit_id=aid)
    await call.message.answer("🔑 Yangi API kalitini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.api_new_key)

@dp.message(AdmS.api_new_key)
async def adm_api_new_key(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    aid  = data.get("api_edit_id")
    c = db(); c.execute("UPDATE apis SET key=? WHERE id=?", (msg.text.strip(), aid)); c.commit(); c.close()
    await msg.answer("✅ API kaliti o'zgartirildi!", reply_markup=kb_admin())

# ── Foydalanuvchini boshqarish ─────────
@dp.message(F.text == "👤 Foydalanuvchini boshqarish")
async def h_usr_mgmt(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("🆔 Foydalanuvchining ID raqamini yuboring:", reply_markup=kb_back())
    await state.set_state(AdmS.find_uid)

@dp.message(AdmS.find_uid)
async def adm_find_uid(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: uid = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri ID!"); return
    u = get_user(uid)
    if not u:
        await msg.answer("❌ Foydalanuvchi topilmadi!"); await state.clear(); return
    await state.clear()
    ban_txt = "🔔 Banlash" if not u['banned'] else "✅ Bandan chiqarish"
    b = InlineKeyboardBuilder()
    b.button(text=f"🔔 {ban_txt}", callback_data=f"UBAN:{uid}")
    b.button(text="+ Pul qo'shish", callback_data=f"UADD:{uid}")
    b.button(text="— Pul ayirish",  callback_data=f"UREM:{uid}")
    b.adjust(1, 2)
    await msg.answer(
        f"✅ Foydalanuvchi topildi!\n\n"
        f"🆔 ID raqami: {uid}\n"
        f"💰 Balansi: {u['balance']:,} So'm\n"
        f"📦 Buyurtmalari: {count_orders(uid)} ta\n"
        f"👥 Referallari: {count_refs(uid)} ta\n"
        f"💵 Kiritgan pullar: {u['deposited']:,} So'm",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("UBAN:"))
async def cb_uban(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[5:])
    c   = db()
    cur = c.execute("SELECT banned FROM users WHERE id=?", (uid,)).fetchone()[0]
    c.execute("UPDATE users SET banned=? WHERE id=?", (0 if cur else 1, uid))
    c.commit(); c.close()
    t = "✅ Ban olib tashlandi" if cur else "🔕 Banlandi"
    await call.message.edit_text(f"{t}: {uid}")

@dp.callback_query(F.data.startswith("UADD:"))
async def cb_uadd(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[5:])
    await state.update_data(target_uid=uid)
    await call.message.answer(f"({uid}) ning hisobiga qancha pul qo'shmoqchisiz?", reply_markup=kb_back())
    await state.set_state(AdmS.add_amt)

@dp.message(AdmS.add_amt)
async def adm_add_amt(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    uid = (await state.get_data())["target_uid"]; await state.clear()
    c = db()
    c.execute("UPDATE users SET balance=balance+?,deposited=deposited+? WHERE id=?", (amt, amt, uid))
    c.commit(); c.close()
    await msg.answer(f"Foydalanuvchi hisobiga {amt:,} So'm qo'shildi!", reply_markup=kb_admin())
    try: await bot.send_message(uid, f"💰 Hisobingizga {amt:,} So'm qo'shildi!")
    except: pass

@dp.callback_query(F.data.startswith("UREM:"))
async def cb_urem(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[5:])
    await state.update_data(target_uid=uid)
    await call.message.answer(f"({uid}) ning hisobidan qancha pul ayirmoqchisiz?", reply_markup=kb_back())
    await state.set_state(AdmS.rem_amt)

@dp.message(AdmS.rem_amt)
async def adm_rem_amt(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: amt = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    uid = (await state.get_data())["target_uid"]; await state.clear()
    c = db()
    c.execute("UPDATE users SET balance=balance-? WHERE id=?", (amt, uid))
    c.commit(); c.close()
    await msg.answer(f"({uid}) ning hisobidan {amt:,} So'm ayirildi!", reply_markup=kb_admin())

# ── Qo'llanmalar (admin) ───────────────
@dp.message(F.text == "📚 Qo'llanmalar")
async def h_adm_faq(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    faqs = db().execute("SELECT * FROM faqs").fetchall()
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f"🗑 {f['q'][:25]}", callback_data=f"FQDEL:{f['id']}")
    b.button(text="➕ Qo'llanma qo'shish", callback_data="FQADD")
    b.adjust(1)
    await msg.answer("📚 Qo'llanmalar ro'yhati:", reply_markup=b.as_markup())

@dp.callback_query(F.data == "FQADD")
async def cb_fqadd(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Qo'llanma nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.faq_q)

@dp.message(AdmS.faq_q)
async def adm_faq_q(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(faq_q=msg.text.strip())
    await msg.answer("Qo'llanma mazmunini kiriting:")
    await state.set_state(AdmS.faq_a)

@dp.message(AdmS.faq_a)
async def adm_faq_a(msg: types.Message, state: FSMContext):
    data = await state.get_data(); await state.clear()
    c = db()
    c.execute("INSERT INTO faqs(q,a) VALUES(?,?)", (data["faq_q"], msg.text.strip()))
    c.commit(); c.close()
    await msg.answer("✅ Qo'llanma qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("FQDEL:"))
async def cb_fqdel(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    fid = int(call.data[6:])
    c = db(); c.execute("DELETE FROM faqs WHERE id=?", (fid,)); c.commit(); c.close()
    await call.message.edit_text("✅ Qo'llanma muvaffaqiyatli o'chirildi!")

# ── Buyurtmalar (admin) ─────────────────
# Videoda:
# "📈 Buyurtmalar: 1 ta
#  ✅ Bajarilganlar: 0 ta
#  🚫 Bekor qilinganlar: 0 ta
#  ⏳ Bajarilayotganlar: 0 ta
#  🔄 Jarayondagilar: 1 ta
#  ♻️ Qayta ishlanganlar: 0 ta"
# [🔍 Qidirish]

@dp.message(F.text == "📈 Buyurtmalar")
async def h_adm_ords(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    c    = db()
    tot  = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    done = c.execute("SELECT COUNT(*) FROM orders WHERE status='Bajarildi'").fetchone()[0]
    canc = c.execute("SELECT COUNT(*) FROM orders WHERE status='Bekor qilindi'").fetchone()[0]
    proc = c.execute("SELECT COUNT(*) FROM orders WHERE status='Jarayonda'").fetchone()[0]
    c.close()
    b = InlineKeyboardBuilder()
    b.button(text="🔍 Qidirish", callback_data="ADSRCH")
    b.adjust(1)
    await msg.answer(
        f"📈 Buyurtmalar: {tot} ta\n\n"
        f"✅ Bajarilganlar: {done} ta\n"
        f"🚫 Bekor qilinganlar: {canc} ta\n"
        f"⏳ Bajarilayotganlar: 0 ta\n"
        f"🔄 Jarayondagilar: {proc} ta\n"
        f"♻️ Qayta ishlanganlar: 0 ta",
        reply_markup=b.as_markup())

@dp.callback_query(F.data == "ADSRCH")
async def cb_adsrch(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("🔍 Buyurtma ID raqamini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.ord_srch)

@dp.message(AdmS.ord_srch)
async def adm_ord_srch(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: oid = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri ID!"); return
    await state.clear()

    # Foydalanuvchi buyurtmasi
    c    = db()
    ords = get_user_orders(msg.from_user.id)
    # Avval user orders dan qidirish
    for o in ords:
        if o[0] == oid:
            b = InlineKeyboardBuilder()
            b.button(text="◀️ Orqaga", callback_data=f"OPG:0:{msg.from_user.id}")
            await msg.answer(ord_detail_text(o), reply_markup=b.as_markup())
            return

    # Admin uchun barcha orders
    if msg.from_user.id in ADMIN_IDS:
        o = get_order_detail(oid)
        if not o:
            await msg.answer("❌ Buyurtma topilmadi!"); return
        se = STATUS_EMOJI.get(o['status'], "❓")
        b = InlineKeyboardBuilder()
        b.button(text="✅ Bajarildi",    callback_data=f"ADONE:{oid}")
        b.button(text="❌ Bekor qilish", callback_data=f"ADCANC:{oid}")
        b.adjust(2)
        await msg.answer(
            f"🆔 Buyurtma IDsi: {oid}\n\n"
            f"{o['net_name']} - 👤 {o['sec_name']} [ ⚡-Tezkor ]\n\n"
            f"♻️ Holat: {se} {o['status']}\n"
            f"🔗 Havola: {o['link']}\n"
            f"📊 Miqdor: {o['qty']} ta\n"
            f"💰 Narxi: {o['price']:,} So'm\n"
            f"📅 Sana: {o['at'][:19]}",
            reply_markup=b.as_markup())
    else:
        await msg.answer("❌ Buyurtma topilmadi!")

@dp.callback_query(F.data.startswith("ADONE:"))
async def cb_adone(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[6:])
    c   = db()
    c.execute("UPDATE orders SET status='Bajarildi' WHERE id=?", (oid,))
    uid = c.execute("SELECT uid FROM orders WHERE id=?", (oid,)).fetchone()
    c.commit(); c.close()
    await call.message.edit_text(f"✅ Buyurtma #{oid} bajarildi!")
    if uid:
        try: await bot.send_message(uid[0], f"✅ #{oid} buyurtmangiz bajarildi!")
        except: pass

@dp.callback_query(F.data.startswith("ADCANC:"))
async def cb_adcanc(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[7:])
    c   = db()
    row = c.execute("SELECT uid,price FROM orders WHERE id=?", (oid,)).fetchone()
    if row:
        c.execute("UPDATE orders SET status='Bekor qilindi' WHERE id=?", (oid,))
        c.execute("UPDATE users SET balance=balance+? WHERE id=?", (row[0], row[1]))
        c.commit()
    c.close()
    await call.message.edit_text(f"❌ Buyurtma #{oid} bekor qilindi!")
    if row:
        try:
            await bot.send_message(row[0],
                f"❌ #{oid} buyurtmangiz bekor qilindi.\n💰 {row[1]:,} So'm qaytarildi.")
        except: pass

# ── Tarmoq/bo'lim qo'shish (admin) ─────
@dp.callback_query(F.data.startswith("SEC_ADD:"))
async def cb_sec_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    net_id = int(call.data[8:])
    await state.update_data(sec_net_id=net_id)
    await call.message.answer("📝 Yangi bo'lim nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.sec_name)

@dp.callback_query(F.data.startswith("SRV_ADD:"))
async def cb_srv_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    sec_id = int(call.data[8:])
    await state.update_data(srv_sec_id=sec_id)
    await call.message.answer("🆔 Xizmat IDsini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.srv_api)

@dp.message(AdmS.net_name)
async def adm_net_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin()); return
    name = msg.text.strip()
    c    = db(); c.execute("INSERT OR IGNORE INTO networks(name) VALUES(?)", (name,)); c.commit(); c.close()
    b    = InlineKeyboardBuilder()
    b.button(text="+ Yana qo'shish", callback_data="NET_MORE")
    b.button(text="◀️ Admin panel",  callback_data="ADM_BACK")
    b.adjust(1)
    await msg.answer(f"✅ {name} - ijtimoiy tarmoqi muvaffaqiyatli qo'shildi!",
                     reply_markup=b.as_markup())
    await state.clear()

@dp.callback_query(F.data == "NET_MORE")
async def cb_net_more(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📝 Yangi ijtimoiy tarmoq nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.net_name)

@dp.message(AdmS.sec_name)
async def adm_sec_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin()); return
    name   = msg.text.strip()
    data   = await state.get_data()
    net_id = data.get("sec_net_id") or data.get("net_id")
    c      = db(); c.execute("INSERT INTO sections(net_id,name) VALUES(?,?)", (net_id, name)); c.commit(); c.close()
    b      = InlineKeyboardBuilder()
    b.button(text="+ Yana bo'lim qo'shish", callback_data=f"SEC_MORE:{net_id}")
    b.button(text="◀️ Admin panel",          callback_data="ADM_BACK")
    b.adjust(1)
    await msg.answer(f"✅ {name} - bo'limi muvaffaqiyatli qo'shildi!", reply_markup=b.as_markup())
    await state.clear()

@dp.callback_query(F.data.startswith("SEC_MORE:"))
async def cb_sec_more(call: types.CallbackQuery, state: FSMContext):
    net_id = int(call.data[9:])
    await state.update_data(sec_net_id=net_id)
    await call.message.answer("📝 Yangi bo'lim nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.sec_name)

@dp.message(AdmS.srv_api)
async def adm_srv_api(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin()); return
    await state.update_data(srv_api=msg.text.strip())
    await msg.answer("💰 Xizmat narxini kiriting (1000 tasi uchun So'mda):")
    await state.set_state(AdmS.srv_price)

@dp.message(AdmS.srv_price)
async def adm_srv_price(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin()); return
    try: price = int(msg.text.strip())
    except: await msg.answer("❌ Noto'g'ri!"); return
    await state.update_data(srv_price=price)
    await msg.answer("📝 Xizmat haqida ma'lumot kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.srv_info)

@dp.message(AdmS.srv_info)
async def adm_srv_info(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("🖥 Admin paneliga xush kelibsiz!", reply_markup=kb_admin()); return
    data   = await state.get_data()
    sec_id = data.get("srv_sec_id")
    c      = db()
    c.execute("INSERT INTO services(sec_id,api_id,name,price,info) VALUES(?,?,?,?,?)",
              (sec_id, data["srv_api"], data["srv_api"], data["srv_price"], msg.text.strip()))
    c.commit(); c.close()
    b = InlineKeyboardBuilder()
    b.button(text="+ Yana xizmat qo'shish", callback_data=f"SRV_MORE:{sec_id}")
    b.button(text="◀️ Admin panel",          callback_data="ADM_BACK")
    b.adjust(1)
    await msg.answer(
        "✅ Xizmat muvaffaqiyatli qo'shildi!\n\n"
        "⬇️ Keyingi xizmatni qo'shish uchun.",
        reply_markup=b.as_markup())
    await state.clear()

@dp.callback_query(F.data.startswith("SRV_MORE:"))
async def cb_srv_more(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data[9:])
    await state.update_data(srv_sec_id=sec_id)
    await call.message.answer("🆔 Xizmat IDsini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.srv_api)

# Tarmoq va bo'lim o'chirish/tahrirlash
@dp.callback_query(F.data.startswith("NET_DEL:"))
async def cb_net_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    net_id = int(call.data[8:])
    c = db(); c.execute("DELETE FROM networks WHERE id=?", (net_id,)); c.commit(); c.close()
    await call.message.edit_text("✅ Tarmoq o'chirildi!")

@dp.callback_query(F.data.startswith("NET_EDIT:"))
async def cb_net_edit(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.answer("Tahrirlash hozircha mavjud emas.", show_alert=True)


# ══════════════════════════════════════════
#  START XABAR (admin)
# ══════════════════════════════════════════
@dp.message(F.text == "✉️ Start xabar")
async def h_start_msg(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    cur_text  = gcfg("start_text")  or "(belgilanmagan)"
    cur_photo = gcfg("start_photo") or "(yo'q)"
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Matnni o'zgartirish",  callback_data="STMSG:text")
    b.button(text="🖼 Rasm o'zgartirish",     callback_data="STMSG:photo")
    b.button(text="🗑 Rasmni o'chirish",      callback_data="STMSG:delpic")
    b.button(text="👁 Ko'rish",               callback_data="STMSG:preview")
    b.adjust(1)
    has_photo = "✅ Bor" if gcfg("start_photo") else "❌ Yo'q"
    await msg.answer(
        f"✉️ Start xabar sozlamalari:\n\n"
        f"📝 Hozirgi matn:\n{cur_text[:200]}\n\n"
        f"🖼 Rasm: {has_photo}",
        reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("STMSG:"))
async def cb_stmsg(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    action = call.data[6:]
    if action == "text":
        await call.message.answer(
            "✏️ Yangi start xabar matnini kiriting.\n\n"
            "HTML teglari ishlatiladi: <b>bold</b>, <i>italic</i>, <code>code</code>\n"
            "Iqtibos uchun: <blockquote>matn</blockquote>",
            reply_markup=kb_back(), parse_mode="HTML")
        await state.set_state(AdmS.start_msg)
    elif action == "photo":
        await call.message.answer(
            "🖼 Rasm yuboring (foto sifatida):",
            reply_markup=kb_back())
        await state.set_state(AdmS.start_photo_st)
    elif action == "delpic":
        scfg("start_photo", "")
        await call.answer("✅ Rasm o'chirildi!", show_alert=True)
    elif action == "preview":
        st = gcfg("start_text")  or "🖥 Asosiy menyudasiz!"
        sp = gcfg("start_photo") or ""
        if sp:
            try:
                await call.message.answer_photo(sp, caption=st, parse_mode="HTML")
                return
            except: pass
        await call.message.answer(st, parse_mode="HTML")

@dp.message(AdmS.start_msg)
async def adm_start_msg(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    # msg.html_text — aiogram avtomatik entities → HTML ga aylantiradi
    # (bold, italic, blockquote, code va h.k. saqlanadi)
    html_text = msg.html_text if msg.html_text else msg.text
    scfg("start_text", html_text.strip())
    await state.clear()
    # Ko'rinishini ko'rsatamiz
    try:
        await msg.answer(
            f"✅ Start xabar matni saqlandi!\n\n"
            f"👁 Ko'rinishi:\n\n{html_text.strip()}",
            parse_mode="HTML",
            reply_markup=kb_admin())
    except:
        await msg.answer("✅ Start xabar matni saqlandi!", reply_markup=kb_admin())

@dp.message(AdmS.start_photo_st)
async def adm_start_photo(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    if not msg.photo:
        await msg.answer("❌ Iltimos, rasm yuboring!"); return
    scfg("start_photo", msg.photo[-1].file_id)
    await state.clear()
    await msg.answer("✅ Rasm saqlandi!", reply_markup=kb_admin())


# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
async def main():
    init_db()
    logging.info("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
