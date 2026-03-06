# 🤖 SMM Nakrutka Bot (Uzbek)

## Xususiyatlar (Features)
- 🛒 Buyurtma berish (Telgram, Instgram, Tik tok, Youtube)
- 📦 Buyurtmalarni kuzatish
- 👤 Shaxsiy hisob
- 💰 Hisob to'ldirish (Click/Payme)
- 💵 Referal tizim (500 So'm/referal)
- 🆘 Admin bilan murojaat
- 📚 FAQ / Qo'llanma
- 🖥 To'liq Admin panel:
  - 📊 Statistika (TOP-50)
  - 👥 Foydalanuvchi boshqaruv (ban, pul qo'shish/ayirish)
  - 📝 Buyurtma boshqaruv
  - 🌐 Tarmoq/Bo'lim/Xizmat qo'shish
  - 📢 Broadcast xabar

## O'rnatish (Installation)

### 1. Python o'rnatish
```
Python 3.10+ kerak
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Bot tokenini olish
1. @BotFather ga boring
2. /newbot yozing
3. Bot nomini va username'ni kiriting
4. Token olasiz

### 4. Config sozlash
`bot.py` faylida quyidagi qatorlarni o'zgartiring:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # O'z tokeningizni yozing
ADMIN_IDS = [123456789]  # O'z Telegram ID'ingizni yozing
```

Yoki environment variable orqali:
```bash
export BOT_TOKEN="your_token_here"
export ADMIN_IDS="123456789"
```

### 5. Botni ishga tushirish
```bash
python bot.py
```

## Foydalanish

### Foydalanuvchi uchun:
1. `/start` - Botni ishga tushirish
2. **Buyurtma berish** - Yangi xizmat buyurtma qilish
3. **Buyurtmalar** - Buyurtmalarni ko'rish
4. **Hisobim** - Balans va ma'lumotlar
5. **Hisob to'ldirish** - Balans qo'shish
6. **Pul ishlash** - Referal havola olish

### Admin uchun:
1. **Boshqaruv** - Admin paneliga kirish
2. **Statistika** - Bot statistikasi
3. **Foydalanuvchilar** - ID bo'yicha qidirish va boshqarish
4. **Buyurtmalar** - Buyurtma holatini o'zgartirish
5. **Tarmoqlar** - Tarmoq/Bo'lim/Xizmat qo'shish
6. **Xabar yuborish** - Barcha foydalanuvchilarga broadcast

## Tarmoq va Xizmat qo'shish

1. Admin panelga kiring → **Tarmoqlar**
2. Tarmoq tanlang (yoki yangi qo'shing)
3. Bo'lim qo'shing
4. Xizmat qo'shing (API ID, nom, narx, min/max)

## Ma'lumotlar bazasi
SQLite ishlatiladi, `smm_bot.db` faylida saqlanadi.
