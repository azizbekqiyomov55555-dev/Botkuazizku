import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# =====================
# SOZLAMALAR
# =====================
BOT_TOKEN = "8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o"  # Tokeningiz
PRO_USERS = [8537782289]  # Pro foydalanuvchilar ID larini shu yerga yozing

# Foydalanuvchi holati (kutish)
waiting_users = {}

# =====================
# BOT VA DISPATCHER
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================
# SHARTNOMA MATNI
# =====================
contract_text = (
    "Soxta Chek Bot shartnomasi:\n\n"
    "1. Foydalanuvchi soxta chek yasash xizmatidan qonuniy maqsadda foydalanishni kafolatlaydi.\n"
    "2. Botda ko'rsatilgan ma'lumotlarning to'g'riligi uchun javobgarlik foydalanuvchida.\n"
    "3. Bot ishlab chiquvchisi nojo'ya foydalanish uchun mas'ul emas.\n\n"
    "Shartnomani qabul qilsangiz, «Qabul qilaman» tugmasini bosing."
)

# =====================
# /start BUYRUG'I
# =====================
@dp.message(CommandStart())
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Qabul qilaman", callback_data="contract_accept")],
        [InlineKeyboardButton(text="Qabul qilmayman", callback_data="contract_decline")]
    ])
    await message.answer(contract_text, reply_markup=keyboard)

# =====================
# SHARTNOMA QABUL QILINDI
# =====================
@dp.callback_query(F.data == "contract_accept")
async def contract_accept(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in PRO_USERS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Paynet Chek", callback_data="choose_paynet")]
        ])
        await callback.message.answer(
            "Shartnoma qabul qilindi.\n\nIltimos, ilovani tanlang:",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            "Siz PRO foydalanuvchi emassiz.\nChek yasash uchun @Dalishev_coder ga murojaat qiling."
        )
    await callback.answer()

# =====================
# SHARTNOMA RAD ETILDI
# =====================
@dp.callback_query(F.data == "contract_decline")
async def contract_decline(callback: CallbackQuery):
    await callback.message.answer("Siz shartnomani qabul qilmagansiz.\nChek yasash mumkin emas.")
    await callback.answer()

# =====================
# PAYNET TANLANDI
# =====================
@dp.callback_query(F.data == "choose_paynet")
async def choose_paynet(callback: CallbackQuery):
    user_id = callback.from_user.id
    waiting_users[user_id] = "paynet"
    await callback.message.answer(
        "Paynet tanlandi.\n\nQuyidagi formatda yuboring:\n\n"
        "40000\n"
        "Ism Familiya\n"
        "8600123456789012\n"
        "10:01"
    )
    await callback.answer()

# =====================
# CHEK MA'LUMOTLARINI QABUL QILISH
# =====================
@dp.message()
async def handle_chek_data(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in waiting_users:
        return

    lines = message.text.strip().split("\n")

    if len(lines) != 4:
        await message.answer(
            "Noto'g'ri format.\n\nMasalan:\n40000\nIsm Familiya\n8600123456789012\n10:01"
        )
        return

    summa, name, card, time = lines

    # Validatsiya
    if not summa.replace(" ", "").isdigit():
        await message.answer("Summa noto'g'ri.")
        return

    if not (12 <= len(card.strip()) <= 19 and card.strip().isdigit()):
        await message.answer("Karta raqami xato.")
        return

    import re
    if not re.match(r'^\d{2}:\d{2}$', time.strip()):
        await message.answer("Vaqt xato (HH:MM formatda).")
        return

    # API URL yaratish
    card_api = card.strip()
    name_api = name.strip()
    summa_api = summa.strip()
    time_api = time.strip()

    # ⚠️ API URL ni to'ldiring!
    api_url = f"https://YOUR_API_URL_HERE?karta={card_api}&ism={name_api}&summa={summa_api}&soat={time_api}"

    me = await bot.get_me()
    bot_username = f"@{me.username}"

    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=api_url,
            caption=f"Chek {bot_username} orqali yaratildi✅"
        )
    except Exception as e:
        await message.answer(f"Chek yuborishda xatolik: {e}")

    del waiting_users[user_id]

# =====================
# BOTNI ISHGA TUSHIRISH
# =====================
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
