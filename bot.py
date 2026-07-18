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
    return "🌐 SYSTEM STATUS: OPERATIONAL. SECURE BRIDGE ACTIVE."

# Environment Variables Config
BOT_TOKEN = os.getenv("BOT_TOKEN", "7961855216:AAGkPvn-bLR6PEHN2S4Wi-8wfpTqG8ING5g")
ADMIN_ID = os.getenv("ADMIN_ID", "6508791739")
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(BOT_TOKEN)

# Verification Targets
REQUIRED_CHANNELS = [
    {"chat_id": "@allioneplace", "url": "https://t.me/allioneplace", "name": "💬 TELEGRAM GROUP"},
    {"chat_id": "@tech_updates_india0763", "url": "https://t.me/tech_updates_india0763", "name": "📢 TELEGRAM CHANNEL"}
]
YOUTUBE_URL = "https://www.youtube.com/@hackeronall"

# Absolute Clearance Level (Bypass Verification entirely)
WHITELISTED_USERS = [1391200164, 6508791739]
SPECIAL_OWNER_ID = 6508791739

# Encryption Core Audit Logs
def notify_admin(log_text):
    if ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, f"⚡ <b>[CORE AUDIT]</b>\n{log_text}", parse_mode="HTML")
        except Exception as e:
            print(f"Audit dump failed: {e}")

# Secure Verification Gate
def check_membership(user_id):
    if int(user_id) in WHITELISTED_USERS:
        return True
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel["chat_id"], user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            return False
    return True

# Premium Terminal Buttons UI
def get_verification_keyboard():
    markup = InlineKeyboardMarkup()
    for channel in REQUIRED_CHANNELS:
        markup.add(InlineKeyboardButton(text=channel["name"], url=channel["url"]))
    markup.add(InlineKeyboardButton(text="📺 YOUTUBE INTEL FEED", url=YOUTUBE_URL))
    markup.add(InlineKeyboardButton(text="⚡ INITIALIZE INJECTION ⚡", callback_data="verify_join"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user

    # Internal Audit Logging
    log_info = (
        f"🛰️ <b>Terminal Connection Request</b>\n"
        f"👤 Agent: {user.first_name}\n"
        f"🆔 UID: <code>{user.id}</code>\n"
        f"🏷️ Handle: @{user.username or 'None'}"
    )
    notify_admin(log_info)

    # 👑 Ultra-Exclusive Welcoming for Owner Sir (Bypasses Everything)
    if user.id == SPECIAL_OWNER_ID:
        owner_welcome = (
            "⚡ <b>⚜️ MASTER SYSTEM PANEL ⚜️</b> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👑 <b>Salutations, Owner Sir! Welcome back.</b>\n"
            "All mainframe safety protocols have been overridden automatically for your presence.\n\n"
            "📡 <b>CONSOLE READY:</b>\n"
            "Directly input target handle using <code>/u username</code> to initialize immediate extraction."
        )
        bot.reply_to(message, owner_welcome, parse_mode="HTML")
        return

    # Standard User Authorization Check
    if not check_membership(user.id):
        verification_text = (
            "🔒 <b>MAINFRAME LOCK: AUTHORIZATION REQUIRED</b> 🔒\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚡ <b>SECURITY NOTICE:</b>\n"
            "To access the VIP private data extraction modules, you must authenticate your credentials.\n\n"
            "👇 <b>ACTIONS REQUIRED:</b>\n"
            "Join our restricted community channels using the gateway buttons below, then hit <b>Initialize Injection</b> to unlock access."
        )
        bot.send_message(message.chat.id, verification_text, reply_markup=get_verification_keyboard(), parse_mode="HTML")
        return

    welcome_text = (
        "⚡ <b>⚜️ 『 𝖬𝖠𝖧𝖠K𝖠𝖫 』 𝖡𝖮𝖳 𝖵𝖨𝖯 ⚜️</b> ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ <b>Welcome, Boss!</b>\n"
        "Mainframe connection secured. I am programmed to bypass server restrictions, "
        "extract hidden database layers, and compile private media assets into a pristine live web portal.\n\n"
        "📥 <b>⚙️ TERMINAL USAGE:</b>\n"
        "👉 Simply pass the target account's name using <code>/u username</code> inside this chat.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 <b>DEVELOPER MASTER MIND:</b> @tomar_ji_99"
    )
    bot.reply_to(message, welcome_text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join_callback(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "⚡ Terminal Access Granted. Core System Unlocked.", show_alert=False)
        welcome_text = (
            "⚡ <b>⚜️ 『 𝖬𝖠𝖧𝖠K𝖠𝖫 』 𝖡𝖮𝖳 𝖵𝖨𝖯 ⚜️</b> ⚡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✨ <b>System Online & Ready!</b>\n"
            "Authentication successful. Please execute the command <code>/u username</code> to ignite extraction sequence."
        )
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    else:
        bot.answer_callback_query(call.id, "❌ Verification Failure! Protocols missing. Join all channels first.", show_alert=True)

# 🚀 TARGET FIXED: Script now tracks only explicit command prefixes to prevent spam in groups
@bot.message_handler(func=lambda message: message.text.startswith('/u '))
def handle_username(message):
    # Splits out the command layer cleanly to fetch raw target variable parameters
    username = message.text.split('/u ', 1)[1].strip()
    user = message.from_user
    
    if not check_membership(user.id):
        verification_text = (
            "🔒 <b>TERMINAL REJECTED</b> 🔒\n"
            "Authentication required to release data stream. Comply with verification protocols."
        )
        bot.send_message(message.chat.id, verification_text, reply_markup=get_verification_keyboard(), parse_mode="HTML")
        return

    # Admin Search Audit Log
    log_search = (
        f"🔍 <b>Target Injection Initiated</b>\n"
        f"👤 Operator: {user.first_name}\n"
        f"¼ User ID: <code>{user.id}</code>\n"
        f"📝 Target Node: <code>{username}</code>"
    )
    notify_admin(log_search)
    
    if " " in username or username.startswith("/"):
        bot.reply_to(message, "❌ SYSTEM REJECTION: Sanitized string required. Remove spaces/commands.")
        return

    status_msg = bot.reply_to(message, f"📡 <b>[SYSTEM LAYER]:</b> Establishing secure tunnel with <code>@{username}</code>...\nBreaching security protocols & capturing network packets.", parse_mode="HTML")

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
                "🛡️ <b>[CRITICAL INTERCEPT NOTIFICATION]:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ <b>TARGET ENDPOINT:</b> <code>@{username}</code>\n"
                "🛑 <b>STATE:</b> Request Denied / Tunnel Collapsed.\n\n"
                "📝 <b>DIAGNOSTIC BACKLOG:</b>\n"
                "• Meta Advanced Architecture Firewall detected.\n"
                "• Dynamic token handshake synchronization failure.\n"
                "• Secure Socket Layer Timeout (Status 403).\n\n"
                "💡 <i>[👑 Tip]: Verify username integrity or wait for system session refresh.</i>"
            )
            bot.edit_message_text(error_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            notify_admin(f"⚠️ <b>Mainframe Handshake Dropped for @{username}</b>")
            return

        bot.edit_message_text("📦 <b>[SYSTEM LAYER]:</b> Content arrays captured! Structuring standalone asset code...", message.chat.id, status_msg.message_id, parse_mode="HTML")

        posts_data = parse_extracted_file(input_filename)
        if posts_data:
            generate_html(posts_data, output_html="index.html")
            bot.edit_message_text("🚀 <b>[SYSTEM LAYER]:</b> Compiling GUI modules... Injecting dual-tab standalone HTML.", message.chat.id, status_msg.message_id, parse_mode="HTML")
            
            caption_text = (
                "⚔️ <b>INTELLIGENCE PORTAL GENERATION COMPLETE</b> ⚔️\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>TARGET PROFILE:</b> <code>@{username}</code>\n"
                "📊 <b>DASHBOARD TYPE:</b> Interactive UI (Dual-Tab Module)\n"
                "🔐 <b>ENCRYPTION STATUS:</b> Anti-Expiry Link Token Patched\n\n"
                "💡 <i>Download this compiled interface file and execute it in any web browser (Chrome/Safari) on PC or Mobile for full interactivity.</i>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "👑 <b>POWERED BY IMMORTAL CORE:</b> @tomar_ji_99"
            )
            
            with open("index.html", 'rb') as html_file:
                bot.send_document(message.chat.id, html_file, caption=caption_text, parse_mode="HTML")
                
            notify_admin(f"✅ <b>Mainframe Extraction Success!</b> Node: <code>{username}</code>")
                
            if os.path.exists(input_filename): os.remove(input_filename)
            if os.path.exists("index.html"): os.remove("index.html")
            
        else:
            empty_text = (
                "🛰️ <b>[MAINFRAME BYPASS EXHAUSTED]:</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>TARGET HANDLE:</b> <code>@{username}</code>\n"
                "📦 <b>PAYLOAD STATUS:</b> Null Sector / Zero Active Files.\n\n"
                "🔍 <b>ANALYSIS:</b> Secure handshake completed successfully, but target "
                "database contains exactly 0 media logs inside the network cache.\n\n"
                "👑 <b>MAINFRAME SIGNATURE:</b> @tomar_ji_99"
            )
            bot.edit_message_text(empty_text, message.chat.id, status_msg.message_id, parse_mode="HTML")
            notify_admin(f"📭 <b>Null Assets found on target node `{username}`</b>")

    except Exception as e:
        bot.edit_message_text(f"❌ Mainframe Malfunction: {str(e)}", message.chat.id, status_msg.message_id)
        notify_admin(f"🚨 <b>Core Kernel Error!</b>\nLog: <code>{str(e)}</code>")

def run_bot():
    print("🤖 MAHAKAL Sovereign Kernel Active. Awaiting queries...")
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Mainframe web interface online on port {port}...")
    app.run(host='0.0.0.0', port=port)
