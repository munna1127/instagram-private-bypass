import os
import subprocess
import threading
from flask import Flask
import telebot
from generate_gallery import parse_extracted_file, generate_html

app = Flask(__name__)

@app.route('/')
def home():
    return "🌐 Telegram Bot is alive and running on Render Web Service!"

# Environment Variables Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
# Admin ID ko int me convert karte hain safe execution ke liye
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(BOT_TOKEN)

# Helper function jo admin ko notification bhejega
def notify_admin(log_text):
    if ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f"🔔 **[BOT LOGGER]**\n{log_text}", parse_mode="Markdown")
        except Exception as e:
            print(f"Admin ko notify karne me dikkat aayi: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 **Welcome to VIP Media Extractor Bot**\n\n"
        "Mujhe kisi bhi account ka Username bhejo, mai uski automatic "
        "HTML gallery website tayaar karke dunga.\n\n"
        "👑 **Owner:** @tomar_ji_99"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")
    
    # Admin alert: Jab koi /start kare
    user = message.from_user
    log_info = (
        f"🚀 **Naya User Start Hua!**\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🆔 User ID: `{user.id}`\n"
        f"🏷️ Username: @{user.username or 'None'}"
    )
    notify_admin(log_info)

@bot.message_handler(func=lambda message: True)
def handle_username(message):
    username = message.text.strip()
    user = message.from_user
    
    # Admin alert: Har ek message aur search request par
    log_search = (
        f"🔍 **New Search Request!**\n"
        f"👤 User: {user.first_name} (@{user.username or 'None'})\n"
        f"🆔 ID: `{user.id}`\n"
        f"📝 Input Text: `{username}`"
    )
    notify_admin(log_search)
    
    if " " in username or username.startswith("/"):
        bot.reply_to(message, "❌ Kripya ek valid Instagram username bhejein (bina spaces ke).")
        return

    status_msg = bot.reply_to(message, f"⏳ **Searching Account:** `{username}`\nBypassing and links extraction is running... Please wait.", parse_mode="Markdown")

    try:
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
            notify_admin(f"⚠️ **Extraction Failed for @{user.username or 'None'}**\nTarget: `{username}`\nLog: `{stdout[:150]}`")
            return

        bot.edit_message_text("📦 **Status:** Links Extracted! Compiling interactive dashboard layout...", message.chat.id, status_msg.message_id, parse_mode="Markdown")

        posts_data = parse_extracted_file(input_filename)
        if posts_data:
            generate_html(posts_data, output_html="index.html")
            
            bot.edit_message_text("🚀 **Status:** Finalizing files and uploading data packet...", message.chat.id, status_msg.message_id, parse_mode="Markdown")
            
            caption_text = (
                f"🌐 **Smart Web Dashboard Generated!**\n\n"
                f"👤 **Target Account:** `{username}`\n"
                f"📊 **Data Split:** Dual View Mode Enabled\n\n"
                f"💡 _Isko download karein aur kisi bhi browser me open karke direct saari images/reels sahi order me dekhein._\n\n"
                f"👑 **Powered By:** @tomar_ji_99"
            )
            
            with open("index.html", 'rb') as html_file:
                bot.send_document(message.chat.id, html_file, caption=caption_text, parse_mode="Markdown")
                
            # Success notification to admin
            notify_admin(f"✅ **Success!** Gallery delivered to @{user.username or 'None'} for target `{username}`.")
                
            if os.path.exists(input_filename): os.remove(input_filename)
            if os.path.exists("index.html"): os.remove("index.html")
            
        else:
            bot.edit_message_text("❌ File toh bani par usme koi valid image/reel links nahi mile.", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Koi error aayi: {str(e)}", message.chat.id, status_msg.message_id)
        notify_admin(f"🚨 **System Error!**\nUser: @{user.username or 'None'}\nError: `{str(e)}`")

def run_bot():
    print("🤖 Telegram Bot thread started with Logger...")
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port)
