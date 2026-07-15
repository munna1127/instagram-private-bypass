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
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(BOT_TOKEN)

# Helper function jo admin ko notification bhejega (HTML Mode)
def notify_admin(log_text):
    if ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f"🔔 <b>[BOT LOGGER]</b>\n{log_text}", parse_mode="HTML")
        except Exception as e:
            print(f"Admin ko notify karne me dikkat aayi: {e}")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🤖 <b>Welcome to VIP Media Extractor Bot</b>\n\n"
        "Mujhe kisi bhi account ka Username bhejo, mai uski automatic "
        "HTML gallery website tayaar karke dunga.\n\n"
        "👑 <b>Owner:</b> @tomar_ji_99"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")
    
    # Admin alert: Jab koi /start kare
    user = message.from_user
    log_info = (
        f"🚀 <b>Naya User Start Hua!</b>\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🏷️ Username: @{user.username or 'None'}"
    )
    notify_admin(log_info)

@bot.message_handler(func=lambda message: True)
def handle_username(message):
    username = message.text.strip()
    user = message.from_user
    
    # Admin alert: Har ek message aur search request par
    log_search = (
        f"🔍 <b>New Search Request!</b>\n"
        f"👤 User: {user.first_name} (@{user.username or 'None'})\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📝 Input Text: <code>{username}</code>"
    )
    notify_admin(log_search)
    
    if " " in username or username.startswith("/"):
        bot.reply_to(message, "❌ Kripya ek valid Instagram username bhejein (bina spaces ke).")
        return

    status_msg = bot.reply_to(message, f"⏳ <b>Searching Account:</b> <code>{username}</code>\nBypassing and links extraction is running... Please wait.", parse_mode="HTML")

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
            notify_admin(f"⚠️ <b>Extraction Failed for @{user.username or 'None'}</b>\nTarget: <code>{username}</code>\nLog: <code>{stdout[:150]}</code>")
            return

        bot.edit_message_text("📦 <b>Status:</b> Links Extracted! Compiling interactive dashboard layout...", message.chat.id, status_msg.message_id, parse_mode="HTML")

        posts_data = parse_extracted_file(input_filename)
        if posts_data:
            generate_html(posts_data, output_html="index.html")
            
            bot.edit_message_text("🚀 <b>Status:</b> Finalizing files and uploading data packet...", message.chat.id, status_msg.message_id, parse_mode="HTML")
            
            caption_text = (
                f"🌐 <b>Smart Web Dashboard Generated!</b>\n\n"
                f"👤 <b>Target Account:</b> <code>{username}</code>\n"
                f"📊 <b>Data Split:</b> Dual View Mode Enabled\n\n"
                f"💡 <i>Isko download karein aur kisi bhi browser me open karke direct saari images/reels sahi order me dekhein.</i>\n\n"
                f"👑 <b>Powered By:</b> @tomar_ji_99"
            )
            
            with open("index.html", 'rb') as html_file:
                bot.send_document(message.chat.id, html_file, caption=caption_text, parse_mode="HTML")
                
            notify_admin(f"✅ <b>Success!</b> Gallery delivered to @{user.username or 'None'} for target <code>{username}</code>.")
                
            if os.path.exists(input_filename): os.remove(input_filename)
            if os.path.exists("index.html"): os.remove("index.html")
            
        else:
            bot.edit_message_text("❌ File toh bani par usme koi valid image/reel links nahi mile.", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Koi error aayi: {str(e)}", message.chat.id, status_msg.message_id)
        notify_admin(f"🚨 <b>System Error!</b>\nUser: @{user.username or 'None'}\nError: <code>{str(e)}</code>")

def run_bot():
    print("🤖 Telegram Bot thread started with HTML Logger...")
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port)
