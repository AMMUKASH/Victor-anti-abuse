import os, asyncio, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, UserIsBlocked, ChatAdminRequired, PeerIdInvalid
from pymongo import MongoClient

# --- 📁 CONFIG IMPORT ---
try:
    from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, LOG_GROUP_ID, MONGO_URL
except ImportError:
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH", "your_hash")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_token")
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", 0))
    MONGO_URL = os.environ.get("MONGO_URL", "")

# --- 🌐 AUTO-HOST SERVER ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Antu Abuse Bot is Live!")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 🛠 DB & BOT SETUP ---
mongo = MongoClient(MONGO_URL)
db = mongo.AntuAbuseBot
warns_db = db.warns
users_db = db.users
chats_db = db.chats
settings_db = db.settings

app = Client("AntuAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🖼 ASSETS ---
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+|@[a-zA-Z0-9_]+)"

# List choti dikh rahi hai par aap apni purani list yaha puri paste kar lena
BANNED_WORDS = ["randi", "gandu", "mc", "bc", "bhenchod", "lund", "chutiya", "porn", "sex"]

# --- 📝 LOGGING SYSTEM (Public & Private) ---
async def send_log(client, chat_title, chat_id, user, action, reason, count=None):
    if not LOG_GROUP_ID:
        return
    try:
        log_text = (
            f"<b>#ANTU_LOGS</b>\n\n"
            f"📌 <b>Action:</b> {action}\n"
            f"👤 <b>User:</b> {user.mention} (<code>{user.id}</code>)\n"
            f"🌐 <b>Chat:</b> {chat_title} (<code>{chat_id}</code>)\n"
            f"⚠️ <b>Reason:</b> {reason}"
        )
        if count:
            log_text += f"\n📊 <b>Warn Level:</b> {count}/3"
        
        await client.send_message(LOG_GROUP_ID, log_text)
    except Exception as e:
        print(f"Log Error: {e}")

# --- 🛡 HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

async def get_setting(chat_id, key):
    res = settings_db.find_one({"c": chat_id})
    return res.get(key, True) if res else True

# --- 🏠 START COMMAND ---
@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    if not users_db.find_one({"u": user.id}):
        users_db.insert_one({"u": user.id})
        # Private Log: New User
        await send_log(client, "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ", "ᴅᴍ", user, "Bot Started", "New User Entry")

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("♻ 𝐀ᴅᴅ 𝐌𝝴 𝝸𝝶 𝐘𝞂𝞄𝐑 𝐆𝐑𝞂𝞄𝞀 ♻", url=f"https://t.me/{app.me.username}?startgroup=true")]])
    await message.reply_photo(photo=START_IMG, caption="👋 **Antu Abuse Bot is Online!**", reply_markup=buttons)

# --- 🔄 RESET WARNS COMMAND ---
@app.on_message(filters.command("reset") & filters.group)
async def reset_warns(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Sirf Admins warnings reset kar sakte hain!")
    
    reply = message.reply_to_message
    if not reply:
        return await message.reply("👤 Us bande ke message pe reply karo jiske warns reset karne hain.")
    
    user_id = reply.from_user.id
    warns_db.delete_one({"u": user_id, "c": message.chat.id})
    
    await message.reply(f"✅ {reply.from_user.mention} ke warnings reset kar diye gaye hain.")
    await send_log(client, message.chat.title, message.chat.id, reply.from_user, "Warns Reset", f"By Admin {message.from_user.id}")

# --- 🛡 SECURITY MANAGER ---
@app.on_message(filters.group & ~filters.service, group=1)
async def security_manager(client, message):
    if not message.from_user: return
    if await is_admin(message.chat.id, message.from_user.id): return
    
    text = (message.text or message.caption or "").lower()
    if not text: return 

    chat_id, user_id = message.chat.id, message.from_user.id
    violation = None

    link_on = await get_setting(chat_id, "link")
    abuse_on = await get_setting(chat_id, "abuse")

    # Smart Abuse Filter
    if abuse_on:
        for word in BANNED_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", text):
                violation = "𝐀𝐛𝐮𝐬𝐢𝐯𝐞 𝐖𝐨𝐫𝐝𝐬"
                break

    if not violation and link_on and re.search(URL_PATTERN, text):
        violation = "𝐔𝐧𝐰𝐚𝐧𝐭𝐞𝐝 𝐋𝐢𝐧𝐤𝐬"

    if violation:
        try:
            await message.delete() # Sirf ganda message delete hoga
            warn_data = warns_db.find_one({"u": user_id, "c": chat_id})
            count = (warn_data["n"] if warn_data else 0) + 1
            
            if count >= 3:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                warns_db.delete_one({"u": user_id, "c": chat_id})
                await message.reply(f"🚫 {message.from_user.mention} ᴍᴜᴛᴇᴅ! (3/3 Warns for {violation})")
                await send_log(client, message.chat.title, chat_id, message.from_user, "User Muted", violation, 3)
            else:
                warns_db.update_one({"u": user_id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
                await message.reply(f"⚠️ {message.from_user.mention}, **{violation}** allowed nahi hain! ({count}/3)")
                await send_log(client, message.chat.title, chat_id, message.from_user, "Warning Issued", violation, count)
        except ChatAdminRequired:
            pass # Bot admin nahi hai toh kuch nahi karega
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    app.run()
