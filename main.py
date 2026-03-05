import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Railway'da xavfsizlik uchun tokenni Environment Variables (muhit o'zgaruvchilari) orqali olamiz
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- TUGMALAR (KEYBOARDS) ---

# Asosiy menyu tugmalari
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Buyurtma berish")],[KeyboardButton(text="Buyurtmalar"), KeyboardButton(text="Hisobim")],[KeyboardButton(text="Pul ishlash"), KeyboardButton(text="Hisob to'ldirish")],[KeyboardButton(text="Murojaat"), KeyboardButton(text="Qo'llanma")],
        [KeyboardButton(text="🗄 Boshqaruv")]
    ],
    resize_keyboard=True
)

# Orqaga qaytish menyusi
back_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Orqaga")]
    ],
    resize_keyboard=True
)

# --- BUYRUQLAR VA XABARLARNI QABUL QILISH ---

# /start buyrug'i uchun
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_menu)

# "Buyurtma berish" tugmasi bosilganda
@dp.message(F.text == "Buyurtma berish")
async def buyurtma_berish_handler(message: types.Message):
    await message.answer("📝 Yangi ijtimoiy tarmoq nomini kiriting:", reply_markup=back_menu)

# "Orqaga" tugmasi bosilganda
@dp.message(F.text == "Orqaga")
async def orqaga_handler(message: types.Message):
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_menu)

# Qolgan tugmalar bosilganda (vaqtinchalik javob)
@dp.message(F.text.in_({"Buyurtmalar", "Hisobim", "Pul ishlash", "Hisob to'ldirish", "Murojaat", "Qo'llanma", "🗄 Boshqaruv"}))
async def other_buttons_handler(message: types.Message):
    await message.answer(f"Siz '{message.text}' tugmasini bosdingiz. Bu bo'lim hali ishlab chiqilmoqda.", reply_markup=main_menu)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    print("Bot muvaffaqiyatli ishga tushdi!")
    # Bot ishlab turishi uchun pollingni yoqamiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Kodni asinxron tarzda ishga tushirish
    asyncio.run(main())
