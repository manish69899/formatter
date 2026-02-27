from pyrogram import Client, filters
from pyromod import listen
import asyncio # TimeoutError ko handle karne ke liye

# --- GLOBAL MEMORY (User ka password yahan save hoga) ---
# Format: { chat_id : "PasswordString" } ya { chat_id : None }
# Note: Render par har 24 ghante me bot restart hota hai, to ye reset ho sakta hai. 
# Long term ke liye hum baad me MongoDB ya database laga sakte hain.
USER_PREFS = {}

@Client.on_message(filters.command("start") & filters.private)
async def start_and_set_mode(client, message):
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
                "🚀 **Setup Complete! Ab aap mujhe koi bhi File, Link ya Text bhej sakte hain.**"
            )
        else:
            USER_PREFS[chat_id] = reply # Password Save ho gaya
            await message.reply_text(
                f"✅ **Password Saved:** `{reply}`\nAb har file me ye password apne aap lag jayega.\n\n"
                "🚀 **Setup Complete! Ab aap mujhe koi bhi File, Link ya Text bhej sakte hain.**"
            )
            
    except asyncio.exceptions.TimeoutError:
        # Agar user 60 second tak reply na kare
        await message.reply_text("⏰ Time out ho gaya hai. Bot setup karne ke liye wapas `/start` bhejein.")
    except Exception as e:
        # Agar koi aur error aaye
        await message.reply_text(f"⚠️ Ek error aagaya: {e}\nDubara `/start` bhejein.")