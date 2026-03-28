import os, asyncio, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid
from pymongo import MongoClient

# --- 📁 CONFIG ---
try:
    from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, LOG_GROUP_ID, MONGO_URL
except ImportError:
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH", "your_hash")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_token")
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", 0))
    MONGO_URL = os.environ.get("MONGO_URL", "")

# --- 🌐 SERVER ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Antu Abuse Bot is Live!")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 🛠 DB SETUP ---
mongo = MongoClient(MONGO_URL)
db = mongo.AntuAbuseBot
warns_db = db.warns
users_db = db.users
approved_db = db.approved
chats_db = db.chats

app = Client("AntuAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🖼 ASSETS ---
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+|@[a-zA-Z0-9_]+)"

def get_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ➕", url=f"https://t.me/{app.me.username}?startgroup=true"),
         InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/YourChannel")]
    ])

BANNED_WORDS = ["randi", "gandu", "mc", "bc", "bhenchod", "lund", "chutiya", "porn", "sex", "bsdk", "maderchod", "gaand", "bhonsdi", "bakchod", "lavda", "lodhu", "pussy", "dick", "fucker", "bastard", "tatte", "saala", "kamine", "haramkhor", "betichod", "madarchod", "gandmasti", "lundtop", "rakhail", "chut", "jhaat", "muth", "mutthal", "chinaal", "kutiya", "bhadvva", "dalal", "haramzada", "behenkelode", "maakelode", "ganduchand", "bhikari", "najayaz", "randa", "kutta", "kaminey", "suar", "gadha", "ullu", "charsi", "behenkichut", "maakichut", "gaandfat", "gaandchat", "lodu", "mullu", "katua", "hijra", "namard", "chhaka", "panchut", "paki", "asshole", "bitch", "slut", "whore", "nigga", "nigger", "cock", "cunt", "faggot", "tit", "boobs", "orgasm", "masturbate", "randibaaz", "lundure", "jhaantu", "gaandmare", "gaandmaru", "chudai", "chodna", "chudne", "chudwa", "bhosadpappu", "bhosdike", "bhosadi", "bhosdika", "tharki", "kameene", "piss", "shit", "crap", "dickhead", "motherfucker", "bhanchod", "benchod", "bhenchod", "teri_maa_ki", "teri_behen_ki"]

# --- 🛡 HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

def is_approved(chat_id, user_id):
    return approved_db.find_one({"c": chat_id, "u": user_id})

# --- 📝 LOGGING ---
async def send_log(client, chat_title, chat_id, user, action, reason, count=None):
    if not LOG_GROUP_ID: return
    try:
        log_text = (f"<b>📊 #ANTU_LOGS</b>\n━━━━━━━━━━━━━━━━━━━━\n"
                    f"📝 <b>Action:</b> {action}\n👤 <b>User:</b> {user.mention}\n"
                    f"🆔 <b>User ID:</b> <code>{user.id}</code>\n🌐 <b>Chat:</b> {chat_title}\n"
                    f"📍 <b>Chat ID:</b> <code>{chat_id}</code>\n⚠️ <b>Reason:</b> {reason}\n")
        if count: log_text += f"🔢 <b>Warn Level:</b> {count}/3\n"
        log_text += f"━━━━━━━━━━━━━━━━━━━━"
        await client.send_photo(LOG_GROUP_ID, photo=START_IMG, caption=log_text)
    except: pass

# --- 🏠 COMMANDS ---

@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    if not users_db.find_one({"u": user.id}):
        users_db.insert_one({"u": user.id})
    if message.chat.type != ChatType.PRIVATE:
        if not chats_db.find_one({"c": message.chat.id}):
            chats_db.insert_one({"c": message.chat.id})
            
    caption = (f"✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀɴᴛᴜ ᴀʙᴜsᴇ ʙᴏᴛ** ✨\n\n🛡️ **ʜᴇʟʟᴏ {user.mention},**\n"
               f"ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.\n\n"
               f"📌 **ғᴇᴀᴛᴜʀᴇs:**\n └─ ᴀɴᴛɪ-ᴀʙᴜsᴇ\n └─ ᴀɴᴛɪ-ʟɪɴᴋ\n └─ ᴀᴜᴛᴏ-ᴡᴀʀɴ (3/3 = Mute)\n └─ ᴀᴘᴘʀᴏᴠᴇ sʏsᴛᴇᴍ")
    await message.reply_photo(photo=START_IMG, caption=caption, reply_markup=get_buttons())

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message):
    u_count = users_db.count_documents({})
    c_count = chats_db.count_documents({})
    await message.reply_text(f"📊 **Bot Stats:**\n\n👤 **Total Users:** {u_count}\n🌐 **Total Chats:** {c_count}")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message: return await message.reply("Reply to a message to broadcast!")
    msg = await message.reply("🚀 Broadcasting...")
    success, failed = 0, 0
    for user in users_db.find():
        try:
            await message.reply_to_message.copy(user["u"])
            success += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(user["u"])
            success += 1
        except: failed += 1
    await msg.edit(f"✅ **Done!**\nSent: {success}\nFailed: {failed}")

@app.on_message(filters.command("approve") & filters.group)
async def approve_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return await message.reply("Reply to user to approve!")
    user = message.reply_to_message.from_user
    approved_db.update_one({"c": message.chat.id, "u": user.id}, {"$set": {"u": user.id}}, upsert=True)
    await message.reply_text(f"✅ {user.mention} has been **Approved** in this chat!")

@app.on_message(filters.command("unapprove") & filters.group)
async def unapprove_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    user = message.reply_to_message.from_user
    approved_db.delete_one({"c": message.chat.id, "u": user.id})
    await message.reply_text(f"❌ {user.mention} is no longer approved.")

@app.on_message(filters.command("reset") & filters.group)
async def reset_warns(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    user = message.reply_to_message.from_user
    warns_db.delete_one({"u": user.id, "c": message.chat.id})
    await message.reply_text(f"✅ Warnings reset for {user.mention}.")

# --- 🛡 SECURITY MANAGER ---
@app.on_message(filters.group & ~filters.service, group=1)
async def security_manager(client, message):
    if not message.from_user or not message.text: return
    # 🚫 Commands ko ignore karein
    if message.text.startswith(("/", "!")): return
    # 🛡 Admin aur Approved users ko ignore karein
    if await is_admin(message.chat.id, message.from_user.id) or is_approved(message.chat.id, message.from_user.id):
        return
    
    text = message.text.lower()
    violation = None

    for word in BANNED_WORDS:
        pattern = rf"\b" + "".join([f"{re.escape(c)}[*@#%._-]*" for c in word]) + rf"\b"
        if re.search(pattern, text):
            violation = "𝐀𝐛𝐮𝐬𝐢𝐯𝐞 𝐖𝐨𝐫𝐝𝐬"
            break
    if not violation and re.search(URL_PATTERN, text):
        violation = "𝐔𝐧𝐰𝐚𝐧𝐭𝐞𝐝 𝐋ɪɴᴋs"

    if violation:
        try:
            await message.delete()
            chat_id, user_id = message.chat.id, message.from_user.id
            warn_data = warns_db.find_one({"u": user_id, "c": chat_id})
            count = (warn_data["n"] if warn_data else 0) + 1
            
            if count >= 3:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                warns_db.delete_one({"u": user_id, "c": chat_id})
                await message.reply(f"🚫 {message.from_user.mention} **Muted**! (3/3 Warnings for {violation})", reply_markup=get_buttons())
                await send_log(client, message.chat.title, chat_id, message.from_user, "Auto-Mute", violation, 3)
            else:
                warns_db.update_one({"u": user_id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
                await message.reply(f"⚠️ {message.from_user.mention}, **{violation}** allowed nahi hai! ({count}/3)", reply_markup=get_buttons())
                await send_log(client, message.chat.title, chat_id, message.from_user, "Warning", violation, count)
        except: pass

if __name__ == "__main__":
    app.run()
