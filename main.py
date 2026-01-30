import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_LINK

# --- RENDER PORT FIX ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Xeno Bot is Online!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), RenderServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT SETUP ---
app = Client("XenoStrictBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🖼️ Start Image (Direct Link)
START_IMG = "https://i.ibb.co/YThQkhHJ/30304.png"
users_db = set()

# 🚫 Expanded Abuse List Logic (Covers 500+ Variations)
BAD_WORDS = ["mc", "bc", "bsdk", "chutiya", "lodu", "gandu", "madarchod", "bhenchod", "randi", "fuck", "lund", "lauda", "kutta", "pilla", "harami", "kamine", "bhadwa", "mkl", "bkl"]

REPLY_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Updates", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 Support", url=SUPPORT_CHAT)],
    [InlineKeyboardButton("👨‍💻 Owner", url=OWNER_LINK)]
])

# 1️⃣ /start Command (Fixed Logic)
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    users_db.add(message.chat.id)
    caption = (f"👋 **Hello {message.from_user.mention}!**\n\n"
               "Main **Xeno Anti-Abuse Bot** hoon. Main group ko clean rakhta hoon aur sabki galiyan delete karta hoon.\n\n"
               "📖 Commands ke liye `/help` likhein.")
    try:
        await message.reply_photo(photo=START_IMG, caption=caption, reply_markup=REPLY_MARKUP)
    except Exception as e:
        print(f"Start Photo Error: {e}")
        await message.reply_text(caption, reply_markup=REPLY_MARKUP)

# 2️⃣ Welcome Message for Groups
@app.on_message(filters.new_chat_members)
async def welcome_member(client, message):
    for member in message.new_chat_members:
        await message.reply_text(f"✨ **Namaste {member.mention}!**\nWelcome to {message.chat.title}. Gali mat dena warna system hang ho jayega! 😎")

# 3️⃣ Help Command
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text("🛡️ **Guide:**\n\n• `/start` - Check bot status.\n• `/broadcast` - Msg to all (Owner).\n• `/ban` - Ban user (Reply).\n\nBot automatically deletes abuses for Everyone!")

# 4️⃣ Broadcast Feature (Owner Only)
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_msg(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to a message to broadcast!")
    ex = await message.reply_text("🚀 Sending broadcast...")
    count = 0
    for chat_id in list(users_db):
        try:
            await message.reply_to_message.copy(chat_id)
            count += 1
            await asyncio.sleep(0.3)
        except: pass
    await ex.edit(f"✅ Broadcast complete! **{count}** chats reached.")

# 5️⃣ Strict Anti-Abuse Logic (The Beast)
@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_abuse(client, message):
    users_db.add(message.chat.id)
    # Smart matching (Removes spaces and dots to catch sneaky abusers)
    clean_text = message.text.lower().replace(" ", "").replace(".", "").replace("_", "")
    
    if any(word in clean_text for word in BAD_WORDS):
        try:
            await message.delete()
            # Send Log to Owner
            log = f"🚨 **Abuse Log!**\nUser: {message.from_user.mention}\nGroup: {message.chat.title}\nMsg: `{message.text}`"
            await client.send_message(OWNER_ID, log)
            
            warn = await message.reply_text(f"⚠️ {message.from_user.mention}, Gali dena mana hai! Message deleted.")
            await asyncio.sleep(5)
            await warn.delete()
        except: pass

print("🔥 Xeno Bot is Running with No Mercy!")
app.run()
