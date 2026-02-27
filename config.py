import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- ESSENTIAL BOT CREDENTIALS ---
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # --- BRANDING ---
    OWNER_NAME = os.getenv("OWNER_NAME", "ARYAN") 
    
    # --- LINKS ---
    TUTORIAL_VIDEO = os.getenv("TUTORIAL_VIDEO", "https://youtu.be/example") 
    DIRECT_PDF_LINK = os.getenv("DIRECT_PDF_LINK", "https://t.me/+AbCdEfGh...") 
    CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/YourChannel")
    
    # --- SOCIAL ---
    TELEGRAM_USER = os.getenv("TELEGRAM_USER", "https://t.me/YourID")
    INSTAGRAM = os.getenv("INSTAGRAM", "https://instagram.com/YourID")
    YOUTUBE = os.getenv("YOUTUBE", "https://youtube.com/YourID")
    
    # --- API KEYS ---
    UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

    # --- SYSTEM PATHS ---
    # Render par host karne ke liye hardcoded path ki jagah relative path 'images' use karna best hai.
    # Agar .env me koi path nahi hoga, to ye automatically usi folder me "images" naam ka folder dhoondega.
    LOCAL_IMAGES_PATH = os.getenv("LOCAL_IMAGES_PATH", "images")