import re
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode  # HTML Parsing ke liye zaroori hai
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

def clean_filename(filename):
    """Faltu underscores hatata hai par Extension (.pdf, .mkv) ko safe rakhta hai"""
    clean_name = str(filename).replace("_", " ")
    return clean_name.strip()

def extract_name_and_size(raw_name):
    """Text me se file size nikalta hai aur emojis clean karta hai"""
    # Text me se size (e.g., 789.5 KB ya MB) dhoondo
    size_match = re.search(r'\(?(\d+(\.\d+)?\s*[KMG]B)\)?', raw_name, re.IGNORECASE)
    size_str = size_match.group(1).upper() if size_match else "Unknown Size"
    
    # Faltu emojis aur size ko title me se hata do
    name = re.sub(r'(📁\s*File Name:|📄|✅|🔗\s*File Link:?)', '', raw_name, flags=re.IGNORECASE)
    name = re.sub(r'\(\d+(\.\d+)?\s*[KMG]B\)', '', name, flags=re.IGNORECASE)
    return name.strip(), size_str

# Filters me Photo, Document, Text sab allowed hai
@Client.on_message((filters.text | filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def format_message(client, message):
    if message.text and message.text.startswith("/"): return

    chat_id = message.chat.id
    status_msg = await message.reply_text("📂 **Analyzing message...**")
    
    # HTML format me Password Section banaya
    saved_pass = USER_PREFS.get(chat_id) 
    pass_section = (f"│\n│  <b>🔐 FILE PASSWORD:</b>\n│   👉  {saved_pass}  👈\n│") if saved_pass else ""

    try:
        # ==========================================
        # SCENARIO 1: AGAR USER NE DIRECT FILE BHEJI HAI
        # ==========================================
        if message.document or message.video or message.audio or message.photo:
            
            if message.photo:
                file_name = "Image File.jpg"
                file_size = format_size(message.photo.file_size) if hasattr(message.photo, 'file_size') else "Unknown Size"
            else:
                media = message.document or message.video or message.audio
                file_name = getattr(media, "file_name", "Unknown File")
                f_size = getattr(media, "file_size", 0)
                file_size = format_size(f_size)

            clean_title = clean_filename(file_name).upper()

            # BLOCKQUOTE (<blockquote>) Box format for beautiful UI
            caption_text = (
                f"══════════════════════\n"
                f"<blockquote>📂 <code>{clean_title}</code> 📂</blockquote>\n"
                f"══════════════════════\n"
                f"│\n"
                f"│ 💾 <b>Size:</b> {file_size}\n"
                f"│\n"
                f"│ 🔓 <b>Direct File (No Ads):</b>\n"
                f"│ <a href='{Config.DIRECT_PDF_LINK}'>Click to Request</a>\n"
                f"│\n"
                f"│ 📺 <b>Video Tutorial:</b>\n"
                f"│ <a href='{Config.TUTORIAL_VIDEO}'>Watch How to Open</a>\n"
                f"{pass_section}\n" 
                f"├───────────────────────\n"
                f"│ 👤 ADMIN: <b>{Config.OWNER_NAME}</b> ✨\n"
                f"│ 🌐 <a href='{Config.TELEGRAM_USER}'>Telegram</a> | <a href='{Config.INSTAGRAM}'>Instagram</a> | <a href='{Config.YOUTUBE}'>YouTube</a>\n"
                f"└───────────────────────┘\n\n"
            
            )
            
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=Config.CHANNEL_LINK)]
            ])
            
            # Wahi same file wapas bhejo, naye mast format aur HTML ParseMode ke sath
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
                        final_name = "Downloaded File"
                        
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

            # Har link/file ke liye Box format generate karo
            for item in items_to_process:
                clean_title = clean_filename(item['name']).upper()
                file_size = item['size']
                short_link = item['link']
                
                image_path = get_image(clean_title)
                if not image_path: continue 

                final_download_link = short_link if short_link else Config.CHANNEL_LINK

                caption_text = (
                    f"══════════════════════\n"
                    f"<blockquote>📂 <code>{clean_title}</code> 📂</blockquote>\n"
                    f"══════════════════════\n"
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
                    f"├───────────────────────\n"
                    f"│ 👤 ADMIN: <b>{Config.OWNER_NAME}</b> ✨\n"
                    f"│ 🌐 <a href='{Config.TELEGRAM_USER}'>Telegram</a> | <a href='{Config.INSTAGRAM}'>Instagram</a> | <a href='{Config.YOUTUBE}'>YouTube</a>\n"
                    f"└───────────────────────┘\n\n"
                    f"👇 <b>Download Your File Below</b> 👇"
                )
                
                buttons_list = []
                if short_link:
                    buttons_list.append([InlineKeyboardButton("📥 Download File", url=short_link)])
                buttons_list.append([InlineKeyboardButton("📢 Join Channel", url=Config.CHANNEL_LINK)])
                
                buttons = InlineKeyboardMarkup(buttons_list)
                
                await client.send_photo(
                    chat_id=chat_id,
                    photo=image_path, 
                    caption=caption_text,
                    parse_mode=ParseMode.HTML, # HTML zaroori hai blockquote ke liye
                    reply_markup=buttons
                )

            await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"⚠️ Error aagaya: {e}")