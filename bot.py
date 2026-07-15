import os
import subprocess
import threading
from flask import Flask
import telebot
from generate_gallery import parse_extracted_file, generate_html

# Dummy Flask App taaki Render Free Web Service deploy ho sake
app = Flask(__name__)

@app.route('/')
def home():
    return "🌐 Telegram Bot is alive and running on Render Web Service!"

# Telegram Bot Setup
BOT_TOKEN = os.getenv("BOT_TOKEN", "8051346795:AAFSmNVmB_QVCEIDUydEDDxqacAYeg3Gqsg")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Mujhe kisi bhi account ka Username bhejo, mai uski extracted files aur HTML gallery generate karke dunga.")

@bot.message_handler(func=lambda message: True)
def handle_username(message):
    username = message.text.strip()
    
    if " " in username or username.startswith("/"):
        bot.reply_to(message, "❌ Kripya ek valid Instagram username bhejein (bina spaces ke).")
        return

    status_msg = bot.reply_to(message, f"⏳ {username} ke liye bypassing aur link extraction shuru ho raha hai... Isme thoda samay lag sakta hai.")

    try:
        # 1. Tumhari poc.py ko background mein chalana
        process = subprocess.Popen(
            ['python', 'poc.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=f"{username}\n")
        
        input_filename = "extracted_urls.txt"
        
        if not os.path.exists(input_filename):
            bot.edit_message_text(f"❌ Extraction fail ho gaya. `poc.py` ne file generate nahi ki.\nLog: {stdout[:200]}", message.chat.id, status_msg.message_id)
            return

        bot.edit_message_text("📦 Links extract ho gaye! Ab unique gallery website generate ho rahi hai...", message.chat.id, status_msg.message_id)

        # 2. Gallery HTML generate karna
        posts_data = parse_extracted_file(input_filename)
        if posts_data:
            generate_html(posts_data, output_html="index.html")
            
            bot.edit_message_text("🚀 Kaam poora hua! Files bheji jaa rahi hain...", message.chat.id, status_msg.message_id)
            
            # 3. Documents user ko bhej dena
            with open(input_filename, 'rb') as txt_file:
                bot.send_document(message.chat.id, txt_file, caption=f"📄 Extracted URLs for {username}")
                
            with open("index.html", 'rb') as html_file:
                bot.send_document(message.chat.id, html_file, caption=f"🌐 Smart HTML Gallery for {username}\n(Isko download karke browser me kholien)")
                
            # Clean up (Optional)
            if os.path.exists(input_filename): os.remove(input_filename)
            if os.path.exists("index.html"): os.remove("index.html")
            
        else:
            bot.edit_message_text("❌ File toh bani par usme koi valid image/reel links nahi mile.", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Koi error aayi: {str(e)}", message.chat.id, status_msg.message_id)

# Bot polling ko ek alag background thread me chalane ke liye function
def run_bot():
    print("🤖 Telegram Bot thread started...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Bot ko alag thread me start karo taaki Flask server block na ho
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Flask app ko Render ke asigned PORT par run karo
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port)

