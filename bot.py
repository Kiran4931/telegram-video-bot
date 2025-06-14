from pyrogram import Client, filters
from pyrogram.types import Message
import os
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_ydl_options():
    return {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True
    }

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("Hello! Send me a video URL to download.")

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_video(client, message: Message):
    url = message.text.strip()
    ydl_opts = get_ydl_options()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        await message.reply_document(filename)
    except Exception as e:
        await message.reply(f"❌ Failed to download:
{e}")

app.run()