import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardRemove  # 👈 Keyboard hatane ke liye naya import
from pyromod import listen

# --- GLOBAL MEMORY STORE ---
USER_PREFS = {}

# 📌 IMAGES PATHS (Aapke 'assets' folder ke hisaab se)
WELCOME_IMAGE = "assets/welcome.jpg"
QR_IMAGE_PATH = "assets/qr.jpg"

# ==========================================
# 🚀 INITIALIZATION & SETUP (/start)
# ==========================================
@Client.on_message(filters.command("start") & filters.private)
async def start_and_set_mode(client, message):
    if message.date and (time.time() - message.date.timestamp() > 60):
        return
   
    chat_id = message.chat.id
    user_name = message.from_user.first_name or "User"
    
    try:
        # 1. Sabse pehle Welcome Image bhejo
        try:
            await client.send_photo(
                chat_id=chat_id,
                photo=WELCOME_IMAGE,
                caption=f"⚡ **SYSTEM ONLINE** ⚡\nWelcome aboard, {user_name}!"
            )
        except Exception as e:
            print(f"Welcome Image Error: {e}") 
            pass

        # 2. Setup wala question
        welcome_text = (
            f"👋 Greetings, **{user_name}**.\n\n"
            "🤖 **Welcome to the Box Formatter Engine.**\n"
            "I am an advanced automated system designed to parse, format, and enhance your files, links, and text into premium quality outputs.\n\n"
            "⚙️ **Initialization (Step 1 of 1):**\n"
            "Would you like to configure a **Global Default Password** for your upcoming files?\n\n"
            "👉 Reply with your exact password (e.g., `SecurePass123`) to set it.\n"
            "👉 Reply with `No`, `Skip`, or `None` to proceed without any password configuration."
        )
        
        ask = await client.ask(chat_id, welcome_text, timeout=60)
        reply = ask.text.strip()
        
        if reply.lower() in ["no", "n", "skip", "none"]:
            USER_PREFS[chat_id] = None 
            await message.reply_text(
                "✅ **Security Mode: OFF.**\nFiles will be processed and formatted without password protection.\n\n"
                "🚀 **System Ready! You may now forward any File, Media, Link, or Text to begin processing.**",
                reply_markup=ReplyKeyboardRemove() # 👈 Yeh line screen se purana keyboard hata degi
            )
        else:
            USER_PREFS[chat_id] = reply 
            await message.reply_text(
                f"✅ **Security Protocol Updated.**\nDefault Password configured as: `{reply}`\nAll subsequent outputs will display this key.\n\n"
                "🚀 **System Ready! You may now forward any File, Media, Link, or Text to begin processing.**",
                reply_markup=ReplyKeyboardRemove() # 👈 Yeh line screen se purana keyboard hata degi
            )
            
    except asyncio.exceptions.TimeoutError:
        await message.reply_text("⏳ **Session Expired.** The setup process timed out. Please send `/start` to re-initialize the configuration.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.reply_text(f"⚠️ **System Exception:** `{e}`\nPlease attempt to restart the engine using `/start`.", reply_markup=ReplyKeyboardRemove())

# ==========================================
# 📋 DASHBOARD / MENU COMMAND
# ==========================================
@Client.on_message(filters.command("menu") & filters.private)
async def menu_command(client, message):
    chat_id = message.chat.id
    current_pass = USER_PREFS.get(chat_id, "None (Disabled)")
    
    menu_text = (
        "📋 **CONTROL PANEL**\n\n"
        "Monitor your current configuration and system parameters below:\n\n"
        f"🔑 **Active Encryption Key:** `{current_pass}`\n\n"
        "📝 **Operational Guidelines:**\n"
        "1. Upload or forward any Media/Document.\n"
        "2. Submit direct download URLs or Text payloads.\n"
        "3. The engine will instantly execute the formatting protocols.\n\n"
        "🔄 To reconfigure your security key, simply execute `/start` again."
    )
    await message.reply_text(menu_text)

# ==========================================
# ❓ HELP COMMAND
# ==========================================
@Client.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    help_text = (
        "🛠️ **SUPPORT & DOCUMENTATION**\n\n"
        "Need assistance operating the engine? Here is the protocol:\n\n"
        "🔹 **Files:** Just forward any file to me. I'll automatically rename, size, add emojis, and generate smart hashtags.\n"
        "🔹 **Links:** Send raw links. I will parse them and attach an aesthetic UI frame.\n"
        "🔹 **Passwords:** Use `/start` to globally lock all outgoing files with a password.\n\n"
        "If you encounter critical bugs, execute `/contribute` to reach the developer."
    )
    await message.reply_text(help_text)

# ==========================================
# 💎 DONATE COMMAND (Financial Support)
# ==========================================
@Client.on_message(filters.command("donate") & filters.private)
async def donate_command(client, message):
    
    donate_text = (
        "💎 **SUPPORT THE BOT** 💎\n\n"
        "Keeping this bot running 24/7, lightning-fast, and completely ad-free requires constant effort and real server costs.\n\n"
        "If this bot saves your time and makes your study life easier, please consider supporting the project. Your small contribution helps us keep this service alive for everyone.\n\n"
        "👨‍💻 **Developer:** Aryan (a.k.a 𝖑𝖔𝖈𝖆𝖑𝖍𝖔𝖘𝖙 )\n"
        "💬 **Contact:** @coolegepyqbot\n\n"
        "☕ **Buy me a coffee / Donate:**\n"
        "👉 **UPI ID:** `cyloc@ibl` (Tap to copy)\n\n"
        "📷 _You can also scan the attached QR code to contribute directly._\n\n"
        "_\"Because servers don't pay for themselves!\"_"
    )
    
    try:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=QR_IMAGE_PATH,
            caption=donate_text
        )
    except Exception as e:
        print(f"QR Code Error: {e}")
        await message.reply_text(donate_text)

# ==========================================
# 📚 CONTRIBUTE COMMAND (Study Material Sharing)
# ==========================================
@Client.on_message(filters.command("contribute") & filters.private)
async def contribute_command(client, message):
    
    contribute_text = (
        "📚 **SHARE MATERIALS & HELP JUNIORS** 📚\n\n"
        "Knowledge grows when you share it! We are building a massive, free collection of study materials to help students prepare for their exams without any struggle.\n\n"
        "If you have good handwritten notes, PYQs, reference books, or summaries, we humbly request you to share them with us. \n\n"
        "Your one small contribution today can save hundreds of hours of tension for a junior tomorrow. Let's build a helpful community together!\n\n"
        "📩 **How to Contribute:**\n"
        "Simply upload or forward your PDFs and Notes directly to this bot, or send them to the admin at @coolegepyqbot.\n\n"
        "✨ _We rise by lifting others. Be the senior you wish you had!_ ✨"
    )
    
    await message.reply_text(
        contribute_text, 
        disable_web_page_preview=True
    )

# ==========================================
# ℹ️ SYSTEM INFO / ABOUT COMMAND
# ==========================================
@Client.on_message(filters.command("about") & filters.private)
async def command_about(client, message):
    about_text = (
        "💻 **SYSTEM INFORMATION**\n\n"
        "🤖 **Core Engine:** Box Bot\n"
        "👨‍💻 **Lead Developer:** Aryan (a.k.a *localhost*)\n"
        "⚙️ **Tech Stack:** Python 3 | Pyrogram Asynchronous Framework\n"
        "⚡ **Performance:** High-speed parsing, automated metadata extraction, and premium UI generation.\n\n"
        "_\"Writing code that formats your chaos into absolute perfection.\"_\n\n"
        "🔒 **Access & Authorization:**\n"
        "This instance is strictly maintained and monitored. To request deployment, report bugs, or gain usage access, establish a secure connection with the developer.\n\n"
        "📩 **Contact Developer:** @coolegepyqbot" 
    )
    await message.reply_text(about_text, disable_web_page_preview=True)