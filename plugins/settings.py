import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from pyromod import listen

# --- GLOBAL MEMORY (User ka password yahan save hoga) ---
USER_PREFS = {}

# ==========================================
# 🎛️ CUSTOM KEYBOARD DESIGN
# ==========================================
# Yeh keyboard user ko hamesha chat ke niche dikhega
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📋 Menu"), KeyboardButton("ℹ️ About")]
    ],
    resize_keyboard=True,  # Keyboard ko screen ke hisaab se chhota kar dega
    is_persistent=True     # Keyboard hamesha open rahega
)

# ==========================================
# 🚀 START COMMAND & PASSWORD SETUP
# ==========================================
@Client.on_message(filters.command("start") & filters.private)
async def start_and_set_mode(client, message):
    
    # 🔥 PENDING UPDATES CLEANER (Spam Rokne Ke Liye)
    if message.date and (time.time() - message.date.timestamp() > 60):
        return

    chat_id = message.chat.id
    user_name = message.from_user.first_name or "User"
    
    # Step 1: Welcome & Pucho kya karna hai
    try:
        welcome_text = (
            f"👋 Hello **{user_name}**!\n\n"
            "🤖 **Welcome to Box Formatter Bot!**\n"
            "Aap mujhe koi bhi file, link ya text bhej sakte hain aur main use ek perfect format me convert kar dunga.\n\n"
            "⚙️ **Bot Settings (1st Step):**\n"
            "Kya aap saari files ke liye ek **Default Password** set karna chahte hain?\n\n"
            "👉 Agar **YES**, to Password type karein (e.g., `Aryan123`).\n"
            "👉 Agar **NO**, to `No` likh dein (Koi password nahi lagega)."
        )
        
        ask = await client.ask(
            chat_id,
            welcome_text,
            timeout=60
        )
        
        reply = ask.text
        
        if reply.lower() in ["no", "n", "skip", "none"]:
            USER_PREFS[chat_id] = None # Password Mode OFF
            await message.reply_text(
                "✅ **Password Mode Disabled.**\nAb files bina password ke aayengi.\n\n"
                "🚀 **Setup Complete! Ab aap mujhe koi bhi File, Link ya Text bhej sakte hain.**",
                reply_markup=main_keyboard # Setup ke baad keyboard show karo
            )
        else:
            USER_PREFS[chat_id] = reply # Password Save ho gaya
            await message.reply_text(
                f"✅ **Password Saved:** `{reply}`\nAb har file me ye password apne aap lag jayega.\n\n"
                "🚀 **Setup Complete! Ab aap mujhe koi bhi File, Link ya Text bhej sakte hain.**",
                reply_markup=main_keyboard # Setup ke baad keyboard show karo
            )
            
    except asyncio.exceptions.TimeoutError:
        # Agar user 60 second tak reply na kare
        await message.reply_text("⏰ Time out ho gaya hai. Bot setup karne ke liye wapas `/start` bhejein.")
    except Exception as e:
        # Agar koi aur error aaye
        await message.reply_text(f"⚠️ Ek error aagaya: {e}\nDubara `/start` bhejein.")

# ==========================================
# 📋 MENU COMMAND / BUTTON HANDLER
# ==========================================
# Yeh '/menu' type karne par ya '📋 Menu' button dabane dono par chalega
@Client.on_message((filters.command("menu") | filters.regex("^📋 Menu$")) & filters.private)
async def menu_command(client, message):
    
    # Current password check karne ke liye
    chat_id = message.chat.id
    current_pass = USER_PREFS.get(chat_id, "None (Disabled)")
    
    menu_text = (
        "📋 **MAIN MENU**\n\n"
        "Yahan aap bot ki settings aur features dekh sakte hain:\n\n"
        f"🔑 **Current Default Password:** `{current_pass}`\n\n"
        "📝 **How to use:**\n"
        "1. Koi bhi File (PDF, Video, etc.) bhejo.\n"
        "2. Koi bhi Link bhejo.\n"
        "3. Main use instantly aapke custom format me design kar dunga.\n\n"
        "🔄 Password change karne ke liye wapas `/start` dabayein."
    )
    await message.reply_text(menu_text, reply_markup=main_keyboard)

# ==========================================
# ℹ️ ABOUT COMMAND / BUTTON HANDLER
# ==========================================
# Yeh '/about' type karne par ya 'ℹ️ About' button dabane dono par chalega
@Client.on_message((filters.command("about") | filters.regex("^ℹ️ About$")) & filters.private)
async def about_command(client, message):
    about_text = (
        "ℹ️ **ABOUT THIS BOT**\n\n"
        "🤖 **Bot Name:** Box Formatter Bot\n"
        "👨‍💻 **Developer:** Aryan \n"
        "⚙️ **Language:** Python 3\n"
        "📚 **Library:** Pyrogram\n\n"
        "Yeh bot files aur links ko premium format me convert karta hai jisme emojis, file size, aur share buttons hote hain."
    )
    await message.reply_text(about_text, reply_markup=main_keyboard)