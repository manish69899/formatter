import logging
from pyrogram import Client
import pyromod # Ye import zaroori hai 'client.ask' feature ke liye
from config import Config

# Agar aapne keep_alive.py file banayi hai (Render ke liye), to is line ko uncomment karein:
from keep_alive import keep_alive 

# --- LOGGING SETUP ---
# Console par errors aur info clear dekhne ke liye
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Bot")

# --- BOT INITIALIZATION ---
# 'plugins' folder me rakhi saari files automatically sync aur load ho jayengi
app = Client(
    "BoxFormatterBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    # 1. Start Web Server (Taaki Render bot ko sleep mode me na daale)
    try:
        logger.info("🌐 Web Server Start ho raha hai...")
        keep_alive()  
    except Exception as e:
        logger.error(f"⚠️ Web Server start karne me error: {e}")

    # 2. Start Telegram Bot
    logger.info("🤖 Box Bot Started! Password puchne aur format karne ke liye ready...")
    
    try:
        app.run()
    except Exception as e:
        logger.error(f"❌ Bot crash ho gaya: {e}")