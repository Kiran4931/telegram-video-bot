import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

ydl_opts = {
    'format': 'best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
    'noplaylist': True
}

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("👋 Welcome! Send me a video link to download.")

@app.on_message(filters.text & ~filters.command("start"))
async def download(client, message: Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.reply("❗ Please send a valid link.")
        return
    try:
        await message.reply("⏳ Downloading...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        await message.reply_document(file_path)
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"❌ Failed to download: {str(e)}")

app.run()
