import os
import requests
import time

TOKEN = "8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o"
ADMIN = "8537782289"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        import json
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(f"{API_URL}/sendMessage", data=data)
        return r.json()
    except:
        pass

def answer_callback(callback_id, text, show_alert=False):
    try:
        requests.post(f"{API_URL}/answerCallbackQuery", data={
            "callback_query_id": callback_id,
            "text": text,
            "show_alert": show_alert
        })
    except:
        pass

def delete_message(chat_id, message_id):
    try:
        requests.post(f"{API_URL}/deleteMessage", data={
            "chat_id": chat_id,
            "message_id": message_id
        })
    except:
        pass

def get_file(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return default

def put_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(content))
    except:
        pass

def del_file(path):
    try:
        os.remove(path)
    except:
        pass

def make_dirs():
    dirs = [
        "foydalanuvchi", "foydalanuvchi/hisob", "foydalanuvchi/referal",
        "foydalanuvchi/sarmoya", "foydalanuvchi/sarhisob",
        "sozlamalar/hamyon", "sozlamalar/kanal", "sozlamalar/tugma",
        "sozlamalar/xizmat", "sozlamalar/xizmatlar", "sozlamalar/bot",
        "sozlamalar/pul", "statistika", "nak", "otkazma", "botlar",
        "step", "baza", "ban", "status"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def init_files(fid):
    defaults = {
        f"foydalanuvchi/hisob/{fid}.txt": "0",
        f"foydalanuvchi/hisob/{fid}.1.txt": "0",
        f"foydalanuvchi/hisob/{fid}.1txt": "0",
        f"foydalanuvchi/referal/{fid}.txt": "0",
        f"foydalanuvchi/sarmoya/{fid}/sarson.txt": "0",
        f"foydalanuvchi/sarhisob/{fid}.kiritgan": "0",
        f"foydalanuvchi/sarhisob/{fid}.chiqargan": "0",
        f"otkazma/{fid}.idraqam": "",
        f"otkazma/{fid}.pulraqam": "",
        "sozlamalar/pul/referal.txt": "100",
        "sozlamalar/pul/valyuta.txt": "so'm",
        "sozlamalar/tugma/tugma1.txt": "Botlarni boshqarish",
        "sozlamalar/tugma/tugma2.txt": "Kabinet",
        "sozlamalar/tugma/tugma3.txt": "Pul ishlash",
        "sozlamalar/tugma/tugma4.txt": "Murojaat",
        "sozlamalar/tugma/tugma5.txt": "Bot do'koni",
        "sozlamalar/tugma/tugma6.txt": "Buyurtma berish",
        "sozlamalar/tugma/tugma7.txt": "Taklifnoma",
        "sozlamalar/kanal/ch.txt": "@Reliabledev",
        "statistika/obunachi.txt": "",
        "statistika/aktivbot.txt": "0",
        "statistika/hammabot.txt": "0",
        "baza/all.num": "0",
        "sozlamalar/holat.txt": "✅",
        "sozlamalar/api_kalit.txt": "",
        "sozlamalar/api_sayt.txt": "",
        "sozlamalar/bot/kategoriya.txt": "",
        "sozlamalar/hamyon/kategoriya.txt": "",
        "sozlamalar/xizmat/kategoriya.txt": "",
        "rek.narx": "500",
        "rek.kanal": "@Reliabledev",
        "admin.user": "@admin",
    }
    for path, val in defaults.items():
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
            put_file(path, val)
    os.makedirs(f"foydalanuvchi/sarmoya/{fid}", exist_ok=True)
    os.makedirs(f"foydalanuvchi/bot/{fid}", exist_ok=True)
    os.makedirs(f"nak/{fid}", exist_ok=True)
    if not os.path.exists(f"foydalanuvchi/bot/{fid}/bots.txt"):
        put_file(f"foydalanuvchi/bot/{fid}/bots.txt", "")

def joinchat(bot_token, user_id):
    kanallar = get_file("sozlamalar/kanal/ch.txt")
    if not kanallar:
        return True
    channels = [c.strip() for c in kanallar.split("\n") if c.strip()]
    all_joined = True
    keyboard = []
    for ch in channels:
        url = ch.replace("@", "")
        try:
            r = requests.get(f"https://api.telegram.org/bot{bot_token}/getChatMember",
                           params={"chat_id": ch, "user_id": user_id})
            status = r.json().get("result", {}).get("status", "")
            if status in ["creator", "administrator", "member"]:
                name = ch
                keyboard.append([{"text": f"✅ {name}", "url": f"https://t.me/{url}"}])
            else:
                name = ch
                keyboard.append([{"text": f"❌ {name}", "url": f"https://t.me/{url}"}])
                all_joined = False
        except:
            all_joined = False
    return all_joined, keyboard

def get_updates(offset=None):
    params = {"timeout": 30, "limit": 100}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []

def main_keyboard(fid):
    t1 = get_file("sozlamalar/tugma/tugma1.txt", "Botlarni boshqarish")
    t2 = get_file("sozlamalar/tugma/tugma2.txt", "Kabinet")
    t3 = get_file("sozlamalar/tugma/tugma3.txt", "Pul ishlash")
    t4 = get_file("sozlamalar/tugma/tugma4.txt", "Murojaat")
    t5 = get_file("sozlamalar/tugma/tugma5.txt", "Bot do'koni")
    is_admin = str(fid) == ADMIN
    kb = {
        "resize_keyboard": True,
        "keyboard": [
            [{"text": f"🤖 {t1}"}],
            [{"text": f"🗄 {t2}"}, {"text": f"💵 {t3}"}],
            [{"text": f"🛒 {t5}"}, {"text": f"☎️ {t4}"}],
            [{"text": "🛠️ Sozlamalar"}],
        ]
    }
    if is_admin:
        kb["keyboard"].append([{"text": "🗄 Boshqaruv"}])
    return kb

def nak_keyboard():
    t2 = get_file("sozlamalar/tugma/tugma2.txt", "Kabinet")
    t3 = get_file("sozlamalar/tugma/tugma3.txt", "Pul ishlash")
    t4 = get_file("sozlamalar/tugma/tugma4.txt", "Murojaat")
    return {
        "resize_keyboard": True,
        "keyboard": [
            [{"text": "📦 Buyurtma berish"}],
            [{"text": f"🗄 {t2}"}, {"text": f"💵 {t3}"}],
            [{"text": "📊 Buyurtma kuzatish"}, {"text": f"☎️ {t4}"}],
            [{"text": "🛠️ Sozlamalar"}],
        ]
    }

def admin_keyboard():
    return {
        "resize_keyboard": True,
        "keyboard": [
            [{"text": "⚙️ Asosiy sozlamalar"}],
            [{"text": "🎛 Tugmalar"}, {"text": "💳 Hamyonlar"}],
            [{"text": "🔎 Foydalanuvchini boshqarish"}],
            [{"text": "📨 Xabarnoma"}, {"text": "📊 Statistika"}],
            [{"text": "🔙 Orqaga"}],
        ]
    }

def process_message(update):
    import json

    make_dirs()

    msg = update.get("message") or {}
    cb = update.get("callback_query") or {}

    # Message info
    cid = msg.get("chat", {}).get("id", 0) if msg else 0
    fid = msg.get("from", {}).get("id", 0) if msg else 0
    text = msg.get("text", "") if msg else ""
    name = msg.get("from", {}).get("first_name", "") if msg else ""
    mid = msg.get("message_id", 0) if msg else 0

    # Callback info
    data = cb.get("data", "") if cb else ""
    callid = cb.get("id", "") if cb else ""
    ccid = cb.get("message", {}).get("chat", {}).get("id", 0) if cb else 0
    cmid = cb.get("message", {}).get("message_id", 0) if cb else 0
    callfrid = cb.get("from", {}).get("id", 0) if cb else 0

    active_id = cid or ccid

    if active_id:
        init_files(active_id)

    pul = get_file("sozlamalar/pul/valyuta.txt", "so'm")
    taklifpul = get_file("sozlamalar/pul/referal.txt", "100")
    asosiy = get_file(f"foydalanuvchi/hisob/{cid}.txt", "0")
    sar = get_file(f"foydalanuvchi/hisob/{cid}.1txt", "0")
    kiritgan = get_file(f"foydalanuvchi/hisob/{cid}.1.txt", "0")
    userstep = get_file(f"step/{cid}.txt", "")
    holat = get_file("sozlamalar/holat.txt", "✅")

    # Ban check
    if text:
        ban = get_file(f"ban/{cid}.txt", "")
        if ban == "ban":
            return
    if data:
        ban = get_file(f"ban/{ccid}.txt", "")
        if ban == "ban":
            return

    # Bot holat check
    if text and holat == "❌" and str(cid) != ADMIN:
        send_message(cid, "⛔️ <b>Bot vaqtinchalik o'chirilgan!</b>\n\n<i>⚙️ Botda ta'mirlash ishlari olib borilayotgan!</i>")
        return
    if data and holat == "❌" and str(ccid) != ADMIN:
        answer_callback(callid, "⛔️ Bot vaqtinchalik o'chirilgan!", show_alert=True)
        return

    # Register user
    if msg:
        statistika = get_file("statistika/obunachi.txt", "")
        if str(fid) not in statistika:
            put_file("statistika/obunachi.txt", statistika + f"\n{fid}" if statistika else str(fid))
            send_message(ADMIN, f"<b>👤 Yangi a'zo\n✉️ Lichka:</b> <a href='tg://user?id={fid}'>{name}</a>")

    # /start
    if text == "/start":
        if str(cid) == ADMIN:
            send_message(cid, "<b>🖥 Asosiy menyudasiz</b>", reply_markup=main_keyboard(cid))
        else:
            send_message(cid, "<b>🖥 Asosiy menyudasiz</b>", reply_markup=main_keyboard(cid))
        return

    # /start referal
    if text and text.startswith("/start "):
        ref = text.split(" ")[1] if len(text.split(" ")) > 1 else ""
        if ref and ref != str(cid):
            idref_path = f"foydalanuvchi/referal/{ref}.db"
            idref2 = get_file(idref_path, "")
            if str(cid) not in idref2:
                with open(idref_path, "a") as f:
                    f.write(f"{cid}\n")
                pulim = int(get_file(f"foydalanuvchi/hisob/{ref}.txt", "0"))
                put_file(f"foydalanuvchi/hisob/{ref}.txt", pulim + int(taklifpul))
                odam = int(get_file(f"foydalanuvchi/referal/{ref}.txt", "0"))
                put_file(f"foydalanuvchi/referal/{ref}.txt", odam + 1)
                send_message(ref, f"<b>📳 Sizda yangi <a href='tg://user?id={cid}'>taklif</a> mavjud!</b>\n\n<i>Hisobingizga {taklifpul} {pul} qo'shildi!</i>")
        send_message(cid, "<b>🖥 Asosiy menyudasiz</b>", reply_markup=main_keyboard(cid))
        return

    # /panel
    if text == "/panel" and str(cid) == ADMIN:
        send_message(cid, "<b>🗄 Boshqaruv paneliga xush kelibsiz!</b>", reply_markup=admin_keyboard())
        return

    # Boshqaruv
    if text == "🗄 Boshqaruv" and str(cid) == ADMIN:
        send_message(cid, "<b>🗄 Boshqaruv paneliga xush kelibsiz!</b>", reply_markup=admin_keyboard())
        del_file(f"step/{cid}.txt")
        return

    # Orqaga
    if text == "🔙 Orqaga":
        send_message(cid, "Menu tanlang", reply_markup={
            "inline_keyboard": [
                [{"text": "📦 Nakrutka Bo'lim", "callback_data": "nak_menu"}],
                [{"text": "🤖 Maker Bo'lim", "callback_data": "mak_menu"}],
            ]
        })
        return

    if text == "🔚 Orqaga" or text == "⬅️ Orqaga":
        send_message(cid, "<b>🔚 Orqaga qaytingiz</b>", reply_markup=main_keyboard(cid))
        del_file(f"step/{cid}.txt")
        return

    # Sozlamalar
    if text == "🛠️ Sozlamalar":
        send_message(cid, "<b>Menulardan birini tanlang</b>", reply_markup={
            "inline_keyboard": [
                [{"text": "📦 Nakrutka Bo'lim", "callback_data": "nak_menu"}],
                [{"text": "🤖 Maker Bo'lim", "callback_data": "mak_menu"}],
            ]
        })
        return

    # Kabinet
    t2 = get_file("sozlamalar/tugma/tugma2.txt", "Kabinet")
    if text and t2 in text:
        odam = get_file(f"foydalanuvchi/referal/{cid}.txt", "0")
        send_message(cid, f"<b>🔎 ID raqamingiz:</b> <code>{cid}</code>\n\n<b>💵 Asosiy balans:</b> {asosiy} {pul}\n<b>🏦 Qo'shimcha balans:</b> {sar} {pul}\n<b>🔗 Takliflaringiz:</b> {odam} ta\n\n<b>💳 Botga kiritgan pullaringiz:</b> {kiritgan} {pul}", reply_markup={
            "inline_keyboard": [
                [{"text": "🔁 O'tkazmalar", "callback_data": "puliz"}],
                [{"text": "💳 Hisobni to'ldirish", "callback_data": "oplata"}],
            ]
        })
        return

    # Pul ishlash
    t3 = get_file("sozlamalar/tugma/tugma3.txt", "Pul ishlash")
    if text and t3 in text:
        t7 = get_file("sozlamalar/tugma/tugma7.txt", "Taklifnoma")
        send_message(cid, "<b>📋 Quyidagilardan birini tanlang:</b>", reply_markup={
            "inline_keyboard": [
                [{"text": f"🔗 {t7}", "callback_data": "taklifnoma"}],
            ]
        })
        return

    # Murojaat
    t4 = get_file("sozlamalar/tugma/tugma4.txt", "Murojaat")
    if text and t4 in text:
        send_message(cid, "<b>📝 Murojaat matnini yuboring:</b>", reply_markup={
            "resize_keyboard": True,
            "keyboard": [[{"text": "🔙 Orqaga"}]]
        })
        put_file(f"step/{cid}.txt", "murojat")
        return

    # Murojat step
    if userstep == "murojat":
        if text == "🔙 Orqaga":
            del_file(f"step/{cid}.txt")
        else:
            put_file(f"step/{cid}.murojat", str(cid))
            murojat = get_file(f"step/{cid}.murojat")
            send_message(ADMIN, f"<b>📨 Yangi murojat keldi:</b> {murojat}\n\n<b>📑 Murojat matni:</b> {text}", reply_markup={
                "inline_keyboard": [[{"text": "💌 Javob yozish", "callback_data": f"yozish={murojat}"}]]
            })
            del_file(f"step/{cid}.txt")
            send_message(cid, "<b>✅ Murojaatingiz yuborildi.</b>\n\n<i>Tez orada javob qaytaramiz!</i>", reply_markup=main_keyboard(cid))
        return

    # Javob step
    if userstep == "javob":
        if text == "🔙 Orqaga":
            del_file(f"step/{cid}.txt")
            del_file(f"step/{cid}.javob")
        else:
            murojat = get_file(f"step/{cid}.javob")
            send_message(murojat, f"<b>☎️ Administrator:</b>\n\n<i>{text}</i>", reply_markup={
                "inline_keyboard": [[{"text": "Javob yozish", "callback_data": "boglanish"}]]
            })
            send_message(cid, "<b>Javob yuborildi</b>", reply_markup=admin_keyboard())
            del_file(f"step/{cid}.txt")
            del_file(f"step/{cid}.javob")
        return

    # Statistika (admin)
    if text == "📊 Statistika" and str(cid) == ADMIN:
        statistika = get_file("statistika/obunachi.txt", "")
        lich = len([x for x in statistika.split("\n") if x.strip()])
        aktivbot = get_file("statistika/aktivbot.txt", "0")
        hammabot = get_file("statistika/hammabot.txt", "0")
        send_message(cid, f"📈 <b>Aktiv botlar: {aktivbot} ta</b>\n📊 <b>Yaratilgan botlar: {hammabot} ta</b>\n👥 <b>Foydalanuvchilar: {lich} ta</b>", reply_markup={
            "inline_keyboard": [
                [{"text": "🔁 Yangilash", "callback_data": "stats"}],
                [{"text": "📊 Hisoblar", "callback_data": "hisob"}, {"text": "📊 Do'stlar", "callback_data": "dostlar"}],
            ]
        })
        return

    # Xabarnoma (admin)
    if text == "📨 Xabarnoma" and str(cid) == ADMIN:
        send_message(cid, "<b>📨 Yuboriladigan xabar turini tanlang:</b>", reply_markup={
            "inline_keyboard": [
                [{"text": "Oddiy xabar", "callback_data": "oddiy_xabar"}],
                [{"text": "Forward xabar", "callback_data": "forward_xabar"}],
            ]
        })
        return

    # Oddiy xabar yuborish
    oddiy = get_file("oddiy.txt", "")
    if oddiy == "oddiy" and str(cid) == ADMIN:
        if text == "🗄 Boshqaruv":
            del_file("oddiy.txt")
        else:
            statistika = get_file("statistika/obunachi.txt", "")
            users = [x.strip() for x in statistika.split("\n") if x.strip()]
            for u in users:
                send_message(u, text)
            del_file("oddiy.txt")
            send_message(cid, f"<b>{len(users)} ta foydalanuvchiga muvaffaqiyatli yuborildi</b>", reply_markup=admin_keyboard())
        return

    # Foydalanuvchi boshqarish
    if text == "🔎 Foydalanuvchini boshqarish" and str(cid) == ADMIN:
        send_message(cid, "<b>Kerakli foydalanuvchining ID raqamini yuboring:</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🗄 Boshqaruv"}]]
        })
        put_file("fbsh.txt", "idraqam")
        return

    fbsh = get_file("fbsh.txt", "")
    if fbsh == "idraqam" and str(cid) == ADMIN:
        if text == "🗄 Boshqaruv":
            del_file("fbsh.txt")
        else:
            tx = text.strip()
            if os.path.exists(f"foydalanuvchi/hisob/{tx}.txt"):
                put_file("step/odam.txt", tx)
                asos = get_file(f"foydalanuvchi/hisob/{tx}.txt", "0")
                tpul = get_file(f"foydalanuvchi/hisob/{tx}.1txt", "0")
                kirit = get_file(f"foydalanuvchi/hisob/{tx}.1.txt", "0")
                odam = get_file(f"foydalanuvchi/referal/{tx}.txt", "0")
                is_banned = get_file(f"ban/{tx}.txt", "") == "ban"
                ban_btn = "🔕 Bandan olish" if is_banned else "🔔 Banlash"
                ban_cb = "unban" if is_banned else "ban"
                send_message(cid, f"<b>✅ Foydalanuvchi topildi:</b> <a href='tg://user?id={tx}'>{tx}</a>\n\n<b>Asosiy balans:</b> {asos} {pul}\n<b>Sarmoya balans:</b> {tpul} {pul}\n<b>Takliflari:</b> {odam} ta\n\n<b>Kiritgan pullari:</b> {kirit} {pul}", reply_markup={
                    "inline_keyboard": [
                        [{"text": ban_btn, "callback_data": ban_cb}],
                        [{"text": "➕ Pul qo'shish", "callback_data": "val_qoshish"}, {"text": "➖ Pul ayirish", "callback_data": "val_ayirish"}],
                    ]
                })
                del_file("fbsh.txt")
            else:
                send_message(cid, "<b>Ushbu foydalanuvchi botdan foydalanmaydi!</b>")
        return

    # Perevodid step
    if userstep == "perevodid" and text != "🔙 Orqaga":
        put_file(f"otkazma/{cid}.idraqam", text)
        del_file(f"step/{cid}.txt")
        send_message(cid, f"<b>Qancha mablag'ingizni o'tkazmoqchisiz?\n\nHisobingiz:</b> {asosiy} {pul}", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🔙 Orqaga"}]]
        })
        put_file(f"step/{cid}.txt", "perevodid1")
        return

    if userstep == "perevodid1" and text != "🔙 Orqaga":
        raqamid = get_file(f"otkazma/{cid}.idraqam")
        try:
            tx_val = int(text)
            olmos1 = int(get_file(f"foydalanuvchi/hisob/{raqamid}.txt", "0"))
            olmos2 = int(get_file(f"foydalanuvchi/hisob/{cid}.txt", "0"))
            if olmos2 >= tx_val and tx_val > 0:
                put_file(f"foydalanuvchi/hisob/{raqamid}.txt", olmos1 + tx_val)
                put_file(f"foydalanuvchi/hisob/{cid}.txt", olmos2 - tx_val)
                send_message(raqamid, f"<b>Hisobingizga</b> <a href='tg://user?id={cid}'>{cid}</a><b> tomonidan {text} {pul} o'tkazdi.</b>")
                send_message(cid, "<b>✅ O'tkazma muvaffaqiyatli amalga oshirildi!</b>")
            else:
                send_message(cid, "<b>⚠️ Hisobingizda mablag' yetarli emas!</b>")
        except:
            send_message(cid, "<b>⚠️ Noto'g'ri miqdor!</b>")
        del_file(f"step/{cid}.txt")
        return

    # Oplata step
    if userstep == "oplata":
        if text == "🔙 Orqaga":
            del_file(f"step/{cid}.txt")
        else:
            put_file(f"step/hisob.{cid}", text)
            send_message(cid, "<b>To'lovingizni chek yoki skreenshotini shu yerga yuboring:</b>")
            put_file(f"step/{cid}.txt", "rasm")
        return

    # Rasm step
    if userstep == "rasm":
        if text == "🔙 Orqaga":
            del_file(f"step/{cid}.txt")
        else:
            photo = msg.get("photo", [])
            if photo:
                file_id = photo[-1]["file_id"]
                hisob_sum = get_file(f"step/hisob.{fid}", "0")
                del_file(f"step/{fid}.txt")
                send_message(cid, "*Hisobni to'ldirganingiz haqida ma'lumot asosiy adminga yuborildi.*", parse_mode="MarkDown", reply_markup=main_keyboard(cid))
                import json
                requests.post(f"{API_URL}/sendPhoto", data={
                    "chat_id": ADMIN,
                    "photo": file_id,
                    "caption": f"📄 <b>Foydalanuvchidan check:\n\n👮 Foydalanuvchi:</b> <a href='tg://user?id={cid}'>{name}</a>\n🔎 <b>ID:</b> {fid}\n💵 <b>To'lov miqdori:</b> {hisob_sum} {pul}",
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps({
                        "inline_keyboard": [
                            [{"text": "✅ Hisobini to'ldirish", "callback_data": f"on={fid}"}],
                            [{"text": "❌ Bekor qilish", "callback_data": f"off={fid}"}],
                        ]
                    })
                })
        return

    # Buyurtma kuzatish
    okstat = get_file(f"status/{cid}.status", "")
    if text == "📊 Buyurtma kuzatish":
        send_message(cid, "*🆔 Buyurtma ID sini kiriting:*", parse_mode="MarkDown", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "⬅️ Orqaga"}]]
        })
        put_file(f"status/{cid}.status", "1")
        return

    if okstat == "1" and text and text.isdigit():
        api_kalit = get_file("sozlamalar/api_kalit.txt")
        api_sayt = get_file("sozlamalar/api_sayt.txt")
        try:
            r = requests.get(f"https://{api_sayt}/api/v2", params={"key": api_kalit, "action": "status", "order": text})
            result = r.json()
            xolat = result.get("status", "")
            miqdor = result.get("remains", "")
            if xolat:
                send_message(cid, f"*\n🆔 Buyurtma idsi: {text}\n🔎 Buyurtmangiz: {xolat}\n🔢 Qoldiq miqdori: {miqdor} ta*", parse_mode="MarkDown", reply_markup=main_keyboard(cid))
            else:
                send_message(cid, "*🤷 Mavjud emas!*", parse_mode="MarkDown")
        except:
            send_message(cid, "*Xatolik yuz berdi!*", parse_mode="MarkDown")
        del_file(f"status/{cid}.status")
        return

    # Val qoshish step
    valqosh = get_file("valqosh.txt", "")
    if valqosh == "valqosh" and str(cid) == ADMIN:
        if text == "🗄 Boshqaruv":
            del_file("valqosh.txt")
            del_file("step/odam.txt")
        else:
            saved = get_file("step/odam.txt")
            try:
                tx_val = int(text)
                get_val = int(get_file(f"foydalanuvchi/hisob/{saved}.txt", "0"))
                currency = int(get_file(f"foydalanuvchi/hisob/{saved}.1.txt", "0"))
                put_file(f"foydalanuvchi/hisob/{saved}.txt", get_val + tx_val)
                put_file(f"foydalanuvchi/hisob/{saved}.1.txt", currency + tx_val)
                send_message(saved, f"<b>Adminlar tomonidan hisobingiz {text} {pul} to'ldirildi</b>")
                send_message(cid, f"<b>Foydalanuvchi hisobiga {text} {pul} qo'shildi</b>", reply_markup=admin_keyboard())
            except:
                pass
            del_file("valqosh.txt")
            del_file("step/odam.txt")
        return

    # Val ayirish step
    valayir = get_file("valayir.txt", "")
    if valayir == "valayir" and str(cid) == ADMIN:
        if text == "🗄 Boshqaruv":
            del_file("valayir.txt")
            del_file("step/odam.txt")
        else:
            saved = get_file("step/odam.txt")
            try:
                tx_val = int(text)
                get_val = int(get_file(f"foydalanuvchi/hisob/{saved}.txt", "0"))
                put_file(f"foydalanuvchi/hisob/{saved}.txt", get_val - tx_val)
                send_message(saved, f"<b>Adminlar tomonidan hisobingizdan {text} {pul} olib tashlandi</b>")
                send_message(cid, f"<b>Foydalanuvchi hisobidan {text} {pul} olib tashlandi</b>", reply_markup=admin_keyboard())
            except:
                pass
            del_file("valayir.txt")
            del_file("step/odam.txt")
        return

    # Callback queries
    if data == "nak_menu":
        delete_message(ccid, cmid)
        send_message(ccid, "<b>🗄 Nakrutka bo'limiga xush kelibsiz!</b>", reply_markup=nak_keyboard())
        return

    if data == "mak_menu":
        delete_message(ccid, cmid)
        send_message(ccid, "<b>🗄 Maker bo'limiga xush kelibsiz!</b>", reply_markup=main_keyboard(ccid))
        return

    if data == "stats" and str(ccid) == ADMIN:
        statistika = get_file("statistika/obunachi.txt", "")
        lich = len([x for x in statistika.split("\n") if x.strip()])
        aktivbot = get_file("statistika/aktivbot.txt", "0")
        hammabot = get_file("statistika/hammabot.txt", "0")
        delete_message(ccid, cmid)
        send_message(ccid, f"📈 <b>Aktiv botlar: {aktivbot} ta</b>\n📊 <b>Yaratilgan botlar: {hammabot} ta</b>\n👥 <b>Foydalanuvchilar: {lich} ta</b>", reply_markup={
            "inline_keyboard": [
                [{"text": "🔁 Yangilash", "callback_data": "stats"}],
                [{"text": "📊 Hisoblar", "callback_data": "hisob"}, {"text": "📊 Do'stlar", "callback_data": "dostlar"}],
            ]
        })
        return

    if data == "oddiy_xabar" and str(ccid) == ADMIN:
        statistika = get_file("statistika/obunachi.txt", "")
        lich = len([x for x in statistika.split("\n") if x.strip()])
        delete_message(ccid, cmid)
        send_message(ccid, f"<b>{lich} ta foydalanuvchiga yuboriladigan xabar matnini yuboring:</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🗄 Boshqaruv"}]]
        })
        put_file("oddiy.txt", "oddiy")
        return

    if data == "taklifnoma":
        odam = get_file(f"foydalanuvchi/referal/{ccid}.txt", "0")
        botname_r = requests.get(f"{API_URL}/getMe")
        botname = botname_r.json().get("result", {}).get("username", "")
        delete_message(ccid, cmid)
        send_message(ccid, f"<b>🔗 Sizning taklif havolangiz:</b>\n\n<code>https://t.me/{botname}?start={ccid}</code>\n\n<b>1 ta taklif uchun {taklifpul} so'm beriladi\n\nSizning takliflaringiz: {odam} ta</b>", reply_markup={
            "inline_keyboard": [
                [{"text": "👥 Do'stlarga yuborish", "url": f"https://t.me/share/url?url=https://t.me/{botname}?start={ccid}"}],
                [{"text": "🔚 Orqaga", "callback_data": "orqaga3"}],
            ]
        })
        return

    if data == "orqaga3":
        t7 = get_file("sozlamalar/tugma/tugma7.txt", "Taklifnoma")
        delete_message(ccid, cmid)
        send_message(ccid, "<b>📋 Quyidagilardan birini tanlang:</b>", reply_markup={
            "inline_keyboard": [[{"text": f"🔗 {t7}", "callback_data": "taklifnoma"}]]
        })
        return

    if data == "oplata":
        kategoriya2 = get_file("sozlamalar/hamyon/kategoriya.txt", "")
        if not kategoriya2.strip():
            answer_callback(callid, "⚠️ To'lov tizimlari qo'shilmagan!", show_alert=True)
            return
        items = [x.strip() for x in kategoriya2.split("\n") if x.strip()]
        keys = [[{"text": item, "callback_data": f"karta-{item}"}] for item in items]
        keys.append([{"text": "◀️ Orqaga", "callback_data": "orqaga12"}])
        import json
        requests.post(f"{API_URL}/editMessageText", data={
            "chat_id": ccid, "message_id": cmid,
            "text": "<b>💳 Quyidagi to'lov tizimlaridan birini tanlang:</b>",
            "parse_mode": "HTML",
            "reply_markup": json.dumps({"inline_keyboard": keys})
        })
        return

    if data and data.startswith("karta-"):
        kat = data.split("karta-")[1]
        raqam = get_file(f"sozlamalar/hamyon/{kat}/raqam.txt", "")
        import json
        requests.post(f"{API_URL}/editMessageText", data={
            "chat_id": ccid, "message_id": cmid,
            "text": f"<b>📲 To'lov turi:</b> <u>{kat}</u>\n\n💳 Karta: <code>{raqam}</code>\n📝 Izoh: #ID{ccid}\n\n1) Istalgan pul miqdorini tepadagi hamyonga tashlang\n2) «✅ To'lov qildim» tugmasini bosing\n3) To'lov haqidagi suratni botga yuboring\n4) Operator tomonidan tasdiqlanishini kuting!",
            "parse_mode": "HTML",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "✅ To'lov qildim", "callback_data": "tolov"}],
                [{"text": "◀️ Orqaga", "callback_data": "oplata"}],
            ]})
        })
        return

    if data == "tolov":
        delete_message(ccid, cmid)
        send_message(ccid, "<b>To'lov miqdorini kiriting:</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🔙 Orqaga"}]]
        })
        put_file(f"step/{ccid}.txt", "oplata")
        return

    if data == "puliz":
        delete_message(ccid, cmid)
        send_message(ccid, "<b>Kerakli foydalanuvchi ID raqamini yuboring:</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🔙 Orqaga"}]]
        })
        put_file(f"step/{ccid}.txt", "perevodid")
        return

    if data == "orqaga12":
        hisob_v = get_file(f"foydalanuvchi/hisob/{ccid}.txt", "0")
        kiritgan_v = get_file(f"foydalanuvchi/hisob/{ccid}.1.txt", "0")
        sar_v = get_file(f"foydalanuvchi/hisob/{ccid}.1txt", "0")
        odam_v = get_file(f"foydalanuvchi/referal/{ccid}.txt", "0")
        delete_message(ccid, cmid)
        send_message(ccid, f"<b>🔎 ID raqamingiz:</b> <code>{ccid}</code>\n\n<b>💵 Asosiy balans:</b> {hisob_v} {pul}\n<b>🏦 Qo'shimcha balans:</b> {sar_v} {pul}\n<b>🔗 Takliflaringiz:</b> {odam_v} ta\n\n<b>💳 Botga kiritgan pullaringiz:</b> {kiritgan_v} {pul}", reply_markup={
            "inline_keyboard": [
                [{"text": "🔁 O'tkazmalar", "callback_data": "puliz"}],
                [{"text": "💳 Hisobni to'ldirish", "callback_data": "oplata"}],
            ]
        })
        return

    if data and data.startswith("on="):
        odam_id = data.split("=")[1]
        delete_message(ccid, cmid)
        hisob_sum = get_file(f"step/hisob.{odam_id}", "0")
        try:
            get_v = int(get_file(f"foydalanuvchi/hisob/{odam_id}.txt", "0"))
            currency_v = int(get_file(f"foydalanuvchi/hisob/{odam_id}.1.txt", "0"))
            put_file(f"foydalanuvchi/hisob/{odam_id}.txt", get_v + int(hisob_sum))
            put_file(f"foydalanuvchi/hisob/{odam_id}.1.txt", currency_v + int(hisob_sum))
        except:
            pass
        send_message(odam_id, f"<b>Hisobingiz {hisob_sum} {pul} ga to'ldirildi</b>")
        send_message(ccid, f"<b>Foydalanuvchi hisobi {hisob_sum} {pul} ga to'ldirildi</b>")
        del_file(f"step/hisob.{odam_id}")
        return

    if data and data.startswith("off="):
        odam_id = data.split("=")[1]
        delete_message(ccid, cmid)
        hisob_sum = get_file(f"step/hisob.{odam_id}", "0")
        send_message(odam_id, f"<b>Hisobingizni {hisob_sum} {pul} ga to'ldirish bekor qilindi</b>")
        send_message(ccid, "<b>Foydalanuvchi cheki bekor qilindi</b>")
        del_file(f"step/hisob.{odam_id}")
        return

    if data == "ban":
        saved = get_file("step/odam.txt")
        put_file(f"ban/{saved}.txt", "ban")
        delete_message(ccid, cmid)
        send_message(ccid, f"<a href='tg://user?id={saved}'>{saved}</a> <b>banlandi</b>", reply_markup=admin_keyboard())
        send_message(saved, "<b>Admin tomonidan bloklandingiz!</b>")
        del_file("step/odam.txt")
        return

    if data == "unban":
        saved = get_file("step/odam.txt")
        del_file(f"ban/{saved}.txt")
        delete_message(ccid, cmid)
        send_message(ccid, f"<a href='tg://user?id={saved}'>{saved}</a> <b>banlandan olindi</b>", reply_markup=admin_keyboard())
        send_message(saved, "<b>Admin tomonidan blokdan olindingiz!</b>")
        del_file("step/odam.txt")
        return

    if data == "val_qoshish" and str(ccid) == ADMIN:
        saved = get_file("step/odam.txt")
        put_file("valqosh.txt", "valqosh")
        delete_message(ccid, cmid)
        send_message(ccid, f"<a href='tg://user?id={saved}'>{saved}</a> <b>ning hisobiga qancha pul qo'shmoqchisiz?</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🗄 Boshqaruv"}]]
        })
        return

    if data == "val_ayirish" and str(ccid) == ADMIN:
        saved = get_file("step/odam.txt")
        put_file("valayir.txt", "valayir")
        delete_message(ccid, cmid)
        send_message(ccid, f"<a href='tg://user?id={saved}'>{saved}</a> <b>ning hisobidan qancha pul ayirmoqchisiz?</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🗄 Boshqaruv"}]]
        })
        return

    if data and data.startswith("yozish="):
        odam_id = data.split("=")[1]
        delete_message(ccid, cmid)
        send_message(ccid, "<b>Javob matnini yuboring:</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🔙 Orqaga"}]]
        })
        put_file(f"step/{ccid}.txt", "javob")
        put_file(f"step/{ccid}.javob", odam_id)
        return

    if data == "boglanish":
        delete_message(ccid, cmid)
        send_message(ccid, "<b>📝 Murojaat matnini yuboring:</b>", reply_markup={
            "resize_keyboard": True, "keyboard": [[{"text": "🔙 Orqaga"}]]
        })
        put_file(f"step/{ccid}.txt", "murojat")
        return

    answer_callback(callid, "") if callid else None


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                try:
                    process_message(update)
                except Exception as e:
                    print(f"Xato: {e}")
        except Exception as e:
            print(f"Connection xato: {e}")
            time.sleep(5)
