import os
import random
from config import Config
from utils.ai_artist import get_smart_thumbnail 

# Pillow library import kar rahe hain dimensions fix karne ke liye
try:
    from PIL import Image
except ImportError:
    Image = None
    print("⚠️ Pillow library install nahi hai. Please run: pip install Pillow")

def fix_image_dimensions(image_path):
    """
    Ye function check karta hai ki image Telegram ke liye theek hai ya nahi.
    Agar image bahut badi ya lambi hui, toh automatically resize kar dega.
    """
    if Image is None:
        return image_path  # Agar Pillow nahi hai to original image hi bhej do
    
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Telegram dimensions me problem tab deta hai jab resolution bahut high ho
            # Hum isko max 1920x1920 me compress kar denge (HD Quality, No Error)
            if width > 1920 or height > 1920 or (width / height > 5) or (height / width > 5):
                print(f"🔧 Resizing large/long image: {image_path} (Original: {width}x{height})")
                
                # Image ko resize karo (Aspect ratio maintain rahega)
                img.thumbnail((1920, 1920))
                
                # Save as a temporary file taaki original file kharab na ho
                temp_path = "temp_fixed_image.jpg"
                
                # Agar PNG/WebP hai jisme transparency ho, to usko RGB me convert karo
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                    
                img.save(temp_path, "JPEG", quality=90)
                return temp_path
                
    except Exception as e:
        print(f"⚠️ Image resize error: {e}")
        
    return image_path

def get_image(file_name="Document"):
    """
    Ye function Local folder se shuffle karke random image uthayega.
    Agar local nahi mila, to AI generate karega.
    """
    folder_path = Config.LOCAL_IMAGES_PATH
    
    # --- 1. LOCAL IMAGE LOGIC (Improved Randomness) ---
    if os.path.exists(folder_path):
        all_files = os.listdir(folder_path)
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
        
        # Sari images ki list banao
        images = [f for f in all_files if f.lower().endswith(valid_extensions)]
        
        if images:
            # 💡 Logic: Puri list ko shuffle kar do taaki randomness badh jaye
            random.shuffle(images)
            # 💡 Logic: Shuffled list me se koi bhi ek random pick karo
            random_image = random.choice(images)
            
            full_path = os.path.join(folder_path, random_image)
            print(f"✅ Random Local Image Selected: {random_image}")
            
            # Bhejne se pehle dimensions theek karo
            safe_image_path = fix_image_dimensions(full_path)
            return safe_image_path
        else:
            print("⚠️ Folder me koi valid image nahi mili!")
    else:
        print(f"⚠️ Error: Folder path galat hai -> {folder_path}")

    # --- 2. AI FALLBACK ---
    print("🤖 Local images kam hain ya nahi mili, AI use kar rahe hain...")
    return get_smart_thumbnail(file_name)