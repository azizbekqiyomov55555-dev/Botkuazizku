"""
SMM Bot — To'liq kod
"""
import asyncio, logging, sqlite3, os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN", "TOKEN_BU_YERGA")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

def db():
    c = sqlite3.connect("bot.db")
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY, username TEXT DEFAULT '',
        name TEXT DEFAULT '', balance INTEGER DEFAULT 0,
        deposited INTEGER DEFAULT 0, ref_id INTEGER,
        banned INTEGER DEFAULT 0, joined TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS networks(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS sections(id INTEGER PRIMARY KEY AUTOINCREMENT, net_id INTEGER, name TEXT);
    CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY AUTOINCREMENT, sec_id INTEGER,
        api_id TEXT DEFAULT '', name TEXT DEFAULT '',
        price INTEGER DEFAULT 0, min_q INTEGER DEFAULT 10,
        max_q INTEGER DEFAULT 100000, info TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER,
        srv_id INTEGER, link TEXT, qty INTEGER, price INTEGER,
        status TEXT DEFAULT 'Jarayonda', at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cid TEXT, title TEXT, url TEXT, type TEXT DEFAULT 'public'
    );
    CREATE TABLE IF NOT EXISTS pay_methods(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, details TEXT);
    CREATE TABLE IF NOT EXISTS cfg(k TEXT PRIMARY KEY, v TEXT);
    CREATE TABLE IF NOT EXISTS apis(id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, key TEXT, price INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS faqs(id INTEGER PRIMARY KEY AUTOINCREMENT, q TEXT, a TEXT);
    INSERT OR IGNORE INTO cfg VALUES('ref_bonus','500');
    INSERT OR IGNORE INTO cfg VALUES('min_dep','1000');
    INSERT OR IGNORE INTO cfg VALUES('currency','Som');
    INSERT OR IGNORE INTO cfg VALUES('start_text','Botga xush kelibsiz!');
    INSERT OR IGNORE INTO cfg VALUES('start_photo','');
    """)
    c.commit(); c.close()

def gcfg(k):
    c = db(); r = c.execute("SELECT v FROM cfg WHERE k=?", (k,)).fetchone()
    c.close(); return r[0] if r else ""

def scfg(k, v):
    c = db(); c.execute("INSERT OR REPLACE INTO cfg VALUES(?,?)", (k, v))
    c.commit(); c.close()

def get_user(uid):
    c = db(); r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone(); c.close(); return r

def ensure_user(uid, username="", name="", ref_id=None):
    c = db()
    c.execute("INSERT OR IGNORE INTO users(id,username,name,ref_id) VALUES(?,?,?,?)", (uid, username, name, ref_id))
    c.commit(); c.close()

def get_nets():
    c = db(); r = c.execute("SELECT * FROM networks ORDER BY id").fetchall(); c.close(); return r

def get_secs(net_id):
    c = db(); r = c.execute("SELECT * FROM sections WHERE net_id=?", (net_id,)).fetchall(); c.close(); return r

def get_srvs(sec_id):
    c = db(); r = c.execute("SELECT * FROM services WHERE sec_id=?", (sec_id,)).fetchall(); c.close(); return r

def get_srv(sid):
    c = db(); r = c.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone(); c.close(); return r

def get_sec_info(sec_id):
    c = db()
    r = c.execute("SELECT s.name, n.name, n.id FROM sections s JOIN networks n ON s.net_id=n.id WHERE s.id=?", (sec_id,)).fetchone()
    c.close(); return r

def get_apis():
    c = db(); r = c.execute("SELECT * FROM apis").fetchall(); c.close(); return r

def get_channels():
    c = db(); r = c.execute("SELECT * FROM channels").fetchall(); c.close(); return r

def get_pays():
    c = db(); r = c.execute("SELECT * FROM pay_methods").fetchall(); c.close(); return r

def get_faqs():
    c = db(); r = c.execute("SELECT * FROM faqs").fetchall(); c.close(); return r

def create_order(uid, srv_id, link, qty, price):
    c = db()
    c.execute("INSERT INTO orders(uid,srv_id,link,qty,price) VALUES(?,?,?,?,?)", (uid, srv_id, link, qty, price))
    oid = c.lastrowid
    c.execute("UPDATE users SET balance=balance-? WHERE id=?", (price, uid))
    c.commit(); c.close(); return oid

NET_ICONS = {"Telegram":"✈️","Instagram":"📷","TikTok":"🎵","YouTube":"▶️","Facebook":"👥","Twitter":"🐦","VK":"💙"}

NET_KEYWORDS = {
    "Telegram":  ["telegram"],
    "Instagram": ["instagram"],
    "TikTok":    ["tiktok","tik tok","tik-tok"],
    "YouTube":   ["youtube","you tube"],
    "Facebook":  ["facebook"],
    "Twitter":   ["twitter"],
    "VK":        ["vkontakte"," vk "],
}

# ══════ STATES ══════
class OrdS(StatesGroup):
    qty     = State()
    link    = State()
    confirm = State()

class AdmS(StatesGroup):
    net_name      = State()
    sec_name      = State()
    srv_api       = State()
    srv_price     = State()
    srv_info      = State()
    ch_cid        = State()
    ch_title      = State()
    ch_url        = State()
    pay_name      = State()
    pay_det       = State()
    api_url       = State()
    api_key       = State()
    api_price     = State()
    api_new_key   = State()
    broadcast     = State()
    add_bal       = State()
    sub_bal       = State()
    add_bal_uid   = State()
    sub_bal_uid   = State()
    faq_q         = State()
    faq_a         = State()
    start_msg     = State()
    start_photo_st = State()
    net_edit      = State()
    sec_edit      = State()
    srv_edit_name = State()
    srv_edit_price= State()

# ══════ KEYBOARDS ══════
def kb_main(is_adm=False):
    b = ReplyKeyboardBuilder()
    b.button(text="🛍 Buyurtma berish")
    b.button(text="📋 Buyurtmalar")
    b.button(text="👤 Hisobim")
    b.button(text="💳 Hisob to'ldirish")
    b.button(text="💰 Pul ishlash")
    b.button(text="❓ Qo'llanma")
    b.button(text="📞 Murojaat")
    if is_adm:
        b.button(text="🖥 Boshqaruv")
    b.adjust(1, 2, 2, 2, 1)
    return b.as_markup(resize_keyboard=True)

def kb_back():
    b = ReplyKeyboardBuilder()
    b.button(text="Orqaga")
    return b.as_markup(resize_keyboard=True)

def kb_admin():
    b = ReplyKeyboardBuilder()
    b.button(text="📊 Statistika")
    b.button(text="👥 Foydalanuvchilar")
    b.button(text="🌐 Tarmoqlar")
    b.button(text="📢 Majburiy obuna")
    b.button(text="💳 To'lov tizimlari")
    b.button(text="🔑 API")
    b.button(text="📨 Xabar yuborish")
    b.button(text="❓ FAQ")
    b.button(text="✉️ Start xabar")
    b.button(text="◀️ Orqaga")
    b.adjust(2, 2, 2, 2, 1, 1)
    return b.as_markup(resize_keyboard=True)

# ══════ OBUNA TEKSHIRISH ══════
async def check_sub(uid):
    chans = get_channels()
    not_joined = []
    for ch in chans:
        if ch['type'] in ('link', 'private'):
            not_joined.append(ch); continue
        try:
            m = await bot.get_chat_member(ch['cid'], uid)
            if m.status in ("left", "kicked", "banned"):
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    real = [c for c in not_joined if c['type'] not in ('link', 'private')]
    return len(real) == 0, not_joined

def kb_sub(nj):
    b = InlineKeyboardBuilder()
    for ch in nj:
        b.button(text=f"📢 {ch['title']}", url=ch['url'])
    b.button(text="✅ Tekshirish", callback_data="chk_sub")
    b.adjust(1)
    return b.as_markup()

# ══════ API YUKLASH ══════
async def api_fetch_all():
    apis = get_apis()
    if not apis: return []
    api = apis[0]
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(api['url'], data={"key": api['key'], "action": "services"},
                              timeout=aiohttp.ClientTimeout(total=30)) as r:
                data = await r.json(content_type=None)
                return data if isinstance(data, list) else []
    except Exception as e:
        logging.error(f"API xato: {e}"); return []

async def sync_network_from_api(net_name):
    all_srvs = await api_fetch_all()
    if not all_srvs: return 0, 0
    keywords = NET_KEYWORDS.get(net_name, [net_name.lower()])
    cats = {}
    for s in all_srvs:
        cat = str(s.get("category", "Boshqa"))
        nm  = str(s.get("name", "")).lower()
        if any(kw in cat.lower() or kw in nm for kw in keywords):
            cats.setdefault(cat, []).append(s)
    if not cats: return 0, 0
    c = db()
    net = c.execute("SELECT id FROM networks WHERE name=?", (net_name,)).fetchone()
    if not net:
        c.execute("INSERT INTO networks(name) VALUES(?)", (net_name,)); net_id = c.lastrowid
    else:
        net_id = net[0]
    for sec in c.execute("SELECT id FROM sections WHERE net_id=?", (net_id,)).fetchall():
        c.execute("DELETE FROM services WHERE sec_id=?", (sec[0],))
    c.execute("DELETE FROM sections WHERE net_id=?", (net_id,))
    secs_n = srvs_n = 0
    for cat_name, srvs in cats.items():
        c.execute("INSERT INTO sections(net_id,name) VALUES(?,?)", (net_id, cat_name))
        sec_id = c.lastrowid; secs_n += 1
        for s in srvs:
            try: rate = float(s.get("rate", 0))
            except: rate = 0.0
            price = max(1, int(rate * 12700))
            try: min_q = int(float(s.get("min", 10)))
            except: min_q = 10
            try: max_q = int(float(s.get("max", 100000)))
            except: max_q = 100000
            c.execute("INSERT INTO services(sec_id,api_id,name,price,min_q,max_q,info) VALUES(?,?,?,?,?,?,?)",
                      (sec_id, str(s.get("service","")), str(s.get("name","")), price, min_q, max_q, str(s.get("type",""))))
            srvs_n += 1
    c.commit(); c.close()
    return secs_n, srvs_n

async def auto_load_all_networks():
    all_srvs = await api_fetch_all()
    if not all_srvs: return {}
    results = {}
    c = db()
    for net_name, keywords in NET_KEYWORDS.items():
        cats = {}
        for s in all_srvs:
            cat = str(s.get("category", "Boshqa"))
            nm  = str(s.get("name", "")).lower()
            if any(kw in cat.lower() or kw in nm for kw in keywords):
                cats.setdefault(cat, []).append(s)
        if not cats: continue
        net = c.execute("SELECT id FROM networks WHERE name=?", (net_name,)).fetchone()
        if not net:
            c.execute("INSERT INTO networks(name) VALUES(?)", (net_name,)); net_id = c.lastrowid
        else:
            net_id = net[0]
        for sec in c.execute("SELECT id FROM sections WHERE net_id=?", (net_id,)).fetchall():
            c.execute("DELETE FROM services WHERE sec_id=?", (sec[0],))
        c.execute("DELETE FROM sections WHERE net_id=?", (net_id,))
        secs_n = srvs_n = 0
        for cat_name, srvs in cats.items():
            c.execute("INSERT INTO sections(net_id,name) VALUES(?,?)", (net_id, cat_name))
            sec_id = c.lastrowid; secs_n += 1
            for s in srvs:
                try: rate = float(s.get("rate", 0))
                except: rate = 0.0
                price = max(1, int(rate * 12700))
                try: min_q = int(float(s.get("min", 10)))
                except: min_q = 10
                try: max_q = int(float(s.get("max", 100000)))
                except: max_q = 100000
                c.execute("INSERT INTO services(sec_id,api_id,name,price,min_q,max_q,info) VALUES(?,?,?,?,?,?,?)",
                          (sec_id, str(s.get("service","")), str(s.get("name","")), price, min_q, max_q, str(s.get("type",""))))
                srvs_n += 1
        c.commit()
        results[net_name] = (secs_n, srvs_n)
    c.close()
    return results

# ══════ /start ══════
@dp.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext):
    await state.clear()
    uid  = msg.from_user.id
    args = msg.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() and int(args[1]) != uid else None
    ensure_user(uid, msg.from_user.username or "", msg.from_user.full_name, ref_id)
    if ref_id:
        bonus = int(gcfg("ref_bonus") or 500)
        c = db()
        already = c.execute("SELECT ref_id FROM users WHERE id=?", (uid,)).fetchone()
        if already and already[0]:
            c.execute("UPDATE users SET balance=balance+? WHERE id=?", (bonus, ref_id))
            c.commit()
        c.close()
    ok, nj = await check_sub(uid)
    txt   = gcfg("start_text") or "Botga xush kelibsiz!"
    photo = gcfg("start_photo")
    if not ok:
        if photo:
            await msg.answer_photo(photo, caption=txt, parse_mode="HTML")
        else:
            await msg.answer(txt, parse_mode="HTML")
        await msg.answer("Quyidagi kanallarga obuna bo'ling:", reply_markup=kb_sub(nj)); return
    is_adm = uid in ADMIN_IDS
    if photo:
        await msg.answer_photo(photo, caption=txt, parse_mode="HTML", reply_markup=kb_main(is_adm))
    else:
        await msg.answer(txt, parse_mode="HTML", reply_markup=kb_main(is_adm))

@dp.callback_query(F.data == "chk_sub")
async def cb_chk_sub(call: types.CallbackQuery, state: FSMContext):
    ok, nj = await check_sub(call.from_user.id)
    if not ok:
        await call.answer("Hali obuna bo'lmadingiz!", show_alert=True); return
    await call.message.delete()
    is_adm = call.from_user.id in ADMIN_IDS
    txt = gcfg("start_text") or "Asosiy menyu"
    await call.message.answer(txt, parse_mode="HTML", reply_markup=kb_main(is_adm))

# ══════ ASOSIY MENU ══════
@dp.message(F.text == "◀️ Orqaga")
async def h_back_admin(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Asosiy menyu:", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS))

@dp.message(F.text == "Orqaga")
async def h_back(msg: types.Message, state: FSMContext):
    cur = await state.get_state()
    if cur:
        await state.clear()
        is_adm = msg.from_user.id in ADMIN_IDS
        if is_adm:
            await msg.answer("Admin panel:", reply_markup=kb_admin())
        else:
            await msg.answer("Asosiy menyu:", reply_markup=kb_main(False))
    else:
        await msg.answer("Asosiy menyu:", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS))

# ══════ BUYURTMA BERISH ══════
@dp.message(F.text == "🛍 Buyurtma berish")
async def h_buyurtma(msg: types.Message, state: FSMContext):
    await state.clear()
    ok, nj = await check_sub(msg.from_user.id)
    if not ok:
        await msg.answer("Avval kanallarga obuna bo'ling:", reply_markup=kb_sub(nj)); return
    nets   = get_nets()
    is_adm = msg.from_user.id in ADMIN_IDS
    if not nets:
        if is_adm:
            b = InlineKeyboardBuilder()
            b.button(text="➕ Tarmoq qo'shish", callback_data="NET:add")
            await msg.answer("Hali tarmoqlar yo'q.\nQo'shish uchun bosing:", reply_markup=b.as_markup())
        else:
            await msg.answer("Hozircha xizmatlar mavjud emas.")
        return
    b = InlineKeyboardBuilder()
    for n in nets:
        icon = NET_ICONS.get(n['name'], "🌐")
        b.button(text=f"{icon} {n['name']}", callback_data=f"NET:{n['id']}")
    if is_adm:
        b.button(text="➕ Tarmoq qo'shish", callback_data="NET:add")
    b.adjust(2)
    await msg.answer("Ijtimoiy tarmoqni tanlang:", reply_markup=b.as_markup())

async def show_nets_inline(obj, is_adm):
    nets = get_nets()
    b = InlineKeyboardBuilder()
    for n in nets:
        icon = NET_ICONS.get(n['name'], "🌐")
        b.button(text=f"{icon} {n['name']}", callback_data=f"NET:{n['id']}")
    if is_adm:
        b.button(text="➕ Tarmoq qo'shish", callback_data="NET:add")
    b.adjust(2)
    if hasattr(obj, 'edit_text'):
        await obj.edit_text("Ijtimoiy tarmoqni tanlang:", reply_markup=b.as_markup())
    else:
        await obj.answer("Ijtimoiy tarmoqni tanlang:", reply_markup=b.as_markup())

@dp.callback_query(F.data == "NET_BACK")
async def cb_net_back(call: types.CallbackQuery):
    await show_nets_inline(call.message, call.from_user.id in ADMIN_IDS)

@dp.callback_query(F.data.startswith("NET:"))
async def cb_net(call: types.CallbackQuery, state: FSMContext):
    val = call.data[4:]
    if val == "add":
        if call.from_user.id not in ADMIN_IDS: return
        await call.message.answer("Tarmoq nomini kiriting\n(masalan: Telegram, Instagram):", reply_markup=kb_back())
        await state.set_state(AdmS.net_name); return
    net_id   = int(val)
    is_adm   = call.from_user.id in ADMIN_IDS
    c = db()
    net_row  = c.execute("SELECT name FROM networks WHERE id=?", (net_id,)).fetchone()
    c.close()
    net_name = net_row[0] if net_row else ""
    icon     = NET_ICONS.get(net_name, "🌐")
    secs     = get_secs(net_id)
    if not secs and get_apis():
        await call.message.edit_text(f"{icon} {net_name} yuklanmoqda...")
        await sync_network_from_api(net_name)
        secs = get_secs(net_id)
    if not secs:
        b = InlineKeyboardBuilder()
        if is_adm:
            b.button(text="➕ Bo'lim qo'shish",   callback_data=f"SEC_ADD:{net_id}")
            b.button(text="🔄 API dan yuklash",    callback_data=f"NET_SYNC:{net_id}")
            b.button(text="📝 Nomini o'zgartirish",callback_data=f"NET_EDIT:{net_id}")
            b.button(text="🗑 O'chirish",          callback_data=f"NET_DEL:{net_id}")
        b.button(text="◀️ Orqaga", callback_data="NET_BACK")
        b.adjust(1)
        try:
            await call.message.edit_text(f"{icon} {net_name}\n\nXizmatlar yo'q.", reply_markup=b.as_markup())
        except:
            await call.message.answer(f"{icon} {net_name}\n\nXizmatlar yo'q.", reply_markup=b.as_markup())
        return
    b = InlineKeyboardBuilder()
    for s in secs:
        b.button(text=s['name'], callback_data=f"SEC:{s['id']}")
    if is_adm:
        b.button(text="➕ Bo'lim qo'shish",    callback_data=f"SEC_ADD:{net_id}")
        b.button(text="🔄 API dan yangilash",   callback_data=f"NET_SYNC:{net_id}")
        b.button(text="📝 Nomini o'zgartirish", callback_data=f"NET_EDIT:{net_id}")
        b.button(text="🗑 Tarmoqni o'chirish",  callback_data=f"NET_DEL:{net_id}")
    b.button(text="◀️ Orqaga", callback_data="NET_BACK")
    b.adjust(1)
    try:
        await call.message.edit_text(f"{icon} {net_name} — bo'limni tanlang:", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{icon} {net_name} — bo'limni tanlang:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("NET_SYNC:"))
async def cb_net_sync(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    net_id   = int(call.data[9:])
    c = db()
    net_row  = c.execute("SELECT name FROM networks WHERE id=?", (net_id,)).fetchone()
    c.close()
    net_name = net_row[0] if net_row else ""
    icon     = NET_ICONS.get(net_name, "🌐")
    try:
        await call.message.edit_text(f"{icon} {net_name} yuklanmoqda...")
    except: pass
    secs_c, srvs_c = await sync_network_from_api(net_name)
    secs = get_secs(net_id)
    b = InlineKeyboardBuilder()
    for s in secs:
        b.button(text=s['name'], callback_data=f"SEC:{s['id']}")
    b.button(text="➕ Bo'lim qo'shish",    callback_data=f"SEC_ADD:{net_id}")
    b.button(text="🔄 API dan yangilash",   callback_data=f"NET_SYNC:{net_id}")
    b.button(text="◀️ Orqaga", callback_data="NET_BACK")
    b.adjust(1)
    txt = f"✅ {secs_c} bo'lim, {srvs_c} xizmat yuklandi!\n{icon} {net_name}:" if srvs_c else f"{icon} {net_name}: API da topilmadi."
    try:
        await call.message.edit_text(txt, reply_markup=b.as_markup())
    except:
        await call.message.answer(txt, reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("NET_DEL:"))
async def cb_net_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    net_id = int(call.data[8:])
    c = db()
    net_row  = c.execute("SELECT name FROM networks WHERE id=?", (net_id,)).fetchone()
    net_name = net_row[0] if net_row else ""
    for sec in c.execute("SELECT id FROM sections WHERE net_id=?", (net_id,)).fetchall():
        c.execute("DELETE FROM services WHERE sec_id=?", (sec[0],))
    c.execute("DELETE FROM sections WHERE net_id=?", (net_id,))
    c.execute("DELETE FROM networks WHERE id=?", (net_id,))
    c.commit(); c.close()
    await call.answer(f"{net_name} o'chirildi!", show_alert=True)
    await show_nets_inline(call.message, True)

@dp.callback_query(F.data.startswith("NET_EDIT:"))
async def cb_net_edit(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    net_id = int(call.data[9:])
    await state.update_data(edit_net_id=net_id)
    await call.message.answer("Yangi tarmoq nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.net_edit)

@dp.message(AdmS.net_edit)
async def adm_net_edit(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    c = db(); c.execute("UPDATE networks SET name=? WHERE id=?", (msg.text.strip(), data.get("edit_net_id"))); c.commit(); c.close()
    await msg.answer("✅ Tarmoq nomi yangilandi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("SEC:"))
async def cb_sec(call: types.CallbackQuery):
    sec_id = int(call.data[4:])
    srvs   = get_srvs(sec_id)
    info   = get_sec_info(sec_id)
    net_id = info[2] if info else 0
    is_adm = call.from_user.id in ADMIN_IDS
    sec_name = info[0] if info else ""
    net_name = info[1] if info else ""
    icon = NET_ICONS.get(net_name, "🌐")
    if not srvs:
        b = InlineKeyboardBuilder()
        if is_adm:
            b.button(text="➕ Xizmat qo'shish",    callback_data=f"SRV_ADD:{sec_id}")
            b.button(text="📝 Bo'lim nomi",         callback_data=f"SEC_EDIT:{sec_id}")
            b.button(text="🗑 Bo'limni o'chirish",  callback_data=f"SEC_DEL:{sec_id}")
        b.button(text="◀️ Orqaga", callback_data=f"NET:{net_id}")
        b.adjust(1)
        try:
            await call.message.edit_text(f"{icon} {net_name} › {sec_name}\n\nXizmatlar yo'q.", reply_markup=b.as_markup())
        except:
            await call.message.answer(f"{icon} {net_name} › {sec_name}\n\nXizmatlar yo'q.", reply_markup=b.as_markup())
        return
    b = InlineKeyboardBuilder()
    for s in srvs:
        b.button(text=s['name'], callback_data=f"SRV:{s['id']}")
    if is_adm:
        b.button(text="➕ Xizmat qo'shish",    callback_data=f"SRV_ADD:{sec_id}")
        b.button(text="📝 Bo'lim nomi",         callback_data=f"SEC_EDIT:{sec_id}")
        b.button(text="🗑 Bo'limni o'chirish",  callback_data=f"SEC_DEL:{sec_id}")
    b.button(text="◀️ Orqaga", callback_data=f"NET:{net_id}")
    b.adjust(1)
    try:
        await call.message.edit_text(f"{icon} {net_name} › {sec_name}\n\nXizmatni tanlang:", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{icon} {net_name} › {sec_name}\n\nXizmatni tanlang:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("SEC_EDIT:"))
async def cb_sec_edit(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    sec_id = int(call.data[9:])
    await state.update_data(edit_sec_id=sec_id)
    await call.message.answer("Yangi bo'lim nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.sec_edit)

@dp.message(AdmS.sec_edit)
async def adm_sec_edit(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    c = db(); c.execute("UPDATE sections SET name=? WHERE id=?", (msg.text.strip(), data.get("edit_sec_id"))); c.commit(); c.close()
    await msg.answer("✅ Bo'lim nomi yangilandi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("SEC_DEL:"))
async def cb_sec_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    sec_id = int(call.data[8:])
    info   = get_sec_info(sec_id)
    net_id = info[2] if info else 0
    c = db()
    c.execute("DELETE FROM services WHERE sec_id=?", (sec_id,))
    c.execute("DELETE FROM sections WHERE id=?", (sec_id,))
    c.commit(); c.close()
    await call.answer("Bo'lim o'chirildi!", show_alert=True)
    # Net sahifasini qayta ko'rsat
    net_row = db().execute("SELECT name FROM networks WHERE id=?", (net_id,)).fetchone()
    net_name = net_row[0] if net_row else ""
    icon = NET_ICONS.get(net_name, "🌐")
    secs = get_secs(net_id)
    b = InlineKeyboardBuilder()
    for s in secs:
        b.button(text=s['name'], callback_data=f"SEC:{s['id']}")
    b.button(text="➕ Bo'lim qo'shish", callback_data=f"SEC_ADD:{net_id}")
    b.button(text="◀️ Orqaga", callback_data="NET_BACK")
    b.adjust(1)
    try:
        await call.message.edit_text(f"{icon} {net_name}:", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{icon} {net_name}:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("SRV:"))
async def cb_srv(call: types.CallbackQuery, state: FSMContext):
    srv_id = int(call.data[4:])
    s      = get_srv(srv_id)
    if not s: await call.answer("Topilmadi!"); return
    await state.update_data(srv_id=srv_id)
    info    = get_sec_info(s['sec_id'])
    sec_nm  = info[0] if info else ""
    net_nm  = info[1] if info else ""
    icon    = NET_ICONS.get(net_nm, "🌐")
    is_adm  = call.from_user.id in ADMIN_IDS
    b = InlineKeyboardBuilder()
    b.button(text="✅ Buyurtma berish", callback_data=f"BUY:{srv_id}")
    if is_adm:
        b.button(text="📝 Tahrirlash",     callback_data=f"SRV_EDIT:{srv_id}")
        b.button(text="🗑 O'chirish",      callback_data=f"SRV_DEL:{srv_id}")
    b.button(text="◀️ Orqaga", callback_data=f"SEC:{s['sec_id']}")
    b.adjust(1)
    try:
        await call.message.edit_text(
            f"{icon} {net_nm} › {sec_nm}\n\n"
            f"📌 {s['name']}\n\n"
            f"🔑 Xizmat IDsi: {s['api_id']}\n"
            f"💵 Narxi (1000x): {s['price']:,} So'm\n"
            f"⬇️ Min: {s['min_q']} ta\n"
            f"⬆️ Max: {s['max_q']} ta",
            reply_markup=b.as_markup())
    except:
        await call.message.answer(
            f"{icon} {net_nm} › {sec_nm}\n\n"
            f"📌 {s['name']}\n\n"
            f"🔑 Xizmat IDsi: {s['api_id']}\n"
            f"💵 Narxi (1000x): {s['price']:,} So'm\n"
            f"⬇️ Min: {s['min_q']} ta\n"
            f"⬆️ Max: {s['max_q']} ta",
            reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("SRV_EDIT:"))
async def cb_srv_edit(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    srv_id = int(call.data[9:])
    await state.update_data(edit_srv_id=srv_id)
    b = InlineKeyboardBuilder()
    b.button(text="📌 Nomini o'zgartirish",  callback_data=f"SRVCHG:name:{srv_id}")
    b.button(text="💰 Narxini o'zgartirish", callback_data=f"SRVCHG:price:{srv_id}")
    b.button(text="◀️ Orqaga",              callback_data=f"SRV:{srv_id}")
    b.adjust(1)
    await call.message.edit_reply_markup(reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("SRVCHG:"))
async def cb_srvchg(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    parts = call.data.split(":")
    field, srv_id = parts[1], int(parts[2])
    await state.update_data(edit_srv_id=srv_id, edit_srv_field=field)
    if field == "name":
        await call.message.answer("Yangi xizmat nomini kiriting:", reply_markup=kb_back())
        await state.set_state(AdmS.srv_edit_name)
    else:
        await call.message.answer("Yangi narxni kiriting (1000 tasi uchun So'm):", reply_markup=kb_back())
        await state.set_state(AdmS.srv_edit_price)

@dp.message(AdmS.srv_edit_name)
async def adm_srv_edit_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    c = db(); c.execute("UPDATE services SET name=? WHERE id=?", (msg.text.strip(), data["edit_srv_id"])); c.commit(); c.close()
    await msg.answer("✅ Xizmat nomi yangilandi!", reply_markup=kb_admin())

@dp.message(AdmS.srv_edit_price)
async def adm_srv_edit_price(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: price = int(msg.text.strip())
    except: await msg.answer("Noto'g'ri raqam!"); return
    data = await state.get_data(); await state.clear()
    c = db(); c.execute("UPDATE services SET price=? WHERE id=?", (price, data["edit_srv_id"])); c.commit(); c.close()
    await msg.answer("✅ Xizmat narxi yangilandi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("SRV_DEL:"))
async def cb_srv_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    srv_id = int(call.data[8:])
    s      = get_srv(srv_id)
    sec_id = s['sec_id'] if s else 0
    c = db(); c.execute("DELETE FROM services WHERE id=?", (srv_id,)); c.commit(); c.close()
    await call.answer("Xizmat o'chirildi!", show_alert=True)
    # Bo'lim sahifasiga qayt
    srvs = get_srvs(sec_id)
    info = get_sec_info(sec_id)
    net_id = info[2] if info else 0
    sec_name = info[0] if info else ""
    net_name = info[1] if info else ""
    icon = NET_ICONS.get(net_name, "🌐")
    b = InlineKeyboardBuilder()
    for sv in srvs:
        b.button(text=sv['name'], callback_data=f"SRV:{sv['id']}")
    b.button(text="➕ Xizmat qo'shish", callback_data=f"SRV_ADD:{sec_id}")
    b.button(text="◀️ Orqaga", callback_data=f"NET:{net_id}")
    b.adjust(1)
    try:
        await call.message.edit_text(f"{icon} {net_name} › {sec_name}:", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{icon} {net_name} › {sec_name}:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("BUY:"))
async def cb_buy(call: types.CallbackQuery, state: FSMContext):
    srv_id = int(call.data[4:])
    s = get_srv(srv_id)
    if not s: await call.answer("Topilmadi!"); return
    await state.clear()
    await state.update_data(srv_id=srv_id)
    await call.answer()
    await call.message.answer(
        f"Buyurtma miqdorini kiriting:\n\n"
        f"Ruxsat etiladi {s['min_q']} - dan {s['max_q']} - gacha",
        reply_markup=kb_back())
    await state.set_state(OrdS.qty)

@dp.message(OrdS.qty)
async def h_qty(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("Asosiy menyu:", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    try: qty = int(msg.text.strip())
    except: await msg.answer("Noto'g'ri son!"); return
    data   = await state.get_data()
    srv_id = data.get("srv_id")
    s = get_srv(srv_id)
    if not s:
        await state.clear(); await msg.answer("Xizmat topilmadi!", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    if qty < s['min_q'] or qty > s['max_q']:
        await msg.answer(f"{s['min_q']} dan {s['max_q']} gacha bo'lishi kerak!"); return
    price = int(qty * s['price'] / 1000)
    bal   = get_user(msg.from_user.id)['balance']
    await state.update_data(qty=qty, price=price)
    if bal < price:
        pays = get_pays()
        b = InlineKeyboardBuilder()
        for p in pays:
            b.button(text=p['name'], callback_data=f"PAYM_ORD:{p['id']}")
        b.adjust(2)
        await msg.answer(
            f"Balans yetarli emas!\n\nKerak: {price:,} So'm\nBalans: {bal:,} So'm\n\nTo'lov tizimini tanlang:",
            reply_markup=b.as_markup()); return
    await msg.answer(
        f"Buyurtma havolasini kiriting\n(masalan: https://instagram.com/username):",
        reply_markup=kb_back())
    await state.set_state(OrdS.link)

@dp.callback_query(F.data.startswith("PAYM_ORD:"))
async def cb_paym_ord(call: types.CallbackQuery, state: FSMContext):
    pid = int(call.data[9:])
    p   = db().execute("SELECT * FROM pay_methods WHERE id=?", (pid,)).fetchone()
    if not p: await call.answer("Topilmadi!"); return
    await state.update_data(pay_for_order=True)
    min_d = gcfg("min_dep") or "1000"
    await call.message.edit_text(
        f"💳 {p['name']}\n\n{p['details']}\n\nTo'lov chekini yuboring (minimum {min_d} So'm):")
    await state.set_state(AdmS.pay_name)

@dp.message(OrdS.link)
async def h_link(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear()
        await msg.answer("Asosiy menyu:", reply_markup=kb_main(msg.from_user.id in ADMIN_IDS)); return
    link  = msg.text.strip()
    data  = await state.get_data()
    s     = get_srv(data["srv_id"])
    price = data["price"]
    qty   = data["qty"]
    await state.update_data(link=link)
    b = InlineKeyboardBuilder()
    b.button(text="✅ Tasdiqlash", callback_data="ORD_CONFIRM")
    await msg.answer(
        f"Malumotlarni o'qib chiqing:\n\n"
        f"💵 Buyurtma narxi: {price:,} so'm\n"
        f"🔗 Manzil: {link}\n"
        f"🔢 Miqdor: {qty} ta\n\n"
        f"Tasdiqlash tugmasini bosing — hisobingizdan {price:,} so'm yechib olinadi!",
        reply_markup=b.as_markup())
    await state.set_state(OrdS.confirm)

@dp.callback_query(F.data == "ORD_CONFIRM", OrdS.confirm)
async def cb_ord_confirm(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    uid  = call.from_user.id
    u    = get_user(uid)
    if u['balance'] < data["price"]:
        await call.answer("Balans yetarli emas!", show_alert=True); return
    oid = create_order(uid, data["srv_id"], data["link"], data["qty"], data["price"])
    await state.clear()
    try:
        await call.message.edit_text(
            f"✅ Buyurtma muvaffaqiyatli ro'yxatdan o'tkazildi\n\n"
            f"Buyurtma ID raqami: {oid}")
    except:
        await call.message.answer(f"✅ Buyurtma {oid} qabul qilindi!")
    for aid in ADMIN_IDS:
        try:
            s = get_srv(data["srv_id"])
            await bot.send_message(aid,
                f"Yangi buyurtma #{oid}\n"
                f"👤 {uid}\n"
                f"📌 {s['name'] if s else '?'}\n"
                f"🔗 {data['link']}\n"
                f"📊 {data['qty']} ta | 💰 {data['price']:,} So'm")
        except: pass

# ══════ BUYURTMALAR ══════
@dp.message(F.text == "📋 Buyurtmalar")
async def h_buyurtmalar(msg: types.Message):
    uid  = msg.from_user.id
    ords = db().execute("SELECT * FROM orders WHERE uid=? ORDER BY id DESC LIMIT 15", (uid,)).fetchall()
    if not ords:
        await msg.answer("Sizda hali buyurtmalar yo'q."); return
    text = "Oxirgi buyurtmalar:\n\n"
    for o in ords:
        s  = get_srv(o['srv_id'])
        nm = s['name'] if s else "?"
        text += f"#{o['id']} | {nm}\n💰 {o['price']:,} So'm | {o['qty']} ta | {o['status']}\n\n"
    await msg.answer(text)

# ══════ HISOBIM ══════
@dp.message(F.text == "👤 Hisobim")
async def h_hisobim(msg: types.Message):
    uid = msg.from_user.id
    ensure_user(uid)
    u   = get_user(uid)
    ords_c = db().execute("SELECT COUNT(*) FROM orders WHERE uid=?", (uid,)).fetchone()[0]
    refs_c = db().execute("SELECT COUNT(*) FROM users WHERE ref_id=?", (uid,)).fetchone()[0]
    me = await bot.get_me()
    await msg.answer(
        f"👤 Profil\n\n"
        f"🆔 ID: {uid}\n"
        f"💰 Balans: {u['balance']:,} So'm\n"
        f"📦 Buyurtmalar: {ords_c} ta\n"
        f"👥 Referallar: {refs_c} ta\n\n"
        f"Referal havola:\nhttps://t.me/{me.username}?start={uid}")

# ══════ HISOB TO'LDIRISH ══════
@dp.message(F.text == "💳 Hisob to'ldirish")
async def h_topdirish(msg: types.Message):
    pays = get_pays()
    if not pays:
        await msg.answer("Hozircha to'lov tizimlari yo'q."); return
    b = InlineKeyboardBuilder()
    for p in pays:
        b.button(text=p['name'], callback_data=f"PAY:{p['id']}")
    b.adjust(2)
    await msg.answer("To'lov tizimini tanlang:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("PAY:"))
async def cb_pay(call: types.CallbackQuery, state: FSMContext):
    pid = int(call.data[4:])
    p   = db().execute("SELECT * FROM pay_methods WHERE id=?", (pid,)).fetchone()
    if not p: await call.answer("Topilmadi!"); return
    min_d = gcfg("min_dep") or "1000"
    await state.update_data(pay_id=pid, pay_for_order=False)
    try:
        await call.message.edit_text(
            f"💳 {p['name']}\n\n{p['details']}\n\nTo'lov chekini yuboring (minimum {min_d} So'm):")
    except:
        await call.message.answer(
            f"💳 {p['name']}\n\n{p['details']}\n\nTo'lov chekini yuboring (minimum {min_d} So'm):")
    await state.set_state(AdmS.pay_name)

@dp.message(AdmS.pay_name)
async def adm_pay_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data()
    if data.get("pay_for_order") or data.get("pay_id"):
        # Bu chek yuborish
        uid = msg.from_user.id
        u   = get_user(uid)
        for aid in ADMIN_IDS:
            try:
                b = InlineKeyboardBuilder()
                b.button(text="✅ Tasdiqlash", callback_data=f"APYES:{uid}")
                b.button(text="❌ Rad etish",  callback_data=f"APNO:{uid}")
                b.adjust(2)
                if msg.photo:
                    await bot.send_photo(aid, msg.photo[-1].file_id,
                        caption=f"To'lov so'rovi\n👤 {uid} | @{msg.from_user.username or '-'}\n💰 Balans: {u['balance']:,} So'm",
                        reply_markup=b.as_markup())
                else:
                    await bot.send_message(aid,
                        f"To'lov so'rovi\n👤 {uid} | @{msg.from_user.username or '-'}\n💰 Balans: {u['balance']:,} So'm\n\n{msg.text}",
                        reply_markup=b.as_markup())
            except: pass
        await msg.answer("✅ To'lovingiz adminga yuborildi. Tasdiqlashni kuting.", reply_markup=kb_main(uid in ADMIN_IDS))
        await state.clear(); return
    # Admin to'lov tizimi qo'shyapti
    await state.update_data(pay_name_new=msg.text.strip())
    await msg.answer("To'lov ma'lumotlarini kiriting (karta raqam, telefon):", reply_markup=kb_back())
    await state.set_state(AdmS.pay_det)

@dp.message(AdmS.pay_det)
async def adm_pay_det(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    c = db()
    c.execute("INSERT INTO pay_methods(name,details) VALUES(?,?)", (data["pay_name_new"], msg.text.strip()))
    c.commit(); c.close()
    await msg.answer(f"✅ {data['pay_name_new']} to'lov tizimi qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("APYES:"))
async def cb_apyes(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data.split(":")[1])
    b = InlineKeyboardBuilder()
    amounts = [1000, 5000, 10000, 25000, 50000, 100000, 200000, 500000]
    for a in amounts:
        b.button(text=f"{a:,}", callback_data=f"ADDBAL:{uid}:{a}")
    b.adjust(4)
    if call.message.caption:
        await call.message.edit_caption(caption=f"✅ {uid} — summani tanlang:", reply_markup=b.as_markup())
    else:
        try:
            await call.message.edit_text(f"✅ {uid} — summani tanlang:", reply_markup=b.as_markup())
        except:
            await call.message.answer(f"✅ {uid} — summani tanlang:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("ADDBAL:"))
async def cb_addbal(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    parts = call.data.split(":")
    uid, amt = int(parts[1]), int(parts[2])
    c = db()
    c.execute("UPDATE users SET balance=balance+?, deposited=deposited+? WHERE id=?", (amt, amt, uid))
    c.commit(); c.close()
    if call.message.caption:
        await call.message.edit_caption(caption=f"✅ {uid} ga {amt:,} So'm qo'shildi!")
    else:
        try:
            await call.message.edit_text(f"✅ {uid} ga {amt:,} So'm qo'shildi!")
        except:
            await call.message.answer(f"✅ {uid} ga {amt:,} So'm qo'shildi!")
    try: await bot.send_message(uid, f"✅ Hisobingizga {amt:,} So'm qo'shildi!")
    except: pass

@dp.callback_query(F.data.startswith("APNO:"))
async def cb_apno(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    uid = int(call.data[5:])
    if call.message.caption:
        await call.message.edit_caption(caption=f"❌ {uid} rad etildi.")
    else:
        try:
            await call.message.edit_text(f"❌ {uid} rad etildi.")
        except:
            await call.message.answer(f"❌ {uid} rad etildi.")
    try: await bot.send_message(uid, "❌ To'lovingiz rad etildi.")
    except: pass

# ══════ PUL ISHLASH ══════
@dp.message(F.text == "💰 Pul ishlash")
async def h_ref(msg: types.Message):
    uid    = msg.from_user.id
    bonus  = gcfg("ref_bonus") or "500"
    refs_c = db().execute("SELECT COUNT(*) FROM users WHERE ref_id=?", (uid,)).fetchone()[0]
    me     = await bot.get_me()
    await msg.answer(
        f"Referal tizimi\n\n"
        f"Har bir do'stingiz uchun {bonus} So'm bonus!\n\n"
        f"Referallaringiz: {refs_c} ta\n\n"
        f"Sizning havolangiz:\nhttps://t.me/{me.username}?start={uid}")

# ══════ QO'LLANMA ══════
@dp.message(F.text == "❓ Qo'llanma")
async def h_qollanma(msg: types.Message):
    faqs = get_faqs()
    if not faqs:
        await msg.answer("Hozircha qo'llanma yo'q."); return
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f['q'][:40], callback_data=f"FAQ:{f['id']}")
    b.adjust(1)
    await msg.answer("Qo'llanma:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("FAQ:"))
async def cb_faq(call: types.CallbackQuery):
    fid = int(call.data[4:])
    f   = db().execute("SELECT * FROM faqs WHERE id=?", (fid,)).fetchone()
    if not f: return
    b = InlineKeyboardBuilder()
    b.button(text="◀️ Orqaga", callback_data="FAQ_BACK")
    try:
        await call.message.edit_text(f"{f['q']}\n\n{f['a']}", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{f['q']}\n\n{f['a']}", reply_markup=b.as_markup())

@dp.callback_query(F.data == "FAQ_BACK")
async def cb_faq_back(call: types.CallbackQuery):
    faqs = get_faqs()
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f['q'][:40], callback_data=f"FAQ:{f['id']}")
    b.adjust(1)
    try:
        await call.message.edit_text("Qo'llanma:", reply_markup=b.as_markup())
    except:
        await call.message.answer("Qo'llanma:", reply_markup=b.as_markup())

# ══════ MUROJAAT ══════
@dp.message(F.text == "📞 Murojaat")
async def h_murojaat(msg: types.Message):
    await msg.answer("Admin bilan bog'lanish:\n@admin_username")

# ══════ ADMIN PANEL ══════
@dp.message(F.text == "🖥 Boshqaruv")
async def h_boshqaruv(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("Admin paneliga xush kelibsiz!", reply_markup=kb_admin())

@dp.message(F.text == "📊 Statistika")
async def h_stat(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    c   = db()
    u   = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    o   = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    oa  = c.execute("SELECT COUNT(*) FROM orders WHERE status='Jarayonda'").fetchone()[0]
    rev = c.execute("SELECT SUM(price) FROM orders").fetchone()[0] or 0
    c.close()
    await msg.answer(
        f"Statistika\n\n"
        f"Foydalanuvchilar: {u} ta\n"
        f"Buyurtmalar: {o} ta\n"
        f"Jarayondagi: {oa} ta\n"
        f"Jami daromad: {rev:,} So'm")

# ── Foydalanuvchilar ──
@dp.message(F.text == "👥 Foydalanuvchilar")
async def h_users(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="➕ Balans qo'shish", callback_data="ADM_ADDBAL")
    b.button(text="➖ Balans ayirish",  callback_data="ADM_SUBBAL")
    b.adjust(2)
    c = db()
    u = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]; c.close()
    await msg.answer(f"Jami {u} ta foydalanuvchi:", reply_markup=b.as_markup())

@dp.callback_query(F.data == "ADM_ADDBAL")
async def cb_adm_addbal(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Foydalanuvchi ID sini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.add_bal_uid)

@dp.message(AdmS.add_bal_uid)
async def adm_add_bal_uid(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    if not msg.text.strip().isdigit():
        await msg.answer("Noto'g'ri ID!"); return
    await state.update_data(target_uid=int(msg.text.strip()))
    await msg.answer("Qancha so'm qo'shish?:", reply_markup=kb_back())
    await state.set_state(AdmS.add_bal)

@dp.message(AdmS.add_bal)
async def adm_add_bal(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: amt = int(msg.text.strip())
    except: await msg.answer("Noto'g'ri!"); return
    data = await state.get_data(); await state.clear()
    uid  = data.get("target_uid")
    c = db(); c.execute("UPDATE users SET balance=balance+? WHERE id=?", (amt, uid)); c.commit(); c.close()
    await msg.answer(f"✅ {uid} ga {amt:,} So'm qo'shildi!", reply_markup=kb_admin())
    try: await bot.send_message(uid, f"✅ Hisobingizga {amt:,} So'm qo'shildi!")
    except: pass

@dp.callback_query(F.data == "ADM_SUBBAL")
async def cb_adm_subbal(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Foydalanuvchi ID sini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.sub_bal_uid)

@dp.message(AdmS.sub_bal_uid)
async def adm_sub_bal_uid(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    if not msg.text.strip().isdigit():
        await msg.answer("Noto'g'ri ID!"); return
    await state.update_data(target_uid=int(msg.text.strip()))
    await msg.answer("Qancha so'm ayirish?:", reply_markup=kb_back())
    await state.set_state(AdmS.sub_bal)

@dp.message(AdmS.sub_bal)
async def adm_sub_bal(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: amt = int(msg.text.strip())
    except: await msg.answer("Noto'g'ri!"); return
    data = await state.get_data(); await state.clear()
    uid  = data.get("target_uid")
    c = db(); c.execute("UPDATE users SET balance=balance-? WHERE id=?", (amt, uid)); c.commit(); c.close()
    await msg.answer(f"✅ {uid} dan {amt:,} So'm ayirildi!", reply_markup=kb_admin())

# ── Tarmoqlar (Admin) ──
@dp.message(F.text == "🌐 Tarmoqlar")
async def h_admin_nets(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    nets = get_nets()
    b = InlineKeyboardBuilder()
    for n in nets:
        icon = NET_ICONS.get(n['name'], "🌐")
        secs_c = len(get_secs(n['id']))
        b.button(text=f"{icon} {n['name']} ({secs_c})", callback_data=f"ADNET:{n['id']}")
    b.button(text="➕ Yangi tarmoq", callback_data="NET:add")
    b.adjust(2, 1)
    await msg.answer(f"Tarmoqlar ({len(nets)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("ADNET:"))
async def cb_adnet(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    net_id   = int(call.data[6:])
    c = db()
    net_row  = c.execute("SELECT name FROM networks WHERE id=?", (net_id,)).fetchone()
    c.close()
    net_name = net_row[0] if net_row else ""
    icon     = NET_ICONS.get(net_name, "🌐")
    secs     = get_secs(net_id)
    total_srvs = sum(len(get_srvs(s['id'])) for s in secs)
    b = InlineKeyboardBuilder()
    b.button(text="➕ Bo'lim qo'shish",    callback_data=f"SEC_ADD:{net_id}")
    b.button(text="🔄 API dan yuklash",    callback_data=f"NET_SYNC:{net_id}")
    b.button(text="📝 Nomini o'zgartirish",callback_data=f"NET_EDIT:{net_id}")
    b.button(text="🗑 O'chirish",          callback_data=f"NET_DEL:{net_id}")
    b.button(text="◀️ Orqaga",            callback_data="ADNET_BACK")
    b.adjust(2, 2, 1)
    try:
        await call.message.edit_text(
            f"{icon} {net_name}\n\nBo'limlar: {len(secs)}\nXizmatlar: {total_srvs}",
            reply_markup=b.as_markup())
    except:
        await call.message.answer(
            f"{icon} {net_name}\n\nBo'limlar: {len(secs)}\nXizmatlar: {total_srvs}",
            reply_markup=b.as_markup())

@dp.callback_query(F.data == "ADNET_BACK")
async def cb_adnet_back(call: types.CallbackQuery):
    nets = get_nets()
    b = InlineKeyboardBuilder()
    for n in nets:
        icon   = NET_ICONS.get(n['name'], "🌐")
        secs_c = len(get_secs(n['id']))
        b.button(text=f"{icon} {n['name']} ({secs_c})", callback_data=f"ADNET:{n['id']}")
    b.button(text="➕ Yangi tarmoq", callback_data="NET:add")
    b.adjust(2, 1)
    try:
        await call.message.edit_text(f"Tarmoqlar ({len(nets)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"Tarmoqlar ({len(nets)} ta):", reply_markup=b.as_markup())

# ── Tarmoq/Bo'lim/Xizmat qo'shish ──
@dp.callback_query(F.data.startswith("SEC_ADD:"))
async def cb_sec_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    net_id = int(call.data[8:])
    await state.update_data(sec_net_id=net_id)
    await call.message.answer("Bo'lim nomini kiriting\n(masalan: Obunchi, Like, Ko'rish):", reply_markup=kb_back())
    await state.set_state(AdmS.sec_name)

@dp.callback_query(F.data.startswith("SRV_ADD:"))
async def cb_srv_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    sec_id = int(call.data[8:])
    await state.update_data(srv_sec_id=sec_id)
    await call.message.answer("Xizmat API IDsini kiriting (masalan: 384):", reply_markup=kb_back())
    await state.set_state(AdmS.srv_api)

@dp.callback_query(F.data.startswith("SRV_MORE:"))
async def cb_srv_more(call: types.CallbackQuery, state: FSMContext):
    sec_id = int(call.data[9:])
    await state.update_data(srv_sec_id=sec_id)
    await call.message.answer("Xizmat API IDsini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.srv_api)

@dp.callback_query(F.data.startswith("SEC_MORE:"))
async def cb_sec_more(call: types.CallbackQuery, state: FSMContext):
    net_id = int(call.data[9:])
    await state.update_data(sec_net_id=net_id)
    await call.message.answer("Yangi bo'lim nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.sec_name)

@dp.callback_query(F.data == "NET_MORE")
async def cb_net_more(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Yangi tarmoq nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.net_name)

@dp.callback_query(F.data == "ADM_BACK")
async def cb_adm_back(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Admin paneliga xush kelibsiz!", reply_markup=kb_admin())

@dp.message(AdmS.net_name)
async def adm_net_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    name = msg.text.strip()
    c    = db()
    c.execute("INSERT OR IGNORE INTO networks(name) VALUES(?)", (name,))
    net_id = c.execute("SELECT id FROM networks WHERE name=?", (name,)).fetchone()[0]
    c.commit(); c.close()
    await state.update_data(sec_net_id=net_id)
    await msg.answer(
        f"✅ {name} tarmoqi qo'shildi!\n\n"
        f"Bo'lim nomini kiriting\n(masalan: Obunchi, Like, Ko'rish):",
        reply_markup=kb_back())
    await state.set_state(AdmS.sec_name)

@dp.message(AdmS.sec_name)
async def adm_sec_name(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    name   = msg.text.strip()
    data   = await state.get_data()
    net_id = data.get("sec_net_id") or data.get("net_id")
    c = db()
    c.execute("INSERT INTO sections(net_id,name) VALUES(?,?)", (net_id, name))
    sec_id = c.lastrowid; c.commit(); c.close()
    await state.update_data(srv_sec_id=sec_id)
    await msg.answer(
        f"✅ {name} bo'limi qo'shildi!\n\n"
        f"Xizmat API IDsini kiriting (masalan: 384):",
        reply_markup=kb_back())
    await state.set_state(AdmS.srv_api)

@dp.message(AdmS.srv_api)
async def adm_srv_api(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(srv_api=msg.text.strip())
    await msg.answer("Narxini kiriting (1000 tasi uchun So'm, masalan: 500):", reply_markup=kb_back())
    await state.set_state(AdmS.srv_price)

@dp.message(AdmS.srv_price)
async def adm_srv_price(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: price = int(msg.text.strip())
    except: await msg.answer("Noto'g'ri raqam!"); return
    await state.update_data(srv_price=price)
    await msg.answer("Xizmat nomini kiriting\n(masalan: Obunchi Tezkor, Like Premium):", reply_markup=kb_back())
    await state.set_state(AdmS.srv_info)

@dp.message(AdmS.srv_info)
async def adm_srv_info(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data   = await state.get_data()
    sec_id = data.get("srv_sec_id")
    if not sec_id:
        await state.clear(); await msg.answer("Bo'lim topilmadi!", reply_markup=kb_admin()); return
    api_id   = data.get("srv_api", "")
    price    = data.get("srv_price", 0)
    srv_name = msg.text.strip()
    c = db()
    c.execute("INSERT INTO services(sec_id,api_id,name,price,min_q,max_q,info) VALUES(?,?,?,?,10,100000,?)",
              (sec_id, api_id, srv_name, price, ""))
    c.commit()
    sec_row = c.execute(
        "SELECT s.name, n.id, n.name FROM sections s JOIN networks n ON s.net_id=n.id WHERE s.id=?",
        (sec_id,)).fetchone()
    c.close()
    sec_name = sec_row[0] if sec_row else ""
    net_id   = sec_row[1] if sec_row else 0
    net_name = sec_row[2] if sec_row else ""
    b = InlineKeyboardBuilder()
    b.button(text=f"➕ Yana xizmat ({sec_name}ga)",  callback_data=f"SRV_MORE:{sec_id}")
    b.button(text=f"➕ Yangi bo'lim ({net_name}ga)",  callback_data=f"SEC_MORE:{net_id}")
    b.button(text="➕ Boshqa tarmoq qo'shish",         callback_data="NET_MORE")
    b.button(text="◀️ Admin panel",                    callback_data="ADM_BACK")
    b.adjust(1)
    await msg.answer(
        f"✅ Xizmat qo'shildi!\n\n"
        f"🌐 {net_name}  ›  {sec_name}\n"
        f"📌 {srv_name}\n"
        f"🔑 API ID: {api_id}\n"
        f"💰 Narx: {price:,} So'm (1000 tasi)\n\n"
        f"Keyingi qadam:",
        reply_markup=b.as_markup())
    await state.clear()

# ── Majburiy obuna ──
@dp.message(F.text == "📢 Majburiy obuna")
async def h_channels(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    chans = get_channels()
    b = InlineKeyboardBuilder()
    for ch in chans:
        b.button(text=f"📢 {ch['title']}", callback_data=f"CH_VIEW:{ch['id']}")
    b.button(text="➕ Kanal qo'shish", callback_data="CH_ADD")
    b.adjust(1)
    await msg.answer(f"Majburiy obuna ({len(chans)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data == "CH_ADD")
async def cb_ch_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="📢 Ommaviy (a'zolik tekshiriladi)", callback_data="CHTYPE:public")
    b.button(text="🔒 Shaxsiy (faqat havola)",         callback_data="CHTYPE:private")
    b.adjust(1)
    try:
        await call.message.edit_text("Kanal turini tanlang:", reply_markup=b.as_markup())
    except:
        await call.message.answer("Kanal turini tanlang:", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("CHTYPE:"))
async def cb_chtype(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    ch_type = call.data[7:]
    await state.update_data(ch_type=ch_type)
    if ch_type == "public":
        await call.message.answer("Kanal ID kiriting (@channel yoki -100123456):", reply_markup=kb_back())
        await state.set_state(AdmS.ch_cid)
    else:
        await call.message.answer("Kanal nomini kiriting:", reply_markup=kb_back())
        await state.set_state(AdmS.ch_title)

@dp.message(AdmS.ch_cid)
async def adm_ch_cid(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(ch_cid=msg.text.strip())
    await msg.answer("Kanal nomini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.ch_title)

@dp.message(AdmS.ch_title)
async def adm_ch_title(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(ch_title=msg.text.strip())
    await msg.answer("Kanal havolasini kiriting (https://t.me/channel):", reply_markup=kb_back())
    await state.set_state(AdmS.ch_url)

@dp.message(AdmS.ch_url)
async def adm_ch_url(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data  = await state.get_data(); await state.clear()
    ctype = data.get("ch_type", "public")
    cid   = data.get("ch_cid", "link")
    title = data.get("ch_title", "")
    c = db()
    c.execute("INSERT INTO channels(cid,title,url,type) VALUES(?,?,?,?)", (cid, title, msg.text.strip(), ctype))
    c.commit(); c.close()
    await msg.answer(f"✅ {title} kanali qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("CH_VIEW:"))
async def cb_ch_view(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    chid = int(call.data[8:])
    ch   = db().execute("SELECT * FROM channels WHERE id=?", (chid,)).fetchone()
    if not ch: return
    b = InlineKeyboardBuilder()
    b.button(text="🗑 O'chirish", callback_data=f"CH_DEL:{chid}")
    b.button(text="◀️ Orqaga",   callback_data="CH_BACK")
    b.adjust(1)
    try:
        await call.message.edit_text(
            f"📢 {ch['title']}\n🔗 {ch['url']}\nTur: {ch['type']}",
            reply_markup=b.as_markup())
    except:
        await call.message.answer(
            f"📢 {ch['title']}\n🔗 {ch['url']}\nTur: {ch['type']}",
            reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("CH_DEL:"))
async def cb_ch_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    chid = int(call.data[7:])
    c = db(); c.execute("DELETE FROM channels WHERE id=?", (chid,)); c.commit(); c.close()
    await call.answer("Kanal o'chirildi!", show_alert=True)
    chans = get_channels()
    b = InlineKeyboardBuilder()
    for ch in chans:
        b.button(text=f"📢 {ch['title']}", callback_data=f"CH_VIEW:{ch['id']}")
    b.button(text="➕ Kanal qo'shish", callback_data="CH_ADD")
    b.adjust(1)
    try:
        await call.message.edit_text(f"Majburiy obuna ({len(chans)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"Majburiy obuna ({len(chans)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data == "CH_BACK")
async def cb_ch_back(call: types.CallbackQuery):
    chans = get_channels()
    b = InlineKeyboardBuilder()
    for ch in chans:
        b.button(text=f"📢 {ch['title']}", callback_data=f"CH_VIEW:{ch['id']}")
    b.button(text="➕ Kanal qo'shish", callback_data="CH_ADD")
    b.adjust(1)
    try:
        await call.message.edit_text(f"Majburiy obuna ({len(chans)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"Majburiy obuna ({len(chans)} ta):", reply_markup=b.as_markup())

# ── To'lov tizimlari ──
@dp.message(F.text == "💳 To'lov tizimlari")
async def h_pays(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    pays = get_pays()
    b = InlineKeyboardBuilder()
    for p in pays:
        b.button(text=p['name'], callback_data=f"PAYV:{p['id']}")
    b.button(text="➕ Qo'shish", callback_data="PAY_ADD_ADM")
    b.adjust(2, 1)
    await msg.answer(f"To'lov tizimlari ({len(pays)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data == "PAY_ADD_ADM")
async def cb_pay_add_adm(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("To'lov tizimi nomi (masalan: Click, Payme):", reply_markup=kb_back())
    await state.set_state(AdmS.pay_name)

@dp.callback_query(F.data.startswith("PAYV:"))
async def cb_payv(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    pid = int(call.data[5:])
    p   = db().execute("SELECT * FROM pay_methods WHERE id=?", (pid,)).fetchone()
    if not p: return
    b = InlineKeyboardBuilder()
    b.button(text="🗑 O'chirish", callback_data=f"PAY_DEL:{pid}")
    b.button(text="◀️ Orqaga",   callback_data="PAY_BACK")
    b.adjust(1)
    try:
        await call.message.edit_text(f"{p['name']}\n\n{p['details']}", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{p['name']}\n\n{p['details']}", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("PAY_DEL:"))
async def cb_pay_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    pid = int(call.data[8:])
    c = db(); c.execute("DELETE FROM pay_methods WHERE id=?", (pid,)); c.commit(); c.close()
    await call.answer("O'chirildi!", show_alert=True)
    pays = get_pays()
    b = InlineKeyboardBuilder()
    for p in pays:
        b.button(text=p['name'], callback_data=f"PAYV:{p['id']}")
    b.button(text="➕ Qo'shish", callback_data="PAY_ADD_ADM")
    b.adjust(2, 1)
    try:
        await call.message.edit_text(f"To'lov tizimlari ({len(pays)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"To'lov tizimlari ({len(pays)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data == "PAY_BACK")
async def cb_pay_back(call: types.CallbackQuery):
    pays = get_pays()
    b = InlineKeyboardBuilder()
    for p in pays:
        b.button(text=p['name'], callback_data=f"PAYV:{p['id']}")
    b.button(text="➕ Qo'shish", callback_data="PAY_ADD_ADM")
    b.adjust(2, 1)
    try:
        await call.message.edit_text(f"To'lov tizimlari ({len(pays)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"To'lov tizimlari ({len(pays)} ta):", reply_markup=b.as_markup())

# ── API ──
@dp.message(F.text == "🔑 API")
async def h_api(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    apis = get_apis()
    b = InlineKeyboardBuilder()
    for i, a in enumerate(apis, 1):
        domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
        b.button(text=f"{i}. {domain}", callback_data=f"APIVIEW:{a['id']}")
    b.button(text="➕ API qo'shish", callback_data="API_ADD")
    b.adjust(1)
    txt = f"API'lar ({len(apis)} ta)"
    if apis:
        txt += ":\n"
        for i, a in enumerate(apis, 1):
            domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
            txt += f"\n{i}. {domain} — {a['price']} UZS"
    await msg.answer(txt, reply_markup=b.as_markup())

@dp.callback_query(F.data == "API_ADD")
async def cb_api_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("API URL kiriting (masalan: https://saleseen.uz/api/v2):", reply_markup=kb_back())
    await state.set_state(AdmS.api_url)

@dp.message(AdmS.api_url)
async def adm_api_url(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(api_url=msg.text.strip())
    await msg.answer("API kalitini kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.api_key)

@dp.message(AdmS.api_key)
async def adm_api_key(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(api_key=msg.text.strip())
    await msg.answer("API narxini kiriting (UZS, masalan: 1430):", reply_markup=kb_back())
    await state.set_state(AdmS.api_price)

@dp.message(AdmS.api_price)
async def adm_api_price(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    try: price = int(msg.text.strip())
    except: await msg.answer("Noto'g'ri son!"); return
    data = await state.get_data(); await state.clear()
    c = db()
    c.execute("INSERT INTO apis(url,key,price) VALUES(?,?,?)", (data["api_url"], data["api_key"], price))
    c.commit(); c.close()
    domain = data["api_url"].replace("https://","").replace("http://","").split("/")[0]
    await msg.answer(f"✅ {domain} API qo'shildi!\n\nXizmatlar yuklanmoqda...", reply_markup=kb_admin())
    try:
        results = await auto_load_all_networks()
        if results:
            icons = {"Telegram":"✈️","Instagram":"📷","TikTok":"🎵","YouTube":"▶️","Facebook":"👥","Twitter":"🐦"}
            lines = ["✅ Xizmatlar yuklandi:\n"]
            total = 0
            for net_name, (secs_c, srvs_c) in results.items():
                icon = icons.get(net_name, "🌐")
                lines.append(f"{icon} {net_name}: {secs_c} bo'lim, {srvs_c} xizmat")
                total += srvs_c
            lines.append(f"\nJami: {total} ta xizmat")
            await msg.answer("\n".join(lines))
        else:
            await msg.answer("API dan xizmatlar yuklanmadi.\nURL va kalitni tekshiring.")
    except Exception as e:
        await msg.answer(f"Xato: {e}")

@dp.callback_query(F.data.startswith("APIVIEW:"))
async def cb_api_view(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    aid = int(call.data[8:])
    a   = db().execute("SELECT * FROM apis WHERE id=?", (aid,)).fetchone()
    if not a: return
    domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
    b = InlineKeyboardBuilder()
    b.button(text="🔄 Kalitni o'zgartirish", callback_data=f"API_CHKEY:{aid}")
    b.button(text="🗑 O'chirish",             callback_data=f"API_DEL:{aid}")
    b.button(text="◀️ Orqaga",               callback_data="API_BACK")
    b.adjust(1)
    try:
        await call.message.edit_text(
            f"{domain}\n\nURL: {a['url']}\nKalit: <code>{a['key']}</code>\nNarx: {a['price']} UZS",
            reply_markup=b.as_markup(), parse_mode="HTML")
    except:
        await call.message.answer(
            f"{domain}\n\nURL: {a['url']}\nKalit: <code>{a['key']}</code>\nNarx: {a['price']} UZS",
            reply_markup=b.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "API_BACK")
async def cb_api_back(call: types.CallbackQuery):
    apis = get_apis()
    b = InlineKeyboardBuilder()
    for i, a in enumerate(apis, 1):
        domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
        b.button(text=f"{i}. {domain}", callback_data=f"APIVIEW:{a['id']}")
    b.button(text="➕ API qo'shish", callback_data="API_ADD")
    b.adjust(1)
    try:
        await call.message.edit_text(f"API'lar ({len(apis)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"API'lar ({len(apis)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("API_DEL:"))
async def cb_api_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    aid = int(call.data[8:])
    c = db(); c.execute("DELETE FROM apis WHERE id=?", (aid,)); c.commit(); c.close()
    await call.answer("API o'chirildi!", show_alert=True)
    apis = get_apis()
    b = InlineKeyboardBuilder()
    for i, a in enumerate(apis, 1):
        domain = a['url'].replace("https://","").replace("http://","").split("/")[0]
        b.button(text=f"{i}. {domain}", callback_data=f"APIVIEW:{a['id']}")
    b.button(text="➕ API qo'shish", callback_data="API_ADD")
    b.adjust(1)
    try:
        await call.message.edit_text(f"API'lar ({len(apis)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"API'lar ({len(apis)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("API_CHKEY:"))
async def cb_api_chkey(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    aid = int(call.data[10:])
    await state.update_data(edit_api_id=aid)
    await call.message.answer("Yangi kalitni kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.api_new_key)

@dp.message(AdmS.api_new_key)
async def adm_api_new_key(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    c = db(); c.execute("UPDATE apis SET key=? WHERE id=?", (msg.text.strip(), data.get("edit_api_id"))); c.commit(); c.close()
    await msg.answer("✅ API kaliti yangilandi!", reply_markup=kb_admin())

# ── Xabar yuborish ──
@dp.message(F.text == "📨 Xabar yuborish")
async def h_broadcast(msg: types.Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS: return
    await msg.answer("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.broadcast)

@dp.message(AdmS.broadcast)
async def adm_broadcast(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.clear()
    users = db().execute("SELECT id FROM users").fetchall()
    ok = fail = 0
    for u in users:
        try:
            await bot.copy_message(u[0], msg.chat.id, msg.message_id)
            ok += 1
        except: fail += 1
    await msg.answer(f"✅ Yuborildi: {ok}\n❌ Xato: {fail}", reply_markup=kb_admin())

# ── FAQ ──
@dp.message(F.text == "❓ FAQ")
async def h_admin_faq(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    faqs = get_faqs()
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f['q'][:35], callback_data=f"AFAQ:{f['id']}")
    b.button(text="➕ Qo'shish", callback_data="FAQ_ADD")
    b.adjust(1)
    await msg.answer(f"FAQ ({len(faqs)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data == "FAQ_ADD")
async def cb_faq_add(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS: return
    await call.message.answer("Savol kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.faq_q)

@dp.message(AdmS.faq_q)
async def adm_faq_q(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    await state.update_data(faq_q=msg.text.strip())
    await msg.answer("Javob kiriting:", reply_markup=kb_back())
    await state.set_state(AdmS.faq_a)

@dp.message(AdmS.faq_a)
async def adm_faq_a(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    data = await state.get_data(); await state.clear()
    c = db(); c.execute("INSERT INTO faqs(q,a) VALUES(?,?)", (data["faq_q"], msg.text.strip())); c.commit(); c.close()
    await msg.answer("✅ FAQ qo'shildi!", reply_markup=kb_admin())

@dp.callback_query(F.data.startswith("AFAQ:"))
async def cb_afaq(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    fid = int(call.data[5:])
    f   = db().execute("SELECT * FROM faqs WHERE id=?", (fid,)).fetchone()
    if not f: return
    b = InlineKeyboardBuilder()
    b.button(text="🗑 O'chirish", callback_data=f"FAQ_DEL:{fid}")
    b.button(text="◀️ Orqaga",   callback_data="AFAQ_BACK")
    b.adjust(1)
    try:
        await call.message.edit_text(f"{f['q']}\n\n{f['a']}", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"{f['q']}\n\n{f['a']}", reply_markup=b.as_markup())

@dp.callback_query(F.data.startswith("FAQ_DEL:"))
async def cb_faq_del(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    fid = int(call.data[8:])
    c = db(); c.execute("DELETE FROM faqs WHERE id=?", (fid,)); c.commit(); c.close()
    await call.answer("O'chirildi!", show_alert=True)
    faqs = get_faqs()
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f['q'][:35], callback_data=f"AFAQ:{f['id']}")
    b.button(text="➕ Qo'shish", callback_data="FAQ_ADD")
    b.adjust(1)
    try:
        await call.message.edit_text(f"FAQ ({len(faqs)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"FAQ ({len(faqs)} ta):", reply_markup=b.as_markup())

@dp.callback_query(F.data == "AFAQ_BACK")
async def cb_afaq_back(call: types.CallbackQuery):
    faqs = get_faqs()
    b = InlineKeyboardBuilder()
    for f in faqs:
        b.button(text=f['q'][:35], callback_data=f"AFAQ:{f['id']}")
    b.button(text="➕ Qo'shish", callback_data="FAQ_ADD")
    b.adjust(1)
    try:
        await call.message.edit_text(f"FAQ ({len(faqs)} ta):", reply_markup=b.as_markup())
    except:
        await call.message.answer(f"FAQ ({len(faqs)} ta):", reply_markup=b.as_markup())

# ── Start xabar ──
@dp.message(F.text == "✉️ Start xabar")
async def h_start_msg(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="📝 Matn o'zgartirish", callback_data="STMSG_TEXT")
    b.button(text="🖼 Rasm o'zgartirish", callback_data="STMSG_PHOTO")
    b.button(text="🗑 Rasmni o'chirish",  callback_data="STMSG_DEL_PHOTO")
    b.button(text="👁 Ko'rish",           callback_data="STMSG_PREVIEW")
    b.adjust(2, 2)
    cur_text  = gcfg("start_text") or "Kiritilmagan"
    cur_photo = "✅ Bor" if gcfg("start_photo") else "❌ Yo'q"
    await msg.answer(f"Start xabar\n\nMatn: {cur_text[:60]}\nRasm: {cur_photo}", reply_markup=b.as_markup())

@dp.callback_query(F.data == "STMSG_TEXT")
async def cb_stmsg_text(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Yangi start matnini kiriting (HTML formatda):", reply_markup=kb_back())
    await state.set_state(AdmS.start_msg)

@dp.message(AdmS.start_msg)
async def adm_start_msg(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    scfg("start_text", msg.html_text or msg.text)
    await state.clear()
    await msg.answer("✅ Start matni saqlandi!", reply_markup=kb_admin())

@dp.callback_query(F.data == "STMSG_PHOTO")
async def cb_stmsg_photo(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Rasm yuboring:", reply_markup=kb_back())
    await state.set_state(AdmS.start_photo_st)

@dp.message(AdmS.start_photo_st)
async def adm_start_photo(msg: types.Message, state: FSMContext):
    if msg.text == "Orqaga":
        await state.clear(); await msg.answer("Admin panel:", reply_markup=kb_admin()); return
    if not msg.photo:
        await msg.answer("Rasm yuboring!"); return
    scfg("start_photo", msg.photo[-1].file_id)
    await state.clear()
    await msg.answer("✅ Rasm saqlandi!", reply_markup=kb_admin())

@dp.callback_query(F.data == "STMSG_DEL_PHOTO")
async def cb_stmsg_del_photo(call: types.CallbackQuery):
    scfg("start_photo", "")
    await call.answer("✅ Rasm o'chirildi!", show_alert=True)

@dp.callback_query(F.data == "STMSG_PREVIEW")
async def cb_stmsg_preview(call: types.CallbackQuery):
    txt   = gcfg("start_text") or "Botga xush kelibsiz!"
    photo = gcfg("start_photo")
    if photo:
        await call.message.answer_photo(photo, caption=txt, parse_mode="HTML")
    else:
        await call.message.answer(txt, parse_mode="HTML")

# ── Buyurtma status (admin) ──
@dp.callback_query(F.data.startswith("ADCMP:"))
async def cb_adcmp(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[6:])
    c = db()
    row = c.execute("SELECT uid FROM orders WHERE id=?", (oid,)).fetchone()
    c.execute("UPDATE orders SET status='Bajarildi' WHERE id=?", (oid,)); c.commit(); c.close()
    try:
        await call.message.edit_text(f"✅ #{oid} bajarildi!")
    except:
        await call.answer("✅ Bajarildi!", show_alert=True)
    if row:
        try: await bot.send_message(row[0], f"✅ #{oid} buyurtmangiz bajarildi!")
        except: pass

@dp.callback_query(F.data.startswith("ADCANC:"))
async def cb_adcanc(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS: return
    oid = int(call.data[7:])
    c   = db()
    row = c.execute("SELECT uid,price FROM orders WHERE id=?", (oid,)).fetchone()
    if row:
        c.execute("UPDATE orders SET status='Bekor qilindi' WHERE id=?", (oid,))
        c.execute("UPDATE users SET balance=balance+? WHERE id=?", (row[1], row[0]))
        c.commit()
    c.close()
    try:
        await call.message.edit_text(f"❌ #{oid} bekor qilindi!")
    except:
        await call.answer("❌ Bekor qilindi!", show_alert=True)
    if row:
        try: await bot.send_message(row[0], f"❌ #{oid} bekor qilindi. {row[1]:,} So'm qaytarildi.")
        except: pass

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
async def main():
    init_db()
    logging.info("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
