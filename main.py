import asyncio
import json
import logging
import os

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import API_ID, API_HASH, SESSION_NAME

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

MUTED_FILE = "muted.json"


def load_muted():
    if not os.path.exists(MUTED_FILE):
        return set()

    try:
        with open(MUTED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception as e:
        logging.error(f"Ошибка загрузки muted.json: {e}")
        return set()


def save_muted():
    try:
        with open(MUTED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(muted_chats), f)
    except Exception as e:
        logging.error(f"Ошибка сохранения muted.json: {e}")


muted_chats = load_muted()


@app.on_message(filters.command("mute", prefixes=".") & filters.me)
async def cmd_mute(client: Client, message: Message):
    muted_chats.add(message.chat.id)
    save_muted()

    await message.edit(
        "👁️ <b>Doors Eyes</b>\n"
        "✅ Режим мьюта включён."
    )


@app.on_message(filters.command("unmute", prefixes=".") & filters.me)
async def cmd_unmute(client: Client, message: Message):
    muted_chats.discard(message.chat.id)
    save_muted()

    await message.edit(
        "👁️ <b>Doors Eyes</b>\n"
        "❎ Режим мьюта отключён."
    )


@app.on_message(filters.command("spam", prefixes=".") & filters.me)
async def cmd_spam(client: Client, message: Message):

    args = message.text.split(maxsplit=2)

    if len(args) < 3:
        await message.edit(
            "❌ Использование:\n"
            "<code>.spam 10 текст</code>"
        )
        return

    try:
        count = int(args[1])
    except ValueError:
        await message.edit("❌ Количество должно быть числом.")
        return

    text = args[2]

    count = max(1, min(count, 100))

    await message.delete()

    for _ in range(count):
        try:
            await client.send_message(message.chat.id, text)
            await asyncio.sleep(0.05)

        except FloodWait as e:
            logging.warning(f"FloodWait {e.value} сек.")
            await asyncio.sleep(e.value)

        except Exception as e:
            logging.error(e)
            break


@app.on_edited_message(filters.private & ~filters.me)
async def edited_handler(client: Client, edited: Message):

    text = (
        edited.text
        or edited.caption
        or "<без текста>"
    )

    try:
        await client.send_message(
            edited.chat.id,
            f"✏️ <b>Сообщение изменено:</b>\n\n{text}"
        )

    except Exception as e:
        logging.error(e)


@app.on_message(filters.private & ~filters.me, group=1)
async def delete_muted_messages(client: Client, message: Message):

    if message.chat.id not in muted_chats:
        return

    try:
        await message.delete()

    except Exception as e:
        logging.error(e)


@app.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping(client: Client, message: Message):
    await message.edit("🏓 Pong!")


@app.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_cmd(client: Client, message: Message):

    await message.edit(
        "<b>👁️ Doors Eyes</b>\n\n"

        "<code>.mute</code> — включить мьют\n"
        "<code>.unmute</code> — выключить мьют\n"
        "<code>.spam N текст</code> — отправить сообщения\n"
        "<code>.ping</code> — проверить работу\n"
        "<code>.help</code> — помощь"
    )


if __name__ == "__main__":
    logging.info("Doors Eyes запущен.")
    app.run()
