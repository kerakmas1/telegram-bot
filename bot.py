import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from config import TOKEN, ADMIN_ID
from db import (
    init_db, add_user, add_code, get_users,
    get_codes, get_code_by_text, delete_code
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

admin_state = {}

# ================= PANEL =================
panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Users"), KeyboardButton(text="📦 Codes")],
        [KeyboardButton(text="➕ Create Code")]
    ],
    resize_keyboard=True
)

# ================= START =================
@dp.message(Command("start"))
async def start(message: types.Message):
    await add_user(message.from_user.id)
    await message.answer("Salom 👋")

# ================= ADMIN =================
@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔")

    await message.answer("Admin panel 👇", reply_markup=panel)

# ================= USERS =================
@dp.message(F.text == "👤 Users")
async def users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    users = await get_users()
    await message.answer(f"👤 Users: {len(users)}")

# ================= CREATE CODE =================
@dp.message(F.text == "➕ Create Code")
async def create_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    admin_state[message.from_user.id] = {"step": "code"}
    await message.answer("🔑 Code yozing:")

# ================= CODES LIST + DELETE BUTTON =================
@dp.message(F.text == "📦 Codes")
async def codes(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    data = await get_codes()

    for c in data:
        code_id = c[0]
        code_name = c[1]
        code_type = c[2]

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🗑 Delete", callback_data=f"del_{code_id}")]
            ]
        )

        await message.answer(f"🔑 {code_name} | {code_type}", reply_markup=kb)

# ================= DELETE HANDLER =================
@dp.callback_query(F.data.startswith("del_"))
async def delete_handler(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("⛔")

    code_id = int(callback.data.split("_")[1])
    await delete_code(code_id)

    await callback.message.edit_text("🗑 Deleted")
    await callback.answer("Deleted")

# ================= CREATE FLOW =================
@dp.message()
async def handler(message: types.Message):
    uid = message.from_user.id

    # ADMIN FLOW
    if uid == ADMIN_ID and uid in admin_state:
        step = admin_state[uid]

        if step["step"] == "code":
            step["code"] = message.text
            step["step"] = "content"
            await message.answer("📎 Rasm/video/file/text yubor:")
            return

        elif step["step"] == "content":
            code = step["code"]

            if message.text and not message.photo and not message.video and not message.document:
                await add_code(code, "text", None, message.text)

            elif message.photo:
                await add_code(code, "photo", message.photo[-1].file_id, None)

            elif message.video:
                await add_code(code, "video", message.video.file_id, None)

            elif message.document:
                await add_code(code, "document", message.document.file_id, None)

            await message.answer(f"✅ Saved: {code}")
            admin_state.pop(uid)
            return

    # USER CODE CHECK
    data = await get_code_by_text(message.text)

    if data:
        _, code, type_, file_id, text = data

        if type_ == "text":
            await message.answer(text)
        elif type_ == "photo":
            await message.answer_photo(file_id)
        elif type_ == "video":
            await message.answer_video(file_id)
        elif type_ == "document":
            await message.answer_document(file_id)
    else:
        await message.answer("❌ Code topilmadi")

# ================= START BOT =================
async def main():
    await init_db()
    print("Bot running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())