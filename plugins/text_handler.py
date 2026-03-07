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
    """File size ko smartly Bytes se KB/MB/GB me convert karta hai.
    Invalid inputs aur 0 bytes ko bhi perfectly handle karta hai."""
    
    # 1. SMART TYPE SAFETY: Agar API ne string bhej diya ho, toh usko number me badlo
    # Agar None ya kachra value aayi, toh crash hone se bachayega
    try:
        bytes_size = float(bytes_size)
    except (ValueError, TypeError):
        return "Unknown Size"

    # 2. ZERO YA NEGATIVE CHECK: 0 byte ki file ko properly "0 B" dikhayega
    if bytes_size <= 0:
        return "0 B"

    # 3. CONVERSION LOGIC (Added PB for PetaBytes just in case)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bytes_size < 1024.0:
            # 4. SMART FORMATTING: Agar last me .00 hai, toh usko hata kar clean look dega
            # Example: 5.00 MB ban jayega 5 MB. Aur 1.50 MB ban jayega 1.5 MB
            formatted_size = f"{bytes_size:.2f}".rstrip('0').rstrip('.')
            return f"{formatted_size} {unit}"
        
        bytes_size /= 1024.0
        
    return "Unknown Size"

def get_smart_file_details(filename):
    """Extension ke hisaab se Smart Emoji aur Format text nikalta hai.
    Programming languages aur un-registered extensions ko bhi handle karta hai."""
    
    filename_str = str(filename).strip()
    
    # Extension nikalne ka safe tarika
    if '.' in filename_str:
        ext = filename_str.split('.')[-1].lower()
    else:
        ext = ""

    # Dictionary mapping (Sabse bada aur advanced list)
    file_types = {
        # 📚 Documents & Media
        ("pdf",): ("📕", "PDF DOCUMENT"),
        ("mp4", "mkv", "avi", "mov", "webm"): ("🎬", "VIDEO"),
        ("zip", "rar", "7z", "tar", "gz", "iso"): ("🗜️", "ARCHIVE"),
        ("jpg", "jpeg", "png", "webp", "gif", "bmp", "svg"): ("🖼️", "IMAGE"),
        ("apk", "xapk", "apks"): ("📱", "ANDROID APP"),
        ("mp3", "m4a", "wav", "flac"): ("🎵", "AUDIO"),
        ("exe", "msi"): ("💻", "WINDOWS SOFTWARE"),
        ("mac", "dmg"): ("🍏", "MAC SOFTWARE"),
        ("doc", "docx", "rtf"): ("📝", "WORD DOCUMENT"),
        ("xls", "xlsx", "csv"): ("📊", "SPREADSHEET"),
        ("ppt", "pptx"): ("🖥️", "PRESENTATION"),
        ("txt", "log"): ("📄", "TEXT FILE"),
        
        # 👨‍💻 Programming & Web Languages
        ("py", "pyw", "ipynb"): ("🐍", "PYTHON SOURCE CODE"),
        ("html", "htm"): ("🌐", "HTML DOCUMENT"),
        ("css",): ("🎨", "CSS STYLESHEET"),
        ("js", "jsx"): ("⚡", "JAVASCRIPT CODE"),
        ("ts", "tsx"): ("📘", "TYPESCRIPT CODE"),
        ("c", "h"): ("⚙️", "C SOURCE CODE"),
        ("cpp", "hpp", "cxx"): ("⚙️", "C++ SOURCE CODE"),
        ("java",): ("☕", "JAVA SOURCE CODE"),
        ("php",): ("🐘", "PHP SCRIPT"),
        ("cs",): ("🔷", "C# SOURCE CODE"),
        ("go",): ("🐹", "GO SOURCE CODE"),
        ("rs",): ("🦀", "RUST SOURCE CODE"),
        ("rb",): ("💎", "RUBY SOURCE CODE"),
        ("swift",): ("🦅", "SWIFT SOURCE CODE"),
        ("kt", "kts"): ("🚀", "KOTLIN SOURCE CODE"),
        ("sql", "sqlite", "db"): ("🗄️", "DATABASE SCRIPT"),
        ("json", "xml", "yaml", "yml", "ini", "env"): ("🛠️", "CONFIG FILE"),
        ("sh", "bash", "zsh"): ("🐧", "LINUX SHELL SCRIPT"),
        ("bat", "cmd", "ps1"): ("📟", "WINDOWS SCRIPT")
    }

    # Default values
    emoji = "📂"
    form = "DOCUMENT"
    found = False

    # Check extension in our dictionary
    for extensions, details in file_types.items():
        if ext in extensions:
            emoji, form = details
            found = True
            break
    
    # SMART FALLBACK: Agar inke alawa koi aur naya format aaye (jaise .dart)
    if not found and ext:
        emoji = "📄"
        form = f"{ext.upper()} FILE" 

    return emoji, form, filename_str

def generate_hashtags(filename):
    """File ke naam se automatically trending aur clean hashtags banata hai.
    Smart Year Detection: Sirf 4 digit wale numbers ko 'Year' banayega, baaki aaltu-faltu numbers ignore honge."""
    
    # 1. Extension hatao safely
    name_without_ext = re.sub(r'\.[a-zA-Z0-9]+$', '', str(filename))
    
    # 2. Brackets, hyphens, underscores ko space me badlo taaki words properly alag ho
    clean_name = re.sub(r'[\_\-\(\)\[\]\{\}]', ' ', name_without_ext)
    
    # 3. Kam se kam 2 characters wale alphanumeric words nikalo
    words = re.findall(r'\b[a-zA-Z0-9]{2,}\b', clean_name)
    
    # 4. 🔥 SMART YEAR DETECTION
    valid_words = []
    for word in words:
        if word.isdigit():
            # Check length: Agar exactly 4 digit hai, toh 'Year' banao
            if len(word) == 4:
                valid_words.append(f"Year{word}")
            else:
                # 10-digit ya kisi aur length ka number ho, toh chhor do (skip)
                continue
        else:
            # Agar letters hain (e.g. Physics), toh normally add karo
            valid_words.append(word)
    
    # 5. Top 3 valid words ko capitalize karke list me daalo
    generated_tags = [f"#{word.capitalize()}" for word in valid_words[:3]]
    
    # 6. Default tags
    default_tags = [
        "#pyqera", 
        "#Notes",
        "#pyq"
    ]
    
    # 7. DUPLICATE REMOVER LOGIC
    final_tags = []
    seen_tags = set()
    
    for tag in generated_tags + default_tags:
        tag_lower = tag.lower() # Case-insensitive check
        if tag_lower not in seen_tags:
            final_tags.append(tag)
            seen_tags.add(tag_lower)
    
    # 8. List ko string me join karke return karo
    return " ".join(final_tags)

def extract_name_and_size(raw_name):
    """Text me se file size nikalta hai aur aaltu-faaltu emojis/text ekdum clean karta hai"""
    
    # 1. Size nikalne ka advanced tarika (Ab TB aur simple Bytes bhi support karega)
    # Matches formats like: 10 MB, 1.5GB, (200 KB), 500B
    size_match = re.search(r'\(?(\d+(?:\.\d+)?)\s*([kKmMgGtT]?[bB])\)?', raw_name)
    
    if size_match:
        # Number aur Unit ko alag nikal kar properly format karo (e.g., "1.5", "MB" -> "1.5 MB")
        num = size_match.group(1)
        unit = size_match.group(2).upper()
        size_str = f"{num} {unit}"
    else:
        size_str = "Unknown Size"
        
    # 2. Faltu Emojis aur Text ko hatao (Aur bhi naye Telegram emojis add kiye hain)
    garbage_patterns = [
        r'📁|📂|📄|💾|📥|✅|🔗|📌|✨|🔥',  # Common Telegram Emojis
        r'(?i)file name:\s*',             # "File Name:" (case insensitive)
        r'(?i)file link:\s*',             # "File Link:"
        r'(?i)name:\s*',                  # "Name:"
        r'(?i)link:\s*',                  # "Link:"
        r'\(\d+(?:\.\d+)?\s*[a-zA-Z]+\)', # (Size brackets hatane ke liye)
        r'\d+(?:\.\d+)?\s*[kKmMgGtT][bB]' # Bina brackets wale size hatane ke liye
    ]
    
    clean_name = raw_name
    for pattern in garbage_patterns:
        clean_name = re.sub(pattern, '', clean_name)
        
    # 3. Agar naam ke aage/peechhe koi hyphen (-) ya pipe (|) ya colon (:) reh gaya ho toh saaf karo
    clean_name = re.sub(r'^[\-\|:\s]+|[\-\|:\s]+$', '', clean_name)
    
    # 4. Double/Triple spaces ko single space me badlo taaki naam neat dikhe
    clean_name = re.sub(r'\s{2,}', ' ', clean_name)
    
    # 5. Final strip karke return karo
    final_name = clean_name.strip()
    
    # Agar saaf karne ke baad naam completely gayab ho jaye, to ek default naam de do
    if not final_name:
        final_name = "Downloaded_File"
        
    return final_name, size_str



# Filters me Photo, Document, Text sab allowed hai
@Client.on_message((filters.text | filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def format_message(client, message):
    if message.text and message.text.startswith("/"): return

    chat_id = message.chat.id
    status_msg = await message.reply_text("⏳ **Analyzing & Upgrading message... Please wait!**")
    
    # Password Section
    saved_pass = USER_PREFS.get(chat_id) 
    pass_section = (f"│\n│ 🔐 <b>FILE PASSWORD:</b>\n│ 👉 <b>{saved_pass}</b> 👈\n│") if saved_pass else ""

    try:
        # ==========================================
        # SCENARIO 1: AGAR USER NE DIRECT FILE BHEJI HAI
        # ==========================================
        if message.media: 
            
            if message.photo:
                # Telegram compressed photos ka naam hata deta hai, 
                # isliye hum Professional Timestamp logic use karenge.
                msg_date = message.date
                date_str = msg_date.strftime("%Y%m%d_%H%M%S") if msg_date else "Unknown"
                file_name = f"IMG_{date_str}.jpg"
                file_size = format_size(message.photo.file_size) if hasattr(message.photo, 'file_size') else "Unknown Size"
            else:
                media = getattr(message, message.media.value)
                # Agar direct document hai, toh asli naam yahan se nikal aayega
                file_name = getattr(media, "file_name", None)
                if not file_name: # Fallback agar document ka bhi naam missing ho
                    # Fallback extension agar mime_type ho
                    mime_ext = ".bin"
                    if hasattr(media, "mime_type") and media.mime_type:
                        mime_ext = "." + media.mime_type.split("/")[-1]
                    file_name = f"Unknown_Media_File{mime_ext}"
                    
                file_size = format_size(getattr(media, "file_size", 0))

            # --- Extract & Format File Metadata ---
            file_emoji, file_format, exact_title = get_smart_file_details(file_name)
            hashtags = generate_hashtags(exact_title)

            # ULTRA-PREMIUM CAPTION
            caption_text = (
                f"\n"
                f"<blockquote>{file_emoji} <b>FILE:</b>\n<b>{exact_title}</b></blockquote>\n"
                f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                f"│\n"
                f"│ ⚙️ <b>Format:</b> {file_format}\n"
                f"│ 💾 <b>Size:</b> {file_size}\n"
                f"│ 🛡️ <b>Status:</b> Safe & Verified\n"
                f"│\n"
                f"│ 🔓 <b>Direct File :</b>\n"
                f"│ <a href='{Config.DIRECT_PDF_LINK}'>Click to Join</a>\n"
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
            
            # Caption Length Check (Telegram Limit is 1024)
            if len(caption_text) > 1024:
                caption_text = caption_text[:1020] + "..."


# ==========================================
            # PERFECT SHARE BUTTON LOGIC (Fixed Layout)
            # ==========================================
            # Pura message ek hi string mein rakhenge taaki link neeche hi aaye
            raw_share_text = f"🚀 Found an amazing file: {exact_title}!\n\n👇 Get it here 👇\n{Config.CHANNEL_LINK}"
            
            # Sirf 'text' parameter bhejenge Telegram ko, bina alag se 'url' parameter diye
            share_params = {"text": raw_share_text}
            encoded_query = urllib.parse.urlencode(share_params)
            
            share_url = f"https://t.me/share/url?{encoded_query}"

            # Inline Buttons Layout
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
                    f"<blockquote>{file_emoji} <b>FILE:</b>\n<b>{exact_title}</b></blockquote>\n"
                    f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                    f"│\n"
                    f"│ 🛡️ <b>Status:</b> Safe & Verified\n"
                    f"│\n"
                    f"│ 📥 <b>File Download Link:</b>\n"
                    f"│ <a href='{final_download_link}'>Click Here to Download</a>\n"
                    f"│\n"
                    f"│ 🔓 <b>Direct File :</b>\n"
                    f"│ <a href='{Config.DIRECT_PDF_LINK}'>Click Here to Join </a>\n"
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
                    # Caption Length Check for Image
                    if len(caption_text) > 1024:
                        caption_text = caption_text[:1020] + "..."
                        
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

    except Exception as e:
        print(f"Error in format_message: {e}")
        try:
            await status_msg.edit(f"⚠️ **Error Occurred:**\n`{e}`\n\n_Please try again or contact Admin._")
        except:
            pass # Agar edit fail ho jaye (e.g. message delete ho gaya ho)
            
    finally:
        # Guarantee that the analyzing message is deleted if it hasn't been edited to an error state
        try:
             # Hum tabhi delete karenge jab text "Error Occurred" na ho
            if "Error" not in status_msg.text:
                await status_msg.delete()
        except:
            pass