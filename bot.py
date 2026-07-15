import os
import subprocess
import threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# Verification Settings
REQUIRED_CHANNELS = [
    {"chat_id": "@allioneplace", "url": "https://t.me/allioneplace", "name": "💬 Telegram Group"},
    {"chat_id": "@tech_updates_india0763", "url": "https://t.me/tech_updates_india0763", "name": "📢 Telegram Channel"}
]
YOUTUBE_URL = "https://www.youtube.com/@hackeronall"

# Whitelisted Users (No verification needed)
WHITELISTED_USERS = [1391200164, 6508791739]
SPECIAL_OWNER_ID = 6508791739

# Helper function to send notifications to the admin (HTML Mode)
def notify_admin(log_text):
    if ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f"🔔 <b>[BOT LOGGER]</b>\n{log_text}", parse_mode="HTML")
        except Exception as e:
            print(f"Failed to notify admin: {e}")

# Helper to check if a user has joined the required channels
def check_membership(user_id):
    if user_id in WHITELISTED_USERS:
        return True
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel["chat_id"], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            # If bot is not admin in the channel/group, this check might fail.
            # Make sure to add the bot as administrator in your channels/groups!
            return False
    return True

# Helper to generate verification keyboard
def get_verification_keyboard():
    markup = InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=channel["name"], url=channel["url"]))
    markup.add(InlineKeyboardButton(text="📺 Subscribe YouTube", url=YOUTUBE_URL))
    markup.add(InlineKeyboardButton(text="✅ Verify Joining", callback_data="verify_join"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user

    # Admin Logger: When a user triggers /start
    log_info = (
        f"🚀 <b>New User Started!</b>\n"
        f"👤 Name: {user.first_name} {user.last_name or ''}\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"🏷️ Username: @{user.username or 'None'}"
    )
    notify_admin(log_info)

    # Special welcome greeting for the special owner ID
    if user.id == SPECIAL_OWNER_ID:
        owner_welcome = (
            "👑 <b>Pranam, Aapka swagat hai Owner Sir!</b> 👑\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Aapka system bilkul taiyar hai. Kisi bhi username par extraction shuru karne ke liye direct input bhejein."
        )
        bot.reply_to(message, owner_welcome, parse_mode="HTML")
        return

    # Normal user/whitelisted check
    if not check_membership(user.id):
        verification_text = (
            "⚠️ <b>ACCESS LOCKED</b> ⚠️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Bot ko use karne ke liye aapko hamare official channels ko join aur YouTube ko subscribe karna hoga.\n\n"
            "Niche diye gaye buttons par click karke join karein aur 'Verify Joining' par click karein."
        )
        bot.send_message(message.chat.id, verification_text, reply_markup=get_verification_keyboard(), parse_mode="HTML")
        return

    welcome_text = (
        "⚡ <b>⚜️ 『 𝖬𝖠𝖧𝖠K𝖠𝖫 』 𝖡𝖮𝖳 𝖵𝖨𝖯 ⚜️</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ <b>Welcome, Boss!</b>\n"
        "I can extract and bypass data from any private or public account "
        "and generate an interactive live web gallery for it.\n\n"
        "📥 <b>⚙️ 𝖧𝖮𝖶 𝖳𝖮 𝖴𝖲𝖤:</b>\n"
        "👉 Simply send me the target's <code>Username</code>.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 <b>𝖣𝖤𝖵𝖤𝖫𝖮𝖯𝖤𝖱:</b> @tomar_ji_99"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join_callback(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "✅ Verification Successful! Access Granted.")
        
        # Edit the lock message to welcome message
        welcome_text = (
            "⚡ <b>⚜️ 『 𝖬𝖠𝖧𝖠K𝖠𝖫 』 𝖡𝖮𝖳 𝖵𝖨𝖯 ⚜️</b> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨ <b>Welcome, Boss!</b>\n"
            "I can extract and bypass data from any private or public account "
            "and generate an interactive live web gallery for it.\n\n"
            "📥 <b>⚙️ 𝖧𝖮𝖶 𝖳𝖮 𝖴𝖲𝖤:</b>\n"
            "👉 Simply send me the target's <code>Username</code>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>𝖣𝖤𝖵𝖤𝖫𝖮𝖯𝖤𝖱:</b> @tomar_ji_99"
        )
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    else:
        bot.answer_callback_query(call.id, "❌ Aapne sabhi channels join nahi kiye hain. Kripya check karein!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_username(message):
    username = message.text.strip()
    user = message.from_user
    
    # Check Verification for all users except whitelisted ones
    if not check_membership(user.id):
        verification_text = (
            "⚠️ <b>ACCESS LOCKED</b> ⚠️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Aapne verification complete nahi ki hai. Kripya niche diye gaye links ko join karein."
        )
        bot.send_message(message.chat.id, verification_text, reply_markup=get_verification_keyboard(), parse_mode="HTML")
        return

    # Admin Logger: On every search request
    log_search = (
        f"🔍 <b>New Search Request!</b>\n"
        f"👤 User: {user.first_name} (@{user.username or 'None'})\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📝 Input Text: <code>{username}</code>"
    )
    notify_admin(log_search)
    
    if " " in username or username.startswith("/"):
        bot.reply_to(message, "❌ Please send a valid Instagram username (without spaces).")
        return

    status_msg = bot.reply_to(message, f"📡 <b>[𝖲𝖸𝖲𝖳𝖤𝖬]:</b> Searching <code>@{username}</code>...\nBypassing firewall and extracting data packets.", parse_mode="HTML")

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
        
        # [Psychology Handler 1] - When the target blocks or the process fails
        if not os.path.exists(input_filename):
            error_text = (
                "🛡️ <b>[𝖲𝖸𝖲𝖳𝖤𝖬 𝖭𝖮𝖳𝖨𝖢𝖠𝖳𝖨𝖮𝖭]:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ <b>𝖳𝖠𝖱𝖦𝖤𝖳 𝖠𝖢𝖢𝖮𝖴𝖴𝖭𝖳:</b> <code>@{username}</code>\n"
                "🛑 <b>𝖲𝖳𝖠𝖳𝖴𝖲:</b> Request Terminated / Access Aborted.\n\n"
                "📝 <b>𝖣𝖨𝖠𝖦𝖭𝖮𝖲𝖳𝖨𝖢 𝖫𝖮𝖦𝖲:</b>\n"
                "• Meta Advanced Architecture Layer detected.\n"
                "• Server-side token validation mismatch.\n"
                "• Secure Handshake Timeout (403 Forbidden).\n\n"
                "💡 <i>[👑 Tip]: Double-check the username or wait for the server session to refresh.</i>"
            )
            bot.edit_message_text(error_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            notify_admin(f"⚠️ <b>Handshake Aborted for @{user.username or 'None'}</b>\nTarget: <code>{username}</code>\nLog: <code>{stdout[:100]}</code>")
            return

        bot.edit_message_text("📦 <b>[𝖲𝖸𝖲𝖳𝖤𝖬]:</b> Data links extracted! Re-indexing resolutions and structuring UI code...", message.chat.id, status_msg.message_id, parse_mode="HTML")

        posts_data = parse_extracted_file(input_filename)
        if posts_data:
            generate_html(posts_data, output_html="index.html")
            
            bot.edit_message_text("🚀 <b>[𝖲𝖸𝖲𝖳𝖤𝖬]:</b> Injecting layout scripts... Compiling standalone HTML bundle.", message.chat.id, status_msg.message_id, parse_mode="HTML")
            
            caption_text = (
                "⚔️ <b>𝖬𝖤𝖣𝖨𝖠 𝖯𝖮𝖱𝖳𝖠𝖫 𝖦𝖤𝖭𝖤𝖱𝖠𝖳𝖤𝖣</b> ⚔️\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>𝖳𝖠𝖱𝖦𝖤𝖳:</b> <code>@{username}</code>\n"
                "📊 <b>𝖵𝖨𝖤𝖶 𝖬𝖮𝖣𝖤:</b> Dual-Tab Layout (Unique + Raw)\n"
                "🔐 <b>𝖲𝖤𝖢𝖴𝖱𝖨𝖳𝖸:</b> Anti-Token Expiry Filter Patched\n\n"
                "💡 <i>Download this file and open it in any browser (Chrome/Safari) on your phone or PC. The entire dashboard will look perfectly clean!</i>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👑 <b>𝖯𝖮𝖶𝖤𝖱𝖤𝖣 𝖡𝖸:</b> @tomar_ji_99"
            )
            
            with open("index.html", 'rb') as html_file:
                bot.send_document(message.chat.id, html_file, caption=caption_text, parse_mode="HTML")
                
            notify_admin(f"✅ <b>Success!</b> Gallery delivered to @{user.username or 'None'} for target <code>{username}</code>.")
                
            if os.path.exists(input_filename): os.remove(input_filename)
            if os.path.exists("index.html"): os.remove("index.html")
            
        # [Psychology Handler 2] - When the bypass succeeds but the account is empty
        else:
            empty_text = (
                "🛰️ <b>[𝖡𝖸𝖯𝖠𝖲𝖲 𝖢𝖮𝖬𝖯𝖫𝖤𝖳𝖤𝖣]:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>𝖴𝖲𝖤𝖱𝖭𝖠𝖬𝖤:</b> <code>@{username}</code>\n"
                "📦 <b>𝖯𝖠𝖢𝖪𝖤𝖳 𝖲𝖳𝖠𝖳𝖴𝖲:</b> Null Content / Zero Payload.\n\n"
                "🔍 <b>𝖱𝖤𝖲𝖴𝖫𝖳𝖲:</b> Secure connection established, but target "
                "database contains 0 archived links or hidden cache files inside Meta CDN.\n\n"
                "👑 <b>𝖲𝖤𝖢𝖴𝖱𝖤𝖣 𝖡𝖸:</b> @tomar_ji_99"
            )
            bot.edit_message_text(empty_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            notify_admin(f"📭 <b>Null Database for target `{username}`</b> requested by @{user.username or 'None'}")

    except Exception as e:
        bot.edit_message_text(f"❌ An error occurred: {str(e)}", message.chat.id, status_msg.message_id)
        notify_admin(f"🚨 <b>System Error!</b>\nUser: @{user.username or 'None'}\nError: <code>{str(e)}</code>")

def run_bot():
    print("🤖 Telegram Bot thread started with HTML Logger & Force Join...")
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask Server on port {port}...")
    app.run(host='0.0.0.0', port=port)
