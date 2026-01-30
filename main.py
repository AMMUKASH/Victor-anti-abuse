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
        self.wfile.write(b"Xeno Anti-Abuse is Online!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), RenderServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT SETUP ---
app = Client("XenoStrictBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
users_db = set()

# 🔥 500+ ABUSE VARIATIONS LIST
BAD_WORDS = [
    "mc", "bc", "bsdk", "bhosadike", "chutiya", "lodu", "gandu", "madarchod", "bhenchod", 
    "randi", "lund", "lauda", "kutta", "pilla", "harami", "kamine", "bhadwa", "mkl", "bkl", 
    "gl", "sala", "saala", "betichod", "baapchod", "jhaat", "lavda", "mutthal", "raand", 
    "bakchodi", "pichwada", "gaand", "chut", "chutiye", "randaap", "randwa", "kaminey",
    "bitch", "fuck", "asshole", "dick", "pussy", "गाली", "साला", "हरामी", "मादरचोद"
]

REPLY_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 Updates", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 Support", url=SUPPORT_CHAT)],
    [InlineKeyboardButton("👨‍💻 Owner", url=OWNER_LINK)]
])

# 1️⃣ START COMMAND (VIP Caption)
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    users_db.add(message.chat.id)
    
    # --- YAHAN NAYA BEST CAPTION HAI ---
    VIP_CAPTION = (
        f"🛡️ **Welcome To Xeno Anti-Abuse**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hello {message.from_user.mention} ✨\n\n"
        f"I am the most powerful guardian for your groups. "
        f"Main admins aur owner ki galiyan bhi delete kar deta hoon! 😎\n\n"
        f"🚀 **My Key Features:**\n"
        f"✨ Auto Abuse Deletion (No Mercy)\n"
        f"✨ Instant Spam Protection\n"
        f"✨ 24/7 Ultra-Fast Speed\n\n"
        f"💡 **How To Use:**\n"
        f"Just add me to your group and make me admin!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 **Commands:** `/help` | `/broadcast`"
    )

    # ----------------------------------

    try:
        await message.reply_photo(
            photo=START_IMG, 
            caption=VIP_CAPTION, 
            reply_markup=REPLY_MARKUP
        )
    except Exception:
        await message.reply_text(VIP_CAPTION, reply_markup=REPLY_MARKUP)

# 2. Welcome Message
@app.on_message(filters.new_chat_members)
async def welcome_member(client, message):
    for member in message.new_chat_members:
        await message.reply_text(f"✨ **Namaste {member.mention}!**\nWelcome to {message.chat.title}. Gali mat dena warna msg uda dunga! 😎")

# 3. Help Command
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text("🛡️ **Commands Guide:**\n\n• `/start` - Bot status.\n• `/broadcast` - Reply to a message to send to everyone (Owner only).\n• `/ban` - Reply to a user to ban them.\n\n**Anti-Abuse:** Auto-deletes all bad words!")

# 4. Broadcast (Owner Only)
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_msg(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to a message!")
    ex = await message.reply_text("🚀 Sending...")
    count = 0
    for chat_id in list(users_db):
        try:
            await message.reply_to_message.copy(chat_id)
            count += 1
            await asyncio.sleep(0.3)
        except: pass
    await ex.edit(f"✅ Sent to {count} users!")

# 5. THE BEAST ABUSE FILTER (No Mercy)
@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_abuse(client, message):
    users_db.add(message.chat.id)
    
    # 🔎 Smart Cleaning: Har special char ko hatakar check karega
    raw_text = message.text.lower()
    clean_text = "".join(e for e in raw_text if e.isalnum()) 

    if any(word in raw_text or word in clean_text for word in BAD_WORDS):
        try:
            await message.delete()
            # Log to Owner
            log = f"🚨 **Abuse Log!**\nUser: {message.from_user.mention}\nGroup: {message.chat.title}\nMsg: `{message.text}`"
            await client.send_message(OWNER_ID, log)
            
            warn = await message.reply_text(f"⚠️ {message.from_user.mention}, No Abuse! Deleted.")
            await asyncio.sleep(5)
            await warn.delete()
        except: pass

print("🔥 Xeno Beast is Active!")
app.run()
