import re
import os
import urllib.parse  # Share button me text encode karne ke liye
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import Config
from plugins.settings import USER_PREFS
from utils.image_manager import get_image

# --- HELPER FUNCTIONS ---
def format_size(bytes_size):
    """File size ko Bytes se KB/MB me convert karta hai"""
    if not bytes_size: return "Unknown Size"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return "Unknown Size"

def get_smart_file_details(filename):
    """Extension ke hisaab se Smart Emoji aur Format text nikalta hai"""
    ext = str(filename).split('.')[-1].lower() if '.' in str(filename) else ""
    
    if ext in ['pdf']:
        emoji, form = "📕", "PDF"
    elif ext in ['mp4', 'mkv', 'avi', 'mov', 'webm']:
        emoji, form = "🎬", "VIDEO"
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
        emoji, form = "🗜️", "ARCHIVE"
    elif ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
        emoji, form = "🖼️", "IMAGE"
    elif ext in ['apk', 'xapk']:
        emoji, form = "📱", "ANDROID APP"
    elif ext in ['mp3', 'm4a', 'wav']:
        emoji, form = "🎵", "AUDIO"
    elif ext in ['exe', 'msi']:
        emoji, form = "💻", "PC SOFTWARE"
    else:
        emoji, form = "📂", "DOCUMENT"
        
    # Extension hatakar clean name do
    clean_name = str(filename).replace("_", " ")
    clean_name = re.sub(r'\.(pdf|zip|mp4|mkv|rar|exe|apk|txt|png|jpg|jpeg|mp3)$', '', clean_name, flags=re.IGNORECASE)
    return emoji, form, clean_name.strip()

def generate_hashtags(clean_name):
    """File ke naam se automatically 2-3 trending hashtags banata hai"""
    # Sirf wo words lo jo 3 letter se bade hain
    words = re.findall(r'\b[a-zA-Z]{4,}\b', clean_name)
    tags = [f"#{word.capitalize()}" for word in words[:3]] # Top 3 words
    
    # Ek generic tag add kar do
    tags.append("#TelegramFiles")
    return " ".join(tags)

def extract_name_and_size(raw_name):
    """Text me se file size nikalta hai aur emojis clean karta hai"""
    size_match = re.search(r'\(?(\d+(\.\d+)?\s*[KMG]B)\)?', raw_name, re.IGNORECASE)
    size_str = size_match.group(1).upper() if size_match else "Unknown Size"
    
    name = re.sub(r'(📁\s*File Name:|📄|✅|🔗\s*File Link:?)', '', raw_name, flags=re.IGNORECASE)
    name = re.sub(r'\(\d+(\.\d+)?\s*[KMG]B\)', '', name, flags=re.IGNORECASE)
    return name.strip(), size_str

# Filters me Photo, Document, Text sab allowed hai
@Client.on_message((filters.text | filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def format_message(client, message):
    if message.text and message.text.startswith("/"): return

    chat_id = message.chat.id
    status_msg = await message.reply_text("📂 **Analyzing & Upgrading message...**")
    
    # Password Section
    saved_pass = USER_PREFS.get(chat_id) 
    pass_section = (f"│\n│  <b>🔐 FILE PASSWORD:</b>\n│   👉  {saved_pass}  👈\n│") if saved_pass else ""

    try:
        # ==========================================
        # SCENARIO 1: AGAR USER NE DIRECT FILE BHEJI HAI
        # ==========================================
        if message.document or message.video or message.audio or message.photo:
            
            if message.photo:
                file_name = "Image_File.jpg"
                file_size = format_size(message.photo.file_size) if hasattr(message.photo, 'file_size') else "Unknown Size"
            else:
                media = message.document or message.video or message.audio
                file_name = getattr(media, "file_name", "Unknown File")
                f_size = getattr(media, "file_size", 0)
                file_size = format_size(f_size)

            # Smart details nikalo
            file_emoji, file_format, clean_title = get_smart_file_details(file_name)
            clean_title = clean_title.upper()
            hashtags = generate_hashtags(clean_title)

            # ULTRA-PREMIUM CAPTION
            caption_text = (
                f"══════════════════════\n"
                f"<blockquote>{file_emoji} <code>{clean_title}</code> {file_emoji}</blockquote>\n"
                f"══════════════════════\n"
                f"│\n"
                f"│ 💾 <b>Size:</b> {file_size} | ⚙️ <b>Format:</b> {file_format}\n"
                f"│ 🛡️ <b>Status:</b> Safe & Verified\n"
                f"│\n"
                f"│ 🔓 <b>Direct File (No Ads):</b>\n"
                f"│ <a href='{Config.DIRECT_PDF_LINK}'>Click to Request</a>\n"
                f"│\n"
                f"│ 📺 <b>Video Tutorial:</b>\n"
                f"│ <a href='{Config.TUTORIAL_VIDEO}'>Watch How to Open</a>\n"
                f"{pass_section}\n" 
                f"│\n"
                f"│ <i>{hashtags}</i>\n"
                f"├───────────────────────\n"
                f"│ 👤 ADMIN: <b>{Config.OWNER_NAME}</b> ✨\n"
                f"│ 🌐 <a href='{Config.TELEGRAM_USER}'>Telegram</a> | <a href='{Config.INSTAGRAM}'>Instagram</a> | <a href='{Config.YOUTUBE}'>YT</a>\n"
                f"└───────────────────────┘\n\n"
                f"👇 <b>Save/Forward Your File From Below</b> 👇"
            )
            
            # SHARE BUTTON LOGIC
            share_text = urllib.parse.quote(f"🚀 Found an amazing file: {clean_title}!\n\nGet it here 👇")
            share_url = f"https://t.me/share/url?url={Config.CHANNEL_LINK}&text={share_text}"

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📢 Join Channel", url=Config.CHANNEL_LINK),
                    InlineKeyboardButton("🚀 Share Post", url=share_url)
                ]
            ])
            
            await message.copy(
                chat_id=chat_id, 
                caption=caption_text, 
                parse_mode=ParseMode.HTML,
                reply_markup=buttons
            )
            
            await status_msg.delete()
            return

        # ==========================================
        # SCENARIO 2: AGAR USER NE TEXT/LINKS BHEJE HAIN
        # ==========================================
        elif message.text:
            raw_text = message.text
            lines = raw_text.split('\n')
            items_to_process = []
            current_name_buffer = []

            for line in lines:
                line = line.strip()
                if not line: continue

                url_match = re.search(r'(https?://[^\s]+)', line)
                if url_match:
                    url = url_match.group(1)
                    raw_name = " ".join(current_name_buffer).strip()
                    
                    text_in_url_line = line.replace(url, "").strip()
                    if text_in_url_line:
                        raw_name = raw_name + " " + text_in_url_line
                        
                    final_name, size_str = extract_name_and_size(raw_name)
                    if not final_name:
                        final_name = "Downloaded_File"
                        
                    items_to_process.append({"name": final_name, "size": size_str, "link": url})
                    current_name_buffer = [] 
                else:
                    if "Upload Complete" not in line and "✅" not in line:
                        current_name_buffer.append(line)

            if not items_to_process:
                final_name, size_str = extract_name_and_size(" ".join(current_name_buffer))
                if final_name:
                    items_to_process.append({"name": final_name, "size": size_str, "link": None})

            if not items_to_process:
                await status_msg.edit("❌ Koi valid file ya link nahi mila!")
                return

            await status_msg.edit(f"⚙️ **Processing {len(items_to_process)} Link(s)...**")

            for item in items_to_process:
                raw_filename = item['name']
                file_size = item['size']
                short_link = item['link']
                
                # Smart details nikalo
                file_emoji, file_format, clean_title = get_smart_file_details(raw_filename)
                clean_title = clean_title.upper()
                hashtags = generate_hashtags(clean_title)

                image_path = get_image(clean_title)
                if not image_path: continue 

                final_download_link = short_link if short_link else Config.CHANNEL_LINK

                # ULTRA-PREMIUM CAPTION FOR LINKS
                caption_text = (
                    f"══════════════════════\n"
                    f"<blockquote>{file_emoji} <code>{clean_title}</code> {file_emoji}</blockquote>\n"
                    f"══════════════════════\n"
                    f"│\n"
                    f"│ 💾 <b>Size:</b> {file_size} | ⚙️ <b>Format:</b> {file_format}\n"
                    f"│ 🛡️ <b>Status:</b> Safe & Verified\n"
                    f"│\n"
                    f"│ 📥 <b>File Download Link:</b>\n"
                    f"│ <a href='{final_download_link}'>Click Here to Download</a>\n"
                    f"│\n"
                    f"│ 🔓 <b>Direct File (No Ads):</b>\n"
                    f"│ <a href='{Config.DIRECT_PDF_LINK}'>Click to Request</a>\n"
                    f"│\n"
                    f"│ 📺 <b>Video Tutorial:</b>\n"
                    f"│ <a href='{Config.TUTORIAL_VIDEO}'>Watch How to Open</a>\n"
                    f"{pass_section}\n" 
                    f"│\n"
                    f"│ <i>{hashtags}</i>\n"
                    f"├───────────────────────\n"
                    f"│ 👤 ADMIN: <b>{Config.OWNER_NAME}</b> ✨\n"
                    f"│ 🌐 <a href='{Config.TELEGRAM_USER}'>Telegram</a> | <a href='{Config.INSTAGRAM}'>Instagram</a> | <a href='{Config.YOUTUBE}'>YT</a>\n"
                    f"└───────────────────────┘\n\n"
                    f"👇 <b>Download Your File Below</b> 👇"
                )
                
                # SHARE BUTTON LOGIC
                share_text = urllib.parse.quote(f"🚀 Found an amazing file: {clean_title}!\n\nGet it here 👇")
                share_url = f"https://t.me/share/url?url={Config.CHANNEL_LINK}&text={share_text}"

                buttons_list = []
                if short_link:
                    buttons_list.append([InlineKeyboardButton("📥 Download File", url=short_link)])
                
                # Niche 2 button ek sath (Join + Share)
                buttons_list.append([
                    InlineKeyboardButton("📢 Join Channel", url=Config.CHANNEL_LINK),
                    InlineKeyboardButton("🚀 Share Post", url=share_url)
                ])
                
                buttons = InlineKeyboardMarkup(buttons_list)
                
                await client.send_photo(
                    chat_id=chat_id,
                    photo=image_path, 
                    caption=caption_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=buttons
                )

            await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"⚠️ Error aagaya: {e}")