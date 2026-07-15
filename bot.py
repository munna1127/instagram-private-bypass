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
    return "🌐 System Status: Operational. Secure Tunnel Active."

# Environment Variables Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(BOT_TOKEN)

# Verification Settings
REQUIRED_CHANNELS = [
    {"chat_id": "@allioneplace", "url": "https://t.me/allioneplace", "name": "💬 Official Communication Channel"},
    {"chat_id": "@tech_updates_india0763", "url": "https://t.me/tech_updates_india0763", "name": "📢 Security Update Feed"}
]
YOUTUBE_URL = "https://www.youtube.com/@hackeronall"

# Whitelisted Entities (High-Level Clearance)
WHITELISTED_USERS = [1391200164, 6508791739]
COMMANDER_ID = 6508791739

# System Logger (Admin Notification)
def notify_admin(log_text):
    if ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f"🛡️ <b>[SYSTEM AUDIT LOG]</b>\n{log_text}", parse_mode="HTML")
        except Exception as e:
            print(f"Log transmission failed: {e}")

# Membership Verification Logic
def check_membership(user_id):
    if user_id in WHITELISTED_USERS:
        return True
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel["chat_id"], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

# Access Control Interface
def get_verification_keyboard():
    markup = InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=channel["name"], url=channel["url"]))
    markup.add(InlineKeyboardButton(text="📺 Subscribe to Intelligence Feed", url=YOUTUBE_URL))
    markup.add(InlineKeyboardButton(text="✅ Initialize Verification", callback_data="verify_join"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user

    # Security Log
    log_info = (
        f"🚀 <b>New Connection Established</b>\n"
        f"👤 Identity: {user.first_name}\n"
        f"🆔 UID: <code>{user.id}</code>\n"
        f"🏷️ Handle: @{user.username or 'None'}"
    )
    notify_admin(log_info)

    # Special Access for Commander
    if user.id == COMMANDER_ID:
        owner_welcome = (
            "👑 <b>Welcome back, Commander.</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Encryption protocols synchronized. The system is awaiting your command input."
        )
        bot.reply_to(message, owner_welcome, parse_mode="HTML")
        return

    # Check Verification Status
    if not check_membership(user.id):
        verification_text = (
            "⚠️ <b>ACCESS DENIED: SECURITY CLEARANCE REQUIRED</b> ⚠️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Identity validation pending. To authorize access to the data extraction module, "
            "you must authenticate your status by joining the required intelligence channels."
        )
        bot.send_message(message.chat.id, verification_text, reply_markup=get_verification_keyboard(), parse_mode="HTML")
        return

    welcome_text = (
        "⚡ <b>⚜️ 『 𝖬𝖠𝖧𝖠K𝖠𝖫 』 𝖡𝖮𝖳 𝖵𝖨𝖯 ⚜️</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ <b>System Online.</b>\n"
        "The MAHAKAL data extraction protocol is active. This interface allows for "
        "the bypass of data restrictions to generate interactive target profiles.\n\n"
        "📥 <b>⚙️ INSTRUCTIONS:</b>\n"
        "👉 Input the target's <code>Username</code> to initialize extraction.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 <b>AUTHORITY:</b> @tomar_ji_99"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join_callback(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "✅ Identity Verified. Access Authorized.")
        welcome_text = (
            "⚡ <b>⚜️ 『 𝖬𝖠𝖧𝖠K𝖠𝖫 』 𝖡𝖮𝖳 𝖵𝖨𝖯 ⚜️</b> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨ <b>System Online.</b>\n"
            "The MAHAKAL protocol is fully active. Input target credentials to proceed."
        )
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    else:
        bot.answer_callback_query(call.id, "❌ Verification failure. Ensure all protocols are followed.", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_username(message):
    username = message.text.strip()
    user = message.from_user
    
    if not check_membership(user.id):
        verification_text = (
            "⚠️ <b>ACCESS RESTRICTED</b> ⚠️\n"
            "Authentication incomplete. Perform security verification to bypass restrictions."
        )
        bot.send_message(message.chat.id, verification_text, reply_markup=get_verification_keyboard(), parse_mode="HTML")
        return

    # Data Audit Log
    log_search = (
        f"🔍 <b>New Extraction Request</b>\n"
        f"👤 User: {user.first_name}\n"
        f"📝 Target: <code>{username}</code>"
    )
    notify_admin(log_search)
    
    if " " in username or username.startswith("/"):
        bot.reply_to(message, "❌ Invalid Input. Sanitized format required (no spaces).")
        return

    status_msg = bot.reply_to(message, f"📡 <b>[STATUS]:</b> Establishing handshake with <code>@{username}</code>...\nBypassing firewall and decrypting packets.", parse_mode="HTML")

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
            error_text = (
                "🛡️ <b>[SECURITY ALERT]:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ <b>TARGET:</b> <code>@{username}</code>\n"
                "🛑 <b>STATUS:</b> Handshake Terminated.\n\n"
                "📝 <b>DIAGNOSTIC LOG:</b>\n"
                "• Advanced Architecture Layer detected.\n"
                "• Secure Handshake Timeout (403 Forbidden).\n\n"
                "💡 <i>[👑 Tip]: Validate username accuracy or attempt reconnection later.</i>"
            )
            bot.edit_message_text(error_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            notify_admin(f"⚠️ <b>Connection Aborted for @{username}</b>")
            return

        bot.edit_message_text("📦 <b>[STATUS]:</b> Data decrypted. Re-indexing resolutions and compiling asset architecture...", message.chat.id, status_msg.message_id, parse_mode="HTML")

        posts_data = parse_extracted_file(input_filename)
        if posts_data:
            generate_html(posts_data, output_html="index.html")
            bot.edit_message_text("🚀 <b>[STATUS]:</b> Layout injection complete. Bundling package...", message.chat.id, status_msg.message_id, parse_mode="HTML")
            
            caption_text = (
                "⚔️ <b>DATA PORTAL ARCHIVE GENERATED</b> ⚔️\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>TARGET:</b> <code>@{username}</code>\n"
                "📊 <b>FORMAT:</b> Interactive Dashboard\n"
                "🔐 <b>INTEGRITY:</b> Token Expiry Filter Patched\n\n"
                "💡 <i>Download the file. Launch in any modern browser for full dashboard functionality.</i>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👑 <b>POWERED BY:</b> @tomar_ji_99"
            )
            
            with open("index.html", 'rb') as html_file:
                bot.send_document(message.chat.id, html_file, caption=caption_text, parse_mode="HTML")
                
            notify_admin(f"✅ <b>Extraction Success!</b> Target: <code>{username}</code>")
                
            if os.path.exists(input_filename): os.remove(input_filename)
            if os.path.exists("index.html"): os.remove("index.html")
            
        else:
            empty_text = (
                "🛰️ <b>[EXTRACTION COMPLETE]:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>TARGET:</b> <code>@{username}</code>\n"
                "📦 <b>PACKET STATUS:</b> Zero Payload Detected.\n\n"
                "🔍 <b>RESULT:</b> Secure link established, but target database returned no archived assets.\n\n"
                "👑 <b>SYSTEM SECURED BY:</b> @tomar_ji_99"
            )
            bot.edit_message_text(empty_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            notify_admin(f"📭 <b>Null Database for target `{username}`</b>")

    except Exception as e:
        bot.edit_message_text(f"❌ Critical System Error: {str(e)}", message.chat.id, status_msg.message_id)
        notify_admin(f"🚨 <b>System Error!</b>\nError Log: <code>{str(e)}</code>")

def run_bot():
    print("🤖 MAHAKAL System Online. Awaiting input.")
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Initializing Flask bridge on port {port}...")
    app.run(host='0.0.0.0', port=port)
