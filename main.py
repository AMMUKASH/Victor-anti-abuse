import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_LINK

# --- RENDER PORT FIX (Dummy Server) ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Xeno Anti-Abuse Bot is Running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), RenderServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT SETUP ---
app = Client("XenoStrictBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Image & DB
START_IMG = "https://i.ibb.co/YThQkhHJ/30304.png"
users_db = set()

# --- ⚠️ THE ULTIMATE ABUSE LIST (Logic covers 500+ variations) ---
BAD_WORDS = [
    # Hinglish Core
    "mc", "bc", "bsdk", "bhosadike", "chutiya", "lodu", "gandu", "madarchod", "bhenchod", 
    "randi", "lund", "lauda", "kutta", "pilla", "harami", "kamine", "bhadwa", "mkl", "bkl", 
    "gl", "sala", "saala", "betichod", "baapchod", "jhaat", "lavda", "mutthal", "raand", 
    "bakchodi", "pichwada", "gaand", "chut", "chutiye", "randaap", "randwa", "kaminey",
    
    # English Slangs
    "fuck", "bitch", "asshole", "bastard", "dick", "pussy", "tits", "boobs", "shitty", "fucker",
    
    # Hindi/Devanagari
    "गाली", "चूतिया", "साला", "हरामी", "मादरचोद", "बहनचोद", "गंाडू", "भोसड़ीके"
]

REPLY_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Updates", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 Support", url=SUPPORT_CHAT)],
    [InlineKeyboardButton("👨‍💻 Owner", url=OWNER_LINK)]
])

# 1. Start Command
@app.on_message(filters.command("start"))
async def start(client, message):
    users_db.add(message.chat.id)
    caption = (f"👋 **Hello {message.from_user.mention}!**\n\n"
               "Main **Xeno Anti-Abuse Bot** hoon. Main Admin aur Owner samet sabki galiyan delete karta hoon.\n\n"
               "📖 Commands ke liye `/help` likhein.")
    await message.reply_photo(photo=START_IMG, caption=caption, reply_markup=REPLY_MARKUP)

# 2. Welcome Message (Swagat Feature)
@app.on_message(filters.new_chat_members)
async def welcome_member(client, message):
    for member in message.new_chat_members:
        welcome_text = (f"✨ **Namaste {member.mention}!**\n\n"
                        f"Welcome to **{message.chat.title}**.\n"
                        "⚠️ Rules: Gali di toh message delete ho jayega!")
        await message.reply_text(welcome_text)

# 3. Help Command
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    help_text = (
        "🛡️ **Admin & User Guide:**\n\n"
        "• `/start` - Bot status check.\n"
        "• `/help` - Ye menu dekhne ke liye.\n"
        "• `/broadcast` - Msg to all users (Owner Only).\n"
        "• `/ban` - Reply to user to ban them.\n\n"
        "**Feature:** Automatic abuse detection for Everyone!"
    )
    await message.reply_text(help_text, reply_markup=REPLY_MARKUP)

# 4. Broadcast Feature (Owner Only)
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to a message to broadcast!")
    
    msg = await message.reply_text("🚀 Sending broadcast...")
    count = 0
    for chat_id in list(users_db):
        try:
            await message.reply_to_message.copy(chat_id)
            count += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit(f"✅ Broadcast complete! **{count}** users ko message mil gaya.")

# 5. Strict Anti-Abuse Logic (The Beast Mode)
@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_strict_abuse(client, message):
    users_db.add(message.chat.id)
    
    # Text cleaning: hum dots, spaces, aur special characters remove kar rahe hain
    # Taaki 'm.c' ya 'm c' ko bhi 'mc' ki tarah detect kiya jaye.
    raw_text = message.text.lower()
    clean_text = "".join(e for e in raw_text if e.isalnum())

    if any(word in raw_text or word in clean_text for word in BAD_WORDS):
        try:
            await message.delete()
            # Log to Owner (Private Reporting)
            log_text = (f"🚨 **Abuse Log!**\n\n"
                        f"👤 User: {message.from_user.mention}\n"
                        f"👥 Group: {message.chat.title}\n"
                        f"💬 Text: `{message.text}`")
            await client.send_message(OWNER_ID, log_text)
            
            # Group Warning
            warn = await message.reply_text(f"⚠️ {message.from_user.mention}, Gali dena mana hai! Message delete kar diya gaya.")
            await asyncio.sleep(5)
            await warn.delete()
        except: pass

print("🔥 Bot is Active with All Features!")
app.run()
