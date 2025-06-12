from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
import yt_dlp
from dotenv import load_dotenv

# Load .env variables if on Render or Replit
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("main_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def progress_hook(d, msg: Message, progress_msg):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        try:
            filled = int(float(percent.replace('%', '')) // 5)
            bar = '█' * filled + '░' * (20 - filled)
            await progress_msg.edit_text(f"⬇ Downloading: {percent}\n`{bar}`")
        except:
            pass

def get_ydl_options(progress_hook_func):
    return {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook_func]
    }

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("👋 Send me any social media link to download the video.")

@app.on_message(filters.text & ~filters.command("start"))
async def download(_, message: Message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.reply("❌ Invalid URL.")
        return

    progress_msg = await message.reply("⏳ Starting download...")

    try:
        async def hook(d):
            await progress_hook(d, message, progress_msg)

        ydl_opts = get_ydl_options(hook)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await progress_msg.edit_text("📤 Uploading video...")
        await message.reply_video(filename, caption="✅ Download complete!")
        await progress_msg.delete()

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Subscribe to Our Channel", url="https://t.me/lootsandearning0")]]
        )
        await message.reply("🙏 Support us by subscribing to our channel!", reply_markup=keyboard)

        os.remove(filename)

    except Exception as e:
        await progress_msg.edit_text(f"❌ Error: `{str(e)}`")

app.run()
