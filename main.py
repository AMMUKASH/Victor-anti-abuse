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
    LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", 123456789)) # Apna ID dalein
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
settings_db = db.settings

app = Client("AntuAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🖼 ASSETS ---
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+|@[a-zA-Z0-9_]+)"

BANNED_WORDS = [
    "randi", "gandu", "mc", "bc", "bhenchod", "lund", "chutiya", "porn", "sex", "bsdk", "maderchod", 
    "gaand", "bhonsdi", "bakchod", "lavda", "lodhu", "pussy", "dick", "fucker", "bastard", "tatte", 
    "saala", "kamine", "haramkhor", "betichod", "madarchod", "gandmasti", "lundtop", 
    "rakhail", "chut", "jhaat", "muth", "mutthal", "chinaal", "kutiya", "bhadvva", "dalal", "haramzada", 
    "behenkelode", "maakelode", "ganduchand", "bhikari", "najayaz", "randa", "kutta", "kaminey", 
    "suar", "gadha", "ullu", "charsi", "behenkichut", "maakichut", "gaandfat", "gaandchat", "lodu", 
    "mullu", "katua", "hijra", "namard", "chhaka", "panchut", "paki", "asshole", "bitch", "slut", 
    "whore", "nigga", "nigger", "cock", "cunt", "faggot", "tit", "boobs", "orgasm", "masturbate", 
    "randibaaz", "lundure", "jhaantu", "gaandmare", "gaandmaru", "chudai", "chodna", "chudne", 
    "chudwa", "bhosadpappu", "bhosdike", "bhosadi", "bhosdika", "tharki", "kameene", "piss", "shit", 
    "crap", "dickhead", "motherfucker", "bhanchod", "benchod", "bhenchod", "teri_maa_ki", "teri_behen_ki"
]

# --- 📝 LOGGING SYSTEM ---
async def send_log(client, chat_title, chat_id, user, action, reason, count=None):
    if not LOG_GROUP_ID: return
    try:
        log_text = (
            f"<b>📊 #ANTU_LOGS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 <b>Action:</b> {action}\n"
            f"👤 <b>User:</b> {user.mention}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🌐 <b>Chat:</b> {chat_title}\n"
            f"📍 <b>Chat ID:</b> <code>{chat_id}</code>\n"
            f"⚠️ <b>Reason:</b> {reason}\n"
        )
        if count: log_text += f"🔢 <b>Warn Level:</b> {count}/3\n"
        log_text += f"━━━━━━━━━━━━━━━━━━━━"
        
        await client.send_photo(LOG_GROUP_ID, photo=START_IMG, caption=log_text)
    except Exception as e: print(f"Log Error: {e}")

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
        await send_log(client, "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ", "ᴅᴍ", user, "Bot Started", "New User Added to Database")

    caption = (
        f"✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀɴᴛᴜ ᴀʙᴜsᴇ ʙᴏᴛ** ✨\n\n"
        f"🛡️ **ʜᴇʟʟᴏ {user.mention},**\n"
        f"ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴄʜᴀᴛs ᴄʟᴇᴀɴ!\n\n"
        f"📌 **ᴍᴀɪɴ ғᴇᴀᴛᴜʀᴇs:**\n"
        f" └─ ᴀɴᴛɪ-ᴀʙᴜsᴇ (100+ Badwords)\n"
        f" └─ ᴀɴᴛɪ-ʟɪɴᴋ (Auto-Delete)\n"
        f" └─ ᴀᴜᴛᴏ-ᴡᴀʀɴ sʏsᴛᴇᴍ\n"
        f" └─ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ (Ban/Mute)\n\n"
        f"**ᴛᴏ ᴜsᴇ ᴍᴇ, ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!**"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{app.me.username}?startgroup=true")],
        [InlineKeyboardButton("📜 ʜᴇʟᴘ", callback_data="help_menu"), InlineKeyboardButton("📖 ɢᴜɪᴅᴇ", callback_data="guide_menu")],
        [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/YourChannel")]
    ])
    await message.reply_photo(photo=START_IMG, caption=caption, reply_markup=buttons)

# --- 📜 HELP & GUIDE COMMANDS ---
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    text = (
        "🛠 **ᴀɴᴛᴜ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴄᴏᴍᴍᴀɴᴅs**\n\n"
        "● `/warn` - Reply to user to give warn\n"
        "● `/reset` - Reset user warnings\n"
        "● `/mute` - Mute a user from group\n"
        "● `/unmute` - Unmute a user\n"
        "● `/ban` - Ban user from group\n"
        "● `/unban` - Unban user\n"
        "● `/guide` - How to setup bot"
    )
    await message.reply_text(text)

@app.on_message(filters.command("guide"))
async def guide_cmd(client, message):
    text = (
        "📖 **ᴀɴᴛᴜ ᴀʙᴜsᴇ ʙᴏᴛ ɢᴜɪᴅᴇ**\n\n"
        "1. ʙᴏᴛ ᴋᴏ ɢʀᴏᴜᴘ ᴍᴇɪɴ ᴀᴅᴅ ᴋᴀʀᴇɪɴ.\n"
        "2. ʙᴏᴛ ᴋᴏ **ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs** ᴅᴇɪɴ.\n"
        "3. ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ 100+ ɢᴀʟɪʏᴏɴ ᴋᴏ ʙʟᴏᴄᴋ ᴋᴀʀᴇɢᴀ.\n"
        "4. 𝟹 ᴡᴀʀɴs ᴘᴇ ᴜsᴇʀ ᴀᴜᴛᴏ-ᴍᴜᴛᴇ ʜᴏ ᴊᴀᴇɢᴀ."
    )
    await message.reply_text(text)

# --- 🔄 CALLBACK HANDLERS ---
@app.on_callback_query(filters.regex(r"help_menu|guide_menu"))
async def cb_handler(client, query):
    if query.data == "help_menu": await help_cmd(client, query.message)
    elif query.data == "guide_menu": await guide_cmd(client, query.message)
    await query.answer()

# --- ⚔️ MODERATION COMMANDS ---

@app.on_message(filters.command("warn") & filters.group)
async def warn_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return await message.reply("Reply to a user to warn them!")
    
    user = message.reply_to_message.from_user
    chat_id = message.chat.id
    warn_data = warns_db.find_one({"u": user.id, "c": chat_id})
    count = (warn_data["n"] if warn_data else 0) + 1
    
    if count >= 3:
        await client.restrict_chat_member(chat_id, user.id, ChatPermissions(can_send_messages=False))
        warns_db.delete_one({"u": user.id, "c": chat_id})
        await message.reply(f"🚫 {user.mention} has been **Muted** for reaching 3 warnings!")
        await send_log(client, message.chat.title, chat_id, user, "Auto-Mute", "3/3 Warnings reached", 3)
    else:
        warns_db.update_one({"u": user.id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
        await message.reply(f"⚠️ {user.mention} has been warned! ({count}/3)")
        await send_log(client, message.chat.title, chat_id, user, "Manual Warn", f"Warned by {message.from_user.id}", count)

@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return await message.reply("Reply to user to mute!")
    user = message.reply_to_message.from_user
    await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
    await message.reply(f"🔇 {user.mention} muted successfully.")
    await send_log(client, message.chat.title, message.chat.id, user, "Manual Mute", f"Muted by Admin")

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return await message.reply("Reply to user to ban!")
    user = message.reply_to_message.from_user
    await client.ban_chat_member(message.chat.id, user.id)
    await message.reply(f"🔨 {user.mention} banned successfully.")
    await send_log(client, message.chat.title, message.chat.id, user, "Manual Ban", f"Banned by Admin")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    user = message.reply_to_message.from_user
    await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
    await message.reply(f"🔊 {user.mention} unmuted.")

@app.on_message(filters.command("reset") & filters.group)
async def reset_warns(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    user_id = message.reply_to_message.from_user.id
    warns_db.delete_one({"u": user_id, "c": message.chat.id})
    await message.reply(f"✅ Warnings reset for {message.reply_to_message.from_user.mention}.")

# --- 🛡 SECURITY MANAGER ---
@app.on_message(filters.group & ~filters.service, group=1)
async def security_manager(client, message):
    if not message.from_user: return
    if await is_admin(message.chat.id, message.from_user.id): return
    
    text = (message.text or message.caption or "").lower()
    chat_id, user_id = message.chat.id, message.from_user.id
    violation = None

    if await get_setting(chat_id, "abuse"):
        for word in BANNED_WORDS:
            pattern = rf"\b" + "".join([f"{re.escape(c)}[*@#%._-]*" for c in word]) + rf"\b"
            if re.search(pattern, text):
                violation = "𝐀𝐛𝐮𝐬𝐢𝐯𝐞 𝐖𝐨𝐫𝐝𝐬"
                break

    if not violation and await get_setting(chat_id, "link") and re.search(URL_PATTERN, text):
        violation = "𝐔𝐧𝐰𝐚𝐧𝐭𝐞𝐝 𝐋ɪɴᴋs"

    if violation:
        try:
            await message.delete()
            warn_data = warns_db.find_one({"u": user_id, "c": chat_id})
            count = (warn_data["n"] if warn_data else 0) + 1
            if count >= 3:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                warns_db.delete_one({"u": user_id, "c": chat_id})
                await message.reply(f"🚫 {message.from_user.mention} ᴍᴜᴛᴇᴅ! (3/3 Warns for {violation})")
                await send_log(client, message.chat.title, chat_id, message.from_user, "Auto-Mute", violation, 3)
            else:
                warns_db.update_one({"u": user_id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
                await message.reply(f"⚠️ {message.from_user.mention}, **{violation}** allowed nahi hain! ({count}/3)")
                await send_log(client, message.chat.title, chat_id, message.from_user, "Warning Issued", violation, count)
        except ChatAdminRequired: pass

if __name__ == "__main__":
    app.run()
