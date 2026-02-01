import os
import asyncio
import threading
import re
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
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
warns_db = {} # Track user warnings: {user_id: count}
LOG_GROUP = -1003867805165  

# 🔥 FULL BANNED LIST
BANNED_WORDS = [
    "randi", "rand", "gandu", "madhrchod", "bhosdike", "lund", "louda", "loda",
    "chut", "gand", "gaand", "gnd", "bhnchod", "bahanchod", "bsdk", "mc", "bc",
    "randibaz", "randibaaz", "motherfucker", "motherchod", "motherchodo", 
    "chudai", "chud", "chudi", "chudata", "chudwa", "choda", "chodunga", 
    "chodungi", "chod", "bhosda", "bhosdi", "lowda", "lowde", "loude", "lode",
    "behen ko chod", "bhn ko chodke", "bahan ko chodke", "teri maa chodunga",
    "bahan ki chut", "behen ki lowdii", "teri behen ko chodu", "teri amaa ka bhosraa",
    "kutta", "pilla", "harami", "kamine", "bhadwa", "mkl", "bkl", "gl", "sala", 
    "saala", "betichod", "baapchod", "jhaat", "lavda", "mutthal", "raand", 
    "bakchodi", "pichwada", "randaap", "randwa", "kaminey", "bitch", "asshole", "dick",
    "join my bio", "join my bioo", "biooo", "bioo", "bioooo", "biooooo", "bio",
    "dm karo", "dmm karo", "dm me", "massage kro", "whatsapp", "videocall", 
    "call", "buy", "sell", "charge", "rs", "join", "biz", "bizz",
    "porn", "pornograpy", "xxx", "xxxx", "xxxxxx", "sexy", "sexx", "sexxx", "sexxxxx",
    "boobs", "boob", "bobe", "suck", "fuck", "pussy", "mia khalifa", "sunny leone",
    "rape", "chikni", "chikna", "aah", "ah", "baby", "drugs", "drug", "ganja", 
    "naseela", "nasila", "nasela", "harm", "malware", "aukat", "aukaat", "kalap", 
    "klp", "kalpo", "kalapo", "boys come", "girls come"
]

# --- KEYBOARDS ---
START_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)],
    [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url=f"https://t.me/{(app.name if hasattr(app, 'name') else 'bot')}?startgroup=true")],
    [InlineKeyboardButton("🛠 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_back")]
])

# 1️⃣ START COMMAND
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.chat.id not in users_db:
        users_db.add(message.chat.id)
        log_txt = f"👤 **#ɴᴇᴡ_ᴜꜱᴇʀ**\n**ɴᴀᴍᴇ:** {message.from_user.mention}\n**ɪᴅ:** `{message.from_user.id}`"
        await client.send_message(LOG_GROUP, log_txt)

    await message.reply_photo(photo=START_IMG, caption="🛡️ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ xᴇɴᴏ ᴀɴᴛɪ-ᴀʙᴜꜱᴇ**\n\nᴍᴀɪɴ ᴀᴘᴋᴇ ɢʀᴏᴜᴘꜱ ᴋᴏ ꜱᴀꜰᴇ ʀᴀᴋʜɴᴇ ᴋᴇ ʟɪʏᴇ ʜᴏᴏɴ!", reply_markup=START_MARKUP)

# 2️⃣ ADVANCED FILTER + 3 WARN MUTE SYSTEM
@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_abuse(client, message):
    if not message.from_user:
        return

    raw_text = message.text.lower()
    clean_text = "".join(e for e in raw_text if e.isalnum()) 

    found = False
    for word in BANNED_WORDS:
        pattern = rf"\b{re.escape(word)}\b"
        if re.search(pattern, raw_text) or word in clean_text:
            found = True
            break

    if found:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Increase warn count
        warns_db[user_id] = warns_db.get(user_id, 0) + 1
        current_warns = warns_db[user_id]

        try:
            await message.delete()
            
            if current_warns >= 3:
                # MUTE USER
                await client.restrict_chat_member(
                    chat_id, 
                    user_id, 
                    ChatPermissions(can_send_messages=False)
                )
                warns_db[user_id] = 0 # Reset after mute
                
                mute_msg = await message.reply_text(
                    f"🚫 {message.from_user.mention} **ʜᴀꜱ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ!**\n"
                    f"**ʀᴇᴀꜱᴏɴ:** Exceeded 3 warnings (Abuse/Spam)."
                )
                
                log_text = f"🔇 **#ᴍᴜᴛᴇ_ᴇᴠᴇɴᴛ**\n**ᴜꜱᴇʀ:** {message.from_user.mention}\n**ɢʀᴏᴜᴘ:** {message.chat.title}"
                await client.send_message(LOG_GROUP, log_text)
            else:
                # WARNING MESSAGE
                warn_msg = await message.reply_text(
                    f"⚠️ {message.from_user.mention}, **ᴅᴏɴ'ᴛ ᴀʙᴜꜱᴇ!**\n"
                    f"**ᴡᴀʀɴɪɴɢꜱ:** {current_warns}/3\n"
                    f"Next time you will be **MUTED**."
                )
                await asyncio.sleep(5)
                await warn_msg.delete()

        except Exception as e:
            print(f"Error: {e}")

# 3️⃣ BROADCAST
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_msg(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ!")
    ex = await message.reply_text("🚀 ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...")
    count = 0
    for chat_id in list(users_db):
        try:
            await message.reply_to_message.copy(chat_id)
            count += 1
            await asyncio.sleep(0.3)
        except: pass
    await ex.edit(f"✅ **Sent to {count} users.**")

print("🔥 Xeno Beast with 3-Warn Mute System is Active!")
app.run()
