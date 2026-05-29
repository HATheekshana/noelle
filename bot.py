import asyncio
from collections import defaultdict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# =========================
# CONFIG
# =========================

BOT_TOKEN = "8596651439:AAG8f6HnKayox8KWVhrtUS8wm7nlVbZfqK8"

# Group/channel ID
TARGET_CHAT_ID = -1001459190925

# Your Telegram user ID
ADMIN_ID = 1675903713

# =========================

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# users waiting to broadcast
waiting_broadcast = set()

# media groups storage
albums = defaultdict(list)

# processed albums
processed_albums = set()


# =========================
# START
# =========================

@dp.message(Command("start"))
async def start(message: Message):
    await message.reply(
        "Broadcast Bot Online.\n\n"
        "/broadcast - send broadcast\n"
        "/cancel - cancel broadcast"
    )


# =========================
# BROADCAST COMMAND
# =========================

@dp.message(Command("broadcast"))
async def broadcast(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    waiting_broadcast.add(message.from_user.id)

    await message.reply(
        "Send the message/media/album to broadcast.\n\n"
        "Use /cancel to stop."
    )


# =========================
# CANCEL
# =========================

@dp.message(Command("cancel"))
async def cancel(message: Message):

    waiting_broadcast.discard(message.from_user.id)

    await message.reply("Broadcast cancelled.")


# =========================
# HANDLE MEDIA GROUPS
# =========================

@dp.message(F.media_group_id)
async def media_group_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting_broadcast:
        return

    media_group_id = message.media_group_id

    albums[media_group_id].append(message.message_id)

    # wait for all album parts
    await asyncio.sleep(2)

    # already processed
    if media_group_id in processed_albums:
        return

    processed_albums.add(media_group_id)

    try:

        message_ids = albums[media_group_id]

        await bot.copy_messages(
            chat_id=TARGET_CHAT_ID,
            from_chat_id=message.chat.id,
            message_ids=message_ids
        )

        await message.reply(
            f"✅ Album broadcasted ({len(message_ids)} items)"
        )

    except Exception as e:
        await message.reply(f"❌ Error:\n{e}")

    finally:
        waiting_broadcast.discard(user_id)

        albums.pop(media_group_id, None)


# =========================
# HANDLE SINGLE MESSAGES
# =========================

@dp.message()
async def single_message_handler(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting_broadcast:
        return

    # ignore album parts
    if message.media_group_id:
        return

    try:

        await bot.copy_message(
            chat_id=TARGET_CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        await message.reply("✅ Broadcast sent.")

    except Exception as e:
        await message.reply(f"❌ Error:\n{e}")

    finally:
        waiting_broadcast.discard(user_id)


# =========================
# MAIN
# =========================

async def main():

    print("Bot started")

    me = await bot.get_me()

    print(f"Logged in as @{me.username}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())