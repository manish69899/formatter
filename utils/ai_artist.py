import urllib.parse
import random
# requests import yahan se hata diya hai kyunki hum seedha URL return kar rahe hain, 
# aur Pyrogram automatically URL se image fetch karke bhej deta hai.

def get_smart_thumbnail(file_name):
    """
    Ye function File Name ko 'Professional 3D Art' ya Cover me convert karega.
    """
    try:
        # 1. Cleaning: Extension aur faltu symbols hatao
        # Pehle file extension hatate hain (agar hai to)
        clean_text = str(file_name).rsplit('.', 1)[0]
        # Phir special characters ko space se replace karte hain
        clean_text = clean_text.replace("_", " ").replace("-", " ").replace(".", " ")
        # Extra spaces hatao
        clean_text = " ".join(clean_text.split())
        
        # Agar cleaning ke baad text empty ho jaye, toh ek default naam de do
        if not clean_text:
            clean_text = "Important File"
        
        # 2. PROMPT ENGINEERING (Isse image aur zyada sundar banegi)
        # Hum random styles use karenge taaki har image alag dikhe
        styles = [
            "soft 3d render, isometric icon, high quality, vibrant colors, trending on artstation",
            "cute digital art illustration, vector style, flat design, freepik style",
            "cinematic lighting, 4k, highly detailed, professional document cover",
            "cyberpunk glowing style, dark theme, neon accents, highly detailed 8k render" # Ek naya cool style add kiya hai
        ]
        selected_style = random.choice(styles)
        
        # Final Prompt: "Typography title" add karne se AI kabhi-kabhi text ko image me achhe se likh deta hai
        final_prompt = f"Typography text '{clean_text}', {selected_style}"
        encoded_prompt = urllib.parse.quote(final_prompt)
        
        # 3. POLLINATIONS AI (Best for Free 3D/Art Generation)
        # Seed use karne se image alag-alag aati hai aur unique lagti hai
        seed = random.randint(1, 999999)
        
        # Hum 1280x720 (Landscape) maang rahe hain jo Telegram par ekdum perfect dikhta hai
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1280&height=720&seed={seed}&model=flux"
        
        return image_url

    except Exception as e:
        print(f"⚠️ AI Art Error: {e}")
        # Agar AI API fail ho jaye, to ek default 'Professional File' image bhej do
        return "https://images.unsplash.com/photo-1618044733300-9472054094ee?auto=format&fit=crop&w=1280"