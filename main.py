import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# =======================================================
# НАСТРОЙКИ (Замени на свои данные, когда перейдешь на ПК)
# Прежде чем пушить на GitHub, оставь эти строки как есть!
# =======================================================
API_ID = 12345678  
API_HASH = "ВАШ_API_HASH_СЮДА"

app = Client("doors_eyes", api_id=API_ID, api_hash=API_HASH)

# Множество для хранения ID чатов, где запущен режим .mute
muted_chats = set()

# -------------------------------------------------------
# КОМАНДА: .mute (Включить режим "Doors Eyes")
# -------------------------------------------------------
@app.on_message(filters.command("mute", prefixes=".") & filters.me)
async def cmd_mute(client: Client, message: Message):
    muted_chats.add(message.chat.id)
    await message.edit_text("👁️ <b>Doors Eyes:</b> Мьют включён. Я вижу и удаляю всё.")

# -------------------------------------------------------
# КОМАНДА: .unmute (Выключить режим "Doors Eyes")
# -------------------------------------------------------
@app.on_message(filters.command("unmute", prefixes=".") & filters.me)
async def cmd_unmute(client: Client, message: Message):
    if message.chat.id in muted_chats:
        muted_chats.remove(message.chat.id)
    await message.edit_text("👁️ <b>Doors Eyes:</b> Мьют отключён. Собеседник помилован.")

# -------------------------------------------------------
# КОМАНДА: .spam X текст (Запустить спам)
# -------------------------------------------------------
@app.on_message(filters.command("spam", prefixes=".") & filters.me)
async def cmd_spam(client: Client, message: Message):
    try:
        # Парсим аргументы команды
        args = message.text.split(maxsplit=2)
        count = int(args[1])
        text = args[2]
        
        # Защитный лимит на количество сообщений
        if count > 100:
            count = 100
            
        # Сначала успешно спамим на максимальной скорости
        for _ in range(count):
            await client.send_message(message.chat.id, text)
            await asyncio.sleep(0.05)  # Минимальная пауза для защиты твоего аккаунта от бана
            
        # Удаляем свою команду .spam только после успешного цикла
        await message.delete()
            
    except Exception:
        # Если в аргументах ошибка — безопасно изменяем текст сообщения команды
        try:
            await message.edit_text("❌ Ошибка. Используй: <code>.spam 10 Текст</code>")
        except Exception:
            pass

# -------------------------------------------------------
# МОНИТОРИНГ: Перехват измененных сообщений собеседника
# -------------------------------------------------------
@app.on_edited_message(filters.private & ~filters.me)
async def edited_handler(client: Client, edited: Message):
    try:
        await client.send_message(
            edited.chat.id, 
            f"✏️ <b>Собеседник изменил сообщение:</b>\n{edited.text}"
        )
    except Exception:
        pass

# -------------------------------------------------------
# ФУНКЦИОНАЛ МЬЮТА: Удаление входящих сообщений на лету
# -------------------------------------------------------
@app.on_message(filters.private & ~filters.me, group=1)
async def delete_muted_messages(client: Client, message: Message):
    if message.chat.id in muted_chats:
        try:
            await message.delete()
        except Exception:
            pass

# -------------------------------------------------------
# ЗАПУСК
# -------------------------------------------------------
if __name__ == "__main__":
    print("[!] Запуск юзербота Doors Eyes...")
    app.run()
