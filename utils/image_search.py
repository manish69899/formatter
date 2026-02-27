import requests
import urllib.parse
import re
from config import Config

def get_real_thumbnail(full_title):
    """
    Ye function Title me se 'Main Keywords' nikal kar 
    Unsplash se HD Real Image layega.
    """
    # 0. API KEY CHECK
    # Agar key set nahi hai to seedha default image bhej do (Crash se bachne ke liye)
    if not Config.UNSPLASH_KEY or Config.UNSPLASH_KEY == "YOUR_UNSPLASH_ACCESS_KEY_HERE":
        print("⚠️ Unsplash Key missing in Config! Default image bhej rahe hain.")
        return "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1080"

    try:
        # 1. CLEANING: Extension aur faltu symbols hatao
        clean_text = str(full_title).rsplit('.', 1)[0]
        clean_text = re.sub(r'\.(pdf|zip|rar|mp4|mkv|exe|apk)$', '', clean_text, flags=re.IGNORECASE)
        clean_text = clean_text.replace("_", " ").replace("-", " ")
        
        # 2. KEYWORD EXTRACTION (Smart Logic)
        # In words ko ignore karna hai taaki search result acha aaye
        stopwords = [
            "of", "the", "in", "on", "at", "to", "a", "an", "for", "by", "with", 
            "file", "download", "pdf", "notes", "book", "class", "chapter", 
            "found", "different", "species", "ranchi", "part", "vol"
        ]
        
        words = clean_text.split()
        # Sirf wo words rakho jo stopwords nahi hain aur 3 letter se bade hain
        keywords = [w for w in words if w.lower() not in stopwords and len(w) > 3]
        
        # Agar keywords mile to top 2 use karo, warna "Study" use karo
        search_query = " ".join(keywords[:2]) if keywords else "Education Library"
        encoded_query = urllib.parse.quote(search_query) # URL me spaces safe rakhne ke liye
        
        print(f"🔍 Searching Unsplash Image for: {search_query}")

        # 3. UNSPLASH API REQUEST
        url = f"https://api.unsplash.com/search/photos?page=1&query={encoded_query}&client_id={Config.UNSPLASH_KEY}&per_page=1"
        
        response = requests.get(url)
        
        # Agar API limit cross ho gayi ya key galat hui to error handle karo
        if response.status_code != 200:
            print(f"⚠️ Unsplash API Error: Status Code {response.status_code}")
            return "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1080"

        data = response.json()
        
        if data and 'results' in data and data['results']:
            # Pehli image utha lo
            return data['results'][0]['urls']['regular']
        else:
            # Agar kuch na mile to ek Random Nature/Tech image dedo
            return "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1080"

    except Exception as e:
        print(f"⚠️ Unsplash Image Search Error: {e}")
        # Error aaye to ye default image bhej do
        return "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1080"