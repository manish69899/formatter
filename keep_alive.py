from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is Alive and Running on Render!"

def run():
    # Render port 8080 or process.env.PORT automatically assign karta hai
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()