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

# Admin ID lari (faqat shu ID lar admin paneliga kira oladi)
ADMIN_IDS = [123456789]  # Bu yerga o'z Telegram ID ingizni yozing

# FSM (Finite State Machine) holatlari
class SocialNetworkStates(StatesGroup):
    waiting_for_network_name = State()
    waiting_for_network_delete = State()
    waiting_for_admin_action = State()

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

# Admin panel menyusi
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="🔒 Majbur obuna kanallar")],
        [KeyboardButton(text="💳 To'lov tizimlar")],
        [KeyboardButton(text="🔧 API")],
        [KeyboardButton(text="👤 Foydalanuvchini boshqarish")],
        [KeyboardButton(text="📚 Qo'llanmalar")],
        [KeyboardButton(text="📦 Buyurtmalar")],
        [KeyboardButton(text="⚙️ Asosiy sozlamalar")],
        [KeyboardButton(text="◀️ Orqaga")]
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
        
        inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        
        await message.answer(
            f"Quyidagi ijtimoiy tarmoqlardan birini tanlang:\n\n{networks_text}",
            reply_markup=inline_markup
        )
        await message.answer("Yangi tarmoq qo'shish uchun pastdagi tugmani bosing:", 
                            reply_markup=social_network_menu)
    else:
        await message.answer("❗️ Ijtimoiy tarmoqlar mavjud emas!", reply_markup=social_network_menu)
        await state.set_state(SocialNetworkStates.waiting_for_network_action)

# "Buyurtmalar" tugmasi bosilganda
@dp.message(F.text == "Buyurtmalar")
async def buyurtmalar_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in user_social_networks and user_social_networks[user_id]:
        networks = user_social_networks[user_id]
        networks_text = "\n".join([f"• {network}" for network in networks])
        
        # Inline tugmalar yaratish
        inline_keyboard = []
        for i, network in enumerate(networks):
            inline_keyboard.append([
                InlineKeyboardButton(text=f"❌ {network}", callback_data=f"delete_{network}")
            ])
        
        inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        
        await message.answer(
            f"Sizning ijtimoiy tarmoqlaringiz:\n\n{networks_text}\n\n"
            f"O'chirish uchun tarmoq ustiga bosing:",
            reply_markup=inline_markup
        )
    else:
        await message.answer("Sizda hali ijtimoiy tarmoqlar mavjud emas!", reply_markup=main_menu)

# Ijtimoiy tarmoqni o'chirish
@dp.callback_query(F.data.startswith("delete_"))
async def delete_network_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    network_name = callback.data.replace("delete_", "")
    
    if user_id in user_social_networks and network_name in user_social_networks[user_id]:
        user_social_networks[user_id].remove(network_name)
        await callback.message.edit_text(
            f"✅ Telgram - tarmoqi muvaffaqiyatli o'chirildi!\n\n"
            f"Boshqaruv"
        )
    else:
        await callback.answer("Tarmoq topilmadi!", show_alert=True)
    
    await callback.answer()

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
        await state.set_state(SocialNetworkStates.waiting_for_network_delete)
    else:
        await message.answer("❗️ O'chirish uchun tarmoqlar mavjud emas!", reply_markup=network_management_menu)

# Tarmoq raqamini kiritib o'chirish
@dp.message(SocialNetworkStates.waiting_for_network_delete)
async def process_delete_network(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    try:
        network_index = int(message.text) - 1
        if user_id in user_social_networks and 0 <= network_index < len(user_social_networks[user_id]):
            deleted_network = user_social_networks[user_id].pop(network_index)
            await message.answer(
                f"✅ {deleted_network} - tarmoqi muvaffaqiyatli o'chirildi!\n\n"
                f"Boshqaruv",
                reply_markup=network_management_menu
            )
        else:
            await message.answer("❌ Noto'g'ri raqam kiritildi!", reply_markup=network_management_menu)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!", reply_markup=network_management_menu)
    
    await state.clear()

# "🗄 Boshqaruv" tugmasi bosilganda (Admin panel)
@dp.message(F.text == "🗄 Boshqaruv")
async def admin_panel_handler(message: types.Message):
    user_id = message.from_user.id
    
    # Admin tekshiruvi
    if user_id in ADMIN_IDS:
        await message.answer(
            "👋 Admin paneliga hush kelibsiz !\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=admin_menu
        )
    else:
        # Oddiy foydalanuvchi uchun tarmoqlar boshqaruvi
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

# Admin panel tugmalari
@dp.message(F.text == "📊 Statistika")
async def admin_statistika(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        total_users = len(user_social_networks)
        total_networks = sum(len(networks) for networks in user_social_networks.values())
        await message.answer(
            f"📊 Statistika:\n\n"
            f"👥 Foydalanuvchilar: {total_users}\n"
            f"🌐 Ijtimoiy tarmoqlar: {total_networks}\n"
            f"📅 Bot ishga tushgan sana: 2024",
            reply_markup=admin_menu
        )

@dp.message(F.text == "📢 Xabar yuborish")
async def admin_xabar(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "📢 Barcha foydalanuvchilarga xabar yuborish.\n"
            "Xabar matnini kiriting:",
            reply_markup=back_menu
        )

@dp.message(F.text == "🔒 Majbur obuna kanallar")
async def admin_kanallar(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "🔒 Majburiy obuna kanallari ro'yxati:\n\n"
            "1. @kanal_nomi1\n"
            "2. @kanal_nomi2\n\n"
            "➕ Yangi kanal qo'shish uchun /add_channel",
            reply_markup=admin_menu
        )

@dp.message(F.text == "💳 To'lov tizimlar")
async def admin_tolov(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "💳 To'lov tizimlari:\n\n"
            "• Click\n"
            "• Payme\n"
            "• Uzum Bank\n\n"
            "Sozlash uchun /payment_settings",
            reply_markup=admin_menu
        )

@dp.message(F.text == "🔧 API")
async def admin_api(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "🔧 API sozlamalari:\n\n"
            "API Token: ******\n"
            "API URL: https://api.example.com\n\n"
            "Yangilash uchun /api_settings",
            reply_markup=admin_menu
        )

@dp.message(F.text == "👤 Foydalanuvchini boshqarish")
async def admin_user(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "👤 Foydalanuvchi boshqaruvi:\n\n"
            "Foydalanuvchi ID sini kiriting:",
            reply_markup=back_menu
        )

@dp.message(F.text == "📚 Qo'llanmalar")
async def admin_qollanma(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "📚 Qo'llanmalar:\n\n"
            "1. Botdan foydalanish\n"
            "2. Admin panel\n"
            "3. To'lov tizimlari\n"
            "4. API integrasiyasi\n\n"
            "Ko'rish uchun raqamni bosing:",
            reply_markup=admin_menu
        )

@dp.message(F.text == "📦 Buyurtmalar")
async def admin_buyurtmalar(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "📦 Barcha buyurtmalar:\n\n"
            "1. Foydalanuvchi @username - Telegram - 100 ta\n"
            "2. Foydalanuvchi @username2 - Instagram - 50 ta\n\n"
            "Jami: 2 ta buyurtma",
            reply_markup=admin_menu
        )

@dp.message(F.text == "⚙️ Asosiy sozlamalar")
async def admin_sozlamalar(message: types.Message):
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer(
            "⚙️ Asosiy sozlamalar:\n\n"
            "• Bot nomi: SMM Bot\n"
            "• Til: O'zbek\n"
            "• Valyuta: UZS\n\n"
            "O'zgartirish uchun /settings",
            reply_markup=admin_menu
        )

# Qolgan tugmalar bosilganda
@dp.message(F.text.in_({"Hisobim", "Pul ishlash", "Hisob to'ldirish", "Murojaat", "Qo'llanma"}))
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
    print(f"👑 Admin ID: {ADMIN_IDS[0]}")
    
    # Bot ishlab turishi uchun pollingni yoqamiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Kodni asinxron tarzda ishga tushirish
    asyncio.run(main())
