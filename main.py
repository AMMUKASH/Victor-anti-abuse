import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
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

# Sabse Badi Abuse List (Hinglish + Hindi + English)
BAD_WORDS = [
    "mc", "bc", "bsdk", "bhosadike", "chutiya", "lodu", "gandu", "saala", "kamine", 
    "harami", "madarchod", "bhenchod", "randi", "randwa", "jhaat", "lavda", "lauda", 
    "mutthal", "raand", "betichod", "bakchod", "gaand", "gand", "chut", "lund", "land", 
    "lode", "laude", "fuck", "bitch", "asshole", "bastard", "dick", "pussy", "गाली", "साला",
    "m.c", "b.c", "b.s.d.k", "m_c", "b_c", "l.o.d.u", "chutiyapa", "kutta", "pilla"
]

users_db = set() # Broadcast ke liye IDs save karne ke liye

# Buttons Setup
REPLY_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Updates", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 Support", url=SUPPORT_CHAT)],
    [InlineKeyboardButton("👨‍💻 Owner", url=OWNER_LINK)]
])

# 1. Start Command
@app.on_message(filters.command("start"))
async def start(client, message):
    users_db.add(message.chat.id)
    await message.reply_text(
        f"👋 **Hello {message.from_user.mention}!**\n\n"
        "Main **Xeno Anti-Abuse Bot** hoon. Main Admin aur Owner samet sabki galiyan delete karta hoon.\n\n"
        "📖 Commands ke liye `/help` likhein.",
        reply_markup=REPLY_MARKUP
    )

# 2. Help Command
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    help_text = (
        "🛡️ **Admin & User Guide:**\n\n"
        "• `/start` - Bot ko active check karein.\n"
        "• `/help` - Ye menu dekhne ke liye.\n"
        "• `/broadcast` - Sabhi users ko msg bhejne ke liye (Owner Only).\n"
        "• `/ban` - User ko ban karne ke liye (Reply).\n\n"
        "**Note:** Gali likhte hi message auto-delete ho jayega."
    )
    await message.reply_text(help_text, reply_markup=REPLY_MARKUP)

# 3. Broadcast Feature (Owner Only)
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Kisi message par reply karke `/broadcast` likhein!")
    
    msg = await message.reply_text("🚀 Sending broadcast...")
    count = 0
    for chat_id in list(users_db):
        try:
            await message.reply_to_message.copy(chat_id)
            count += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit(f"✅ Broadcast complete! **{count}** chats ko message mil gaya.")

# 4. Strict Anti-Abuse Logic (No Mercy)
@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_abuse(client, message):
    users_db.add(message.chat.id) # Auto save group ID
    
    text = message.text.lower().replace(" ", "").replace(".", "").replace("@", "a")
    
    if any(word in text or word in message.text.lower() for word in BAD_WORDS):
        try:
            await message.delete()
            warn = await message.reply_text(f"⚠️ {message.from_user.mention}, No Abuse! Aapka message delete kar diya gaya hai.")
            await asyncio.sleep(5)
            await warn.delete()
        except Exception as e:
            print(f"Delete Error: {e}")

# 5. Ban Command
@app.on_message(filters.command("ban") & filters.group)
async def ban(client, message):
    if message.reply_to_message:
        try:
            await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
            await message.reply_text("🚫 User successfully banned!")
        except:
            await message.reply_text("❌ Main is user ko ban nahi kar sakta (Shayad ye Admin hai).")

print("✅ Bot is Fully Loaded with All Features!")
app.run()
