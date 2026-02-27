import os
import random
from config import Config
# Fallback ke liye AI artist ko import kiya hai
from utils.ai_artist import get_smart_thumbnail 

def get_image(file_name="Document"):
    """
    Ye function pehle aapke Local PC/Render folder se random image uthayega.
    Agar folder nahi mila ya khali hua, toh automatically AI se generate kar dega.
    Supported: JPG, JPEG, PNG, WEBP
    """
    folder_path = Config.LOCAL_IMAGES_PATH
    
    # --- 1. LOCAL IMAGE LOGIC ---
    if os.path.exists(folder_path):
        all_files = os.listdir(folder_path)
        
        # Sirf Images ko filter karo (HEIC avoid kiya hai kyunki wo preview nahi deta)
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        images = [f for f in all_files if f.lower().endswith(valid_extensions)]
        
        if images:
            # Randomly ek select karo
            random_image = random.choice(images)
            full_path = os.path.join(folder_path, random_image)
            print(f"✅ Selected Local Image: {random_image}")
            return full_path
        else:
            print("⚠️ Folder me koi JPG/PNG image nahi mili!")
    else:
        print(f"⚠️ Error: Folder nahi mila! Path check karo: {folder_path}")

    # --- 2. AI IMAGE FALLBACK LOGIC ---
    # Agar upar ka code fail ho jata hai (image nahi milti), to ye AI ka use karega
    print("🤖 Nayi AI Image generate kar rahe hain...")
    
    # Ye wahi function hai jo abhi humne ai_artist.py me banaya tha
    return get_smart_thumbnail(file_name)