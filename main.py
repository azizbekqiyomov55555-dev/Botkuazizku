import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Railway'da xavfsizlik uchun tokenni Environment Variables (muhit o'zgaruvchilari) orqali olamiz
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM (Finite State Machine) holatlari
class SocialNetworkStates(StatesGroup):
    waiting_for_network_name = State()
    waiting_for_network_action = State()

# Ma'lumotlar bazasi (oddiy ro'yxat ko'rinishida)
user_social_networks = {}  # {user_id: [network1, network2, ...]}

# --- TUGMALAR (KEYBOARDS) ---

# Asosiy menyu tugmalari
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Buyurtma berish")],
        [KeyboardButton(text="Buyurtmalar"), KeyboardButton(text="Hisobim")],
        [KeyboardButton(text="Pul ishlash"), KeyboardButton(text="Hisob to'ldirish")],
        [KeyboardButton(text="Murojaat"), KeyboardButton(text="Qo'llanma")],
        [KeyboardButton(text="🗄 Boshqaruv")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Menyudan tanlang..."
)

# Orqaga qaytish menyusi
back_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Orqaga")]
    ],
    resize_keyboard=True
)

# Ijtimoiy tarmoq qo'shish menyusi
social_network_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="+ Qo'shish")],
        [KeyboardButton(text="Orqaga")]
    ],
    resize_keyboard=True
)

# Tarmoq boshqaruv menyusi
network_management_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="+ Qo'shish")],
        [KeyboardButton(text="Tahrirlash")],
        [KeyboardButton(text="O'chirish")],
        [KeyboardButton(text="Orqaga")]
    ],
    resize_keyboard=True
)

# --- BUYRUQLAR VA XABARLARNI QABUL QILISH ---

# /start buyrug'i uchun
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_menu)

# "Buyurtma berish" tugmasi bosilganda
@dp.message(F.text == "Buyurtma berish")
async def buyurtma_berish_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Foydalanuvchining tarmoqlarini tekshirish
    if user_id in user_social_networks and user_social_networks[user_id]:
        networks = user_social_networks[user_id]
        networks_text = "\n".join([f"• {network}" for network in networks])
        
        # Inline tugmalar yaratish
        inline_keyboard = []
        for network in networks:
            inline_keyboard.append([InlineKeyboardButton(text=f"📱 {network}", callback_data=f"select_{network}")])
        
        inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keydown)
        
        await message.answer(
            f"Quyidagi ijtimoiy tarmoqlardan birini tanlang:\n\n{networks_text}",
            reply_markup=inline_markup
        )
        await message.answer("Yangi tarmoq qo'shish uchun pastdagi tugmani bosing:", 
                            reply_markup=social_network_menu)
    else:
        await message.answer("❗️ Ijtimoiy tarmoqlar mavjud emas!", reply_markup=social_network_menu)
        await state.set_state(SocialNetworkStates.waiting_for_network_action)

# Ijtimoiy tarmoq tanlanganda (inline tugma)
@dp.callback_query(F.data.startswith("select_"))
async def select_network_callback(callback: types.CallbackQuery):
    network_name = callback.data.replace("select_", "")
    await callback.message.answer(f"Siz {network_name} tanladingiz")
    await callback.answer()

# "+ Qo'shish" tugmasi bosilganda
@dp.message(F.text == "+ Qo'shish")
async def add_network_handler(message: types.Message, state: FSMContext):
    await message.answer("📝 Yangi ijtimoiy tarmoq nomini kiriting:", reply_markup=back_menu)
    await state.set_state(SocialNetworkStates.waiting_for_network_name)

# Ijtimoiy tarmoq nomi kiritilganda
@dp.message(SocialNetworkStates.waiting_for_network_name)
async def process_network_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    network_name = message.text
    
    # Foydalanuvchi ma'lumotlarini saqlash
    if user_id not in user_social_networks:
        user_social_networks[user_id] = []
    
    user_social_networks[user_id].append(network_name)
    
    await message.answer(
        f"✔ {network_name} - ijtimoiy tarmoqi muvaffaqiyatli qo'shildi!\n\n"
        f"Saat: 00:49",
        reply_markup=social_network_menu
    )
    
    await state.set_state(SocialNetworkStates.waiting_for_network_action)

# "Orqaga" tugmasi bosilganda
@dp.message(F.text == "Orqaga")
async def orqaga_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🖥 Asosiy menyudasiz!", reply_markup=main_menu)

# "Tahrirlash" tugmasi bosilganda
@dp.message(F.text == "Tahrirlash")
async def edit_network_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_social_networks and user_social_networks[user_id]:
        networks = user_social_networks[user_id]
        networks_text = "\n".join([f"{i+1}. {network}" for i, network in enumerate(networks)])
        
        await message.answer(
            f"Tahrirlash uchun tarmoq raqamini kiriting:\n\n{networks_text}",
            reply_markup=back_menu
        )
    else:
        await message.answer("❗️ Tahrirlash uchun tarmoqlar mavjud emas!", reply_markup=network_management_menu)

# "O'chirish" tugmasi bosilganda
@dp.message(F.text == "O'chirish")
async def delete_network_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_social_networks and user_social_networks[user_id]:
        networks = user_social_networks[user_id]
        networks_text = "\n".join([f"{i+1}. {network}" for i, network in enumerate(networks)])
        
        await message.answer(
            f"O'chirish uchun tarmoq raqamini kiriting:\n\n{networks_text}",
            reply_markup=back_menu
        )
    else:
        await message.answer("❗️ O'chirish uchun tarmoqlar mavjud emas!", reply_markup=network_management_menu)

# "🗄 Boshqaruv" tugmasi bosilganda
@dp.message(F.text == "🗄 Boshqaruv")
async def admin_panel_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_social_networks and user_social_networks[user_id]:
        networks = user_social_networks[user_id]
        networks_text = "\n".join([f"• {network}" for network in networks])
        
        await message.answer(
            f"Sizning tarmoqlaringiz:\n\n{networks_text}\n\n"
            f"Quyidagi amallardan birini tanlang:",
            reply_markup=network_management_menu
        )
    else:
        await message.answer(
            "Sizda hali tarmoqlar mavjud emas. Yangi tarmoq qo'shing:",
            reply_markup=social_network_menu
        )

# Qolgan tugmalar bosilganda
@dp.message(F.text.in_({"Buyurtmalar", "Hisobim", "Pul ishlash", "Hisob to'ldirish", "Murojaat", "Qo'llanma"}))
async def other_buttons_handler(message: types.Message):
    await message.answer(
        f"Siz '{message.text}' tugmasini bosdingiz. Bu bo'lim hali ishlab chiqilmoqda.",
        reply_markup=main_menu
    )

# Boshqa barcha xabarlar uchun
@dp.message()
async def echo_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("Iltimos, menyudan biror tugmani tanlang.", reply_markup=main_menu)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    print("🤖 Bot muvaffaqiyatli ishga tushdi!")
    print("📊 Kutilayotgan xabarlar...")
    
    # Bot ishlab turishi uchun pollingni yoqamiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Kodni asinxron tarzda ishga tushirish
    asyncio.run(main())
