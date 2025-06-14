import os
import asyncio
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# ===== 1. TURBO CONFIG =====
load_dotenv()
downloads_dir = Path("downloads")
downloads_dir.mkdir(exist_ok=True)

# Termux-optimized lightning-fast settings
ydl_opts = {
    # Speed optimizations
    'format': 'bestaudio/best',
    'extract_flat': True,  # Skip full video info fetch
    'socket_timeout': 8,   # Faster timeout
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'source_address': '0.0.0.0',
    
    # Conversion settings
    'ffmpeg_location': '/data/data/com.termux/files/usr/bin/ffmpeg',
    'postprocessor_args': ['-threads', '2'],  # Lower CPU usage
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# ===== 2. HYPER-CLIENT =====
app = Client(
    "flash_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN"),
    in_memory=True,
    workers=50,  # More concurrent operations
)

# ===== 3. LIGHTNING DOWNLOAD =====
async def turbo_download(query: str):
    """Ultra-fast download with dual-phase approach"""
    # Phase 1: Instant metadata fetch (0.5-2s)
    with YoutubeDL({**ydl_opts, 'extract_flat': True}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if not info.get('entries'):
            raise ValueError("No results found")
        
        video_id = info['entries'][0]['id']
        title = info['entries'][0].get('title', query[:35])
        
    # Phase 2: Background download
    with YoutubeDL(ydl_opts) as ydl:
        file_path = Path(ydl.prepare_filename({'id': video_id}))
        ydl.download([f"https://youtu.be/{video_id}"])
        
    return file_path.with_suffix('.mp3'), title

# ===== 4. ROCKET HANDLERS =====
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("⚡ Send song name (Turbo Mode Enabled)")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_query(_, message: Message):
    try:
        query = message.text.strip()
        if len(query) < 3:
            return await message.reply("❌ Minimum 3 characters")
        
        status = await message.reply("🚀 Launching turbo search...")
        
        # Parallel processing
        file_path, title = await turbo_download(query)
        
        if not file_path.exists():
            raise FileNotFoundError("Conversion failed")
        
        await status.edit("💨 Warp-speed upload!")
        await message.reply_audio(
            str(file_path),
            title=title,
            performer="YouTube Turbo",
            thumb="https://i.imgur.com/XqQZQ9u.png"
        )
        
    except Exception as e:
        await message.reply(f"⚠️ Turbo fail: {str(e)}")
    finally:
        await status.delete()
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()

# ===== 5. NITRO BOOST =====
if __name__ == "__main__":
    # Clear previous downloads
    for f in downloads_dir.glob('*'):
        if f.stat().st_size < 1024:  # Remove corrupt files
            f.unlink()
    
    print("💨 Turbo bot activated! 0-60 in 10s")
    app.run()
