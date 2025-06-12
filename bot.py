from pyrogram import Client, filters
from pyrogram.types import Message
import os
import yt_dlp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Progress hook for download progress
async def progress_hook(d, msg: Message):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        try:
            filled = int(float(percent.replace('%', '')) // 5)
            bar = '█' * filled + '░' * (20 - filled)
            await msg.edit_text(f"📥 Downloading...\n[{bar}] {percent}")
        except:
            pass

# yt-dlp options
def get_ydl_options(progress_hook_func):
    return {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'progress_hooks': [lambda d: app.loop.create_task(progress_hook_func(d))],
    }

# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Send me any video URL (YouTube, Instagram, etc) and I’ll download it!")

# Download handler
@app.on_message(filters.text & ~filters.command("start"))
async def download_video(client, message):
    url = message.text
    status_msg = await message.reply("🔍 Fetching download link...")
    try:
        with yt_dlp.YoutubeDL(get_ydl_options(lambda d: progress_hook(d, status_msg))) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            await message.reply_document(file_path, caption=f"✅ Downloaded: {info.get('title', 'Video')}")
            os.remove(file_path)  # optional: cleanup
    except Exception as e:
        await status_msg.edit(f"❌ Failed to download:\n`{str(e)}`")

# Run the bot
app.run()