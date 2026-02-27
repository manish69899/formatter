import urllib.parse
import random

def generate_thumbnail(prompt_text):
    """
    Ye function Pollinations.ai (Free API) ko use karke
    text ke basis par image ka URL generate karega.
    """
    try:
        # 1. Text Cleanup (Zaroori hai taaki AI ko clean title mile)
        clean_text = str(prompt_text).rsplit('.', 1)[0]
        clean_text = clean_text.replace("_", " ").replace("-", " ")
        clean_text = " ".join(clean_text.split())
        
        if not clean_text:
            clean_text = "Important Document"

        # 2. Prompt ko URL safe banao
        # Hum prompt ko thoda enhance karenge taaki image achi bane
        enhanced_prompt = f"A professional, attractive document cover poster titled '{clean_text}'. High quality, vibrant colors, digital art style, clean typography, 4k resolution."
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        
        # 3. Random Seed (Har baar ek unique aur fresh image ke liye)
        seed = random.randint(1, 999999)

        # 4. API URL (Pollinations.ai free endpoint)
        # Hum portrait aspect ratio (2:3) maang rahe hain poster jaisa
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=768&height=1024&seed={seed}&model=flux"
        
        # NOTE for FREE API:
        # Ye API kabhi-kabhi slow ho sakti hai ya down ho sakti hai.
        # Commercial use ke liye DALL-E 3 use karna chahiye.
        
        return image_url

    except Exception as e:
        print(f"⚠️ Image Generation Error: {e}")
        # Agar error aaye to ek default professional document image bhej do
        # Isse aapka bot fail/crash nahi hoga
        return "https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=768&q=80"