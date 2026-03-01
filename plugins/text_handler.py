import re
import os
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import Config
from plugins.settings import USER_PREFS
from utils.image_manager import get_image
from datetime import datetime

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
    """Extension ke hisaab se Smart Emoji aur Format text nikalta hai.
    Original file name ko bhi preserve karta hai."""
    ext = str(filename).split('.')[-1].lower() if '.' in str(filename) else "file"
    
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
        
    # File name ko bilkul waise hi rakha gaya hai taaki original feel aaye
    clean_name = str(filename).strip()
    return emoji, form, clean_name

def generate_hashtags(filename):
    """File ke naam se automatically 2-3 trending hashtags banata hai"""
    # Extension hatakar clean words nikalte hain sirf tags ke liye
    name_without_ext = re.sub(r'\.[a-zA-Z0-9]+$', '', str(filename))
    words = re.findall(r'\b[a-zA-Z]{4,}\b', name_without_ext)
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
    status_msg = await message.reply_text("⏳ **Analyzing & Upgrading message... Please wait!**")
    
    # Password Section
    saved_pass = USER_PREFS.get(chat_id) 
    pass_section = (f"│\n│ 🔐 <b>FILE PASSWORD:</b>\n│ 👉 <code>{saved_pass}</code> 👈\n│") if saved_pass else ""

    try:
        # ==========================================
        # SCENARIO 1: AGAR USER NE DIRECT FILE BHEJI HAI
        # ==========================================
        if message.document or message.video or message.audio or message.photo:
            
            if message.photo:
                # Telegram compressed photos ka naam hata deta hai, 
                # isliye hum Professional Timestamp logic use karenge.
                msg_date = message.date
                date_str = msg_date.strftime("%Y%m%d_%H%M%S") if msg_date else "Unknown"
                file_name = f"IMG_{date_str}.jpg"
                file_size = format_size(message.photo.file_size) if hasattr(message.photo, 'file_size') else "Unknown Size"
            else:
                media = message.document or message.video or message.audio
                # Agar direct document hai, toh asli naam yahan se nikal aayega
                file_name = getattr(media, "file_name", None)
                if not file_name: # Fallback agar document ka bhi naam missing ho
                    file_name = "Unknown_Media_File"
                    
                file_size = format_size(getattr(media, "file_size", 0))

            # --- Extract & Format File Metadata ---
            file_emoji, file_format, exact_title = get_smart_file_details(file_name)
            hashtags = generate_hashtags(exact_title)

            # ULTRA-PREMIUM CAPTION
            caption_text = (
                f"\n"
                f"<blockquote>{file_emoji} <b>FILE NAME:</b>\n<code>{exact_title}</code></blockquote>\n"
                f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                f"│\n"
                f"│ ⚙️ <b>Format:</b> {file_format}\n"
                f"│ 💾 <b>Size:</b> {file_size}\n"
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
                f"│ 🌐 <a href='{Config.TELEGRAM_USER}'>Telegram</a> | <a href='{Config.INSTAGRAM}'>Instagram</a> | <a href='{Config.YOUTUBE}'>YouTube</a>\n"
                f"└───────────────────────┘\n\n"
                f"👇 <b>Save/Forward Your File From Below</b> 👇"
            )
            
            # PERFECT SHARE BUTTON LOGIC
            raw_share_text = f"🚀 Found an amazing file: {exact_title}!\n\n👇 Get it here 👇\n{Config.CHANNEL_LINK}"
            share_text = urllib.parse.quote(raw_share_text)
            share_url = f"https://t.me/share/url?text={share_text}"

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
                
                # Smart details nikalo (original naam same rahega)
                file_emoji, file_format, exact_title = get_smart_file_details(raw_filename)
                hashtags = generate_hashtags(exact_title)

                image_path = get_image(exact_title)
                final_download_link = short_link if short_link else Config.CHANNEL_LINK

                # ULTRA-PREMIUM CAPTION FOR LINKS
                caption_text = (
                    f"\n"
                    f"<blockquote>{file_emoji} <b>FILE NAME:</b>\n<code>{exact_title}</code></blockquote>\n"
                    f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                    f"│\n"
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
                    f"│ 🌐 <a href='{Config.TELEGRAM_USER}'>Telegram</a> | <a href='{Config.INSTAGRAM}'>Instagram</a> | <a href='{Config.YOUTUBE}'>YouTube</a>\n"
                    f"└───────────────────────┘\n\n"
                    f"👇 <b>Download Your File Below</b> 👇"
                )
                
                # PERFECT SHARE BUTTON LOGIC
                raw_share_text = f"🚀 Found an amazing file: {exact_title}!\n\n👇 Get it here 👇\n{Config.CHANNEL_LINK}"
                share_text = urllib.parse.quote(raw_share_text)
                share_url = f"https://t.me/share/url?text={share_text}"

                buttons_list = []
                if short_link:
                    buttons_list.append([InlineKeyboardButton("📥 Download File", url=short_link)])
                
                # Niche 2 button ek sath (Join + Share)
                buttons_list.append([
                    InlineKeyboardButton("📢 Join Channel", url=Config.CHANNEL_LINK),
                    InlineKeyboardButton("🚀 Share Post", url=share_url)
                ])
                
                buttons = InlineKeyboardMarkup(buttons_list)
                
                # Bug Fix: Agar image na ho toh properly text message bhej dega (skip nahi karega)
                if image_path:
                    await client.send_photo(
                        chat_id=chat_id,
                        photo=image_path, 
                        caption=caption_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=buttons
                    )
                else:
                    await client.send_message(
                        chat_id=chat_id,
                        text=caption_text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=buttons,
                        disable_web_page_preview=True
                    )

            await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"⚠️ **Error Occurred:**\n`{e}`\n\n_Please try again or contact Admin._")