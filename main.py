import os, asyncio, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, CallbackQuery
from pyrogram.enums import ChatMemberStatus, ChatType
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, LOG_GROUP_ID, MONGO_URL

# --- 🌐 AUTO-HOST SERVER (Render Fix) ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Victor Advanced Bot is Live!")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer).serve_forever(), daemon=True).start()

# --- 🛠 DB & BOT SETUP ---
mongo = MongoClient(MONGO_URL)
db = mongo.AntuAbuseBot
warns_db = db.warns
bio_cache = db.bio_cache 
app = Client("VictorAdminBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🖼 ASSETS ---
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+)"
# 🔥 MASTER BANNED LIST (Including all your words)
BANNED_WORDS = [
    "randi ke bache", "randi ka bacha", "gandu", "maiya rand", "madhrchod", "ma na chudaya",
    "chudata", "chudwa", "chudai", "bhosdike", "lund", "louda", "loda", "chut", "gand",
    "gand marwa", "gand mra", "kalap", "klp", "kalpo", "kalapo", "kalp", "chud", "chudi",
    "baap", "biz", "bizz", "gaand", "gnd", "bhosda", "bhosdi", "aukaat", "aukat",
    "motherchodo", "motherchod", "bhnchod", "bahanchod", "bur", "burr", "burrr", "bacho",
    "behen ki lowdii", "teri behen ko chodu", "teri amaa ka bhosraa", "behen ko chod",
    "bhn ko chodke", "bahan ko chodke", "randi", "rand", "lowda", "loda", "randi ka bizz",
    "join my bio", "massage kro", "dm karo", "dmm karo", "baby", "whatsapp", "call", "join",
    "mc", "bc", "bsdk", "randibaaz", "boobs", "bobe", "boob", "suck", "fuck", "motherfucker",
    "pussy", "aah", "ah", "buy", "sell", "join my bioo", "biooo", "bio", "bioo", "bioooo",
    "biooooo", "copyright", "rape", "sex", "sexual", "pornograpy", "harm", "malware", "drug",
    "mia khalifa", "sunny leone", "xxx", "xxxx", "xxxxxx", "porn", "ganja", "naseela",
    "nasila", "nasela", "drugs", "boys come", "girls come", "boy's come", "girl's come",
    "randi ki bachi", "sexy", "sexx", "sexxx", "sexxxxx", "teri maa chodunga", "chodunga",
    "chodungi", "chod", "bahan ki chut", "chikni", "chikna", "chod dalunga", "choddalunga",
    "chod daalunga", "choddaalunga", "loude", "lowde", "lode", "rs", "charge", "videocall",
    "voicecall", "needs group", "10k", "8k", "need groups", "buyer", "seller", "selling",
    "paid", "hack", "mod apk", "mod", "injector", "carding", "hacking", "hacker", "data",
    "number", "photo", "video", "call girl", "call boy", "aajao baby"
]
MESSAGES_COUNT = {}

# --- 🛡 HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

async def check_bio_optimized(user_id):
    if bio_cache.find_one({"u": user_id, "safe": True}): return False
    try:
        user = await app.get_users(user_id)
        has_link = bool(re.search(URL_PATTERN, user.bio.lower())) if user.bio else False
        if not has_link: bio_cache.update_one({"u": user_id}, {"$set": {"safe": True}}, upsert=True)
        return has_link
    except: return False

# --- 🏠 UI & BUTTONS ---
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("📜 ʜᴇʟᴘ", callback_data="help_data"), InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/radhesupport")]
    ])
    await message.reply_photo(photo=START_IMG, caption=f"👋 **ʜᴇʟʟᴏ {message.from_user.mention}!**\n\nᴍᴀɪɴ **ᴠɪᴄᴛᴏʀ ᴀᴅᴠᴀɴᴄᴇᴅ** ʙᴏᴛ ʜᴏᴏɴ. ᴍᴀɪɴ ᴀᴀᴘᴋᴇ ɢʀᴏᴜᴘ ᴋᴏ sᴘᴀᴍ, ɢᴀᴀʟɪ, ᴀᴜʀ ꜰᴀʟᴛᴜ ʟɪɴᴋs sᴇ ʙᴀᴄʜᴀ sᴀᴋᴛᴀ ʜᴏᴏɴ.", reply_markup=buttons)

@app.on_callback_query(filters.regex("help_data"))
async def help_callback(client, callback_query: CallbackQuery):
    help_text = "🛠 **ʜᴇʟᴘ ᴍᴇɴᴜ**\n\n`/ban` - Ban User\n`/mute` - Mute User\n`/unmute` - Unmute\n`/info` - User Info\n`/guide` - Setup Guide"
    await callback_query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="start_back")]]))

@app.on_callback_query(filters.regex("start_back"))
async def back_to_start(client, callback_query: CallbackQuery):
    await callback_query.message.delete()
    await start(client, callback_query.message)

# --- ⚙️ SECURITY & ADMIN ---
@app.on_message(filters.group & ~filters.service)
async def security_manager(client, message):
    if not message.from_user or await is_admin(message.chat.id, message.from_user.id): return
    
    user_id, chat_id = message.from_user.id, message.chat.id
    text = (message.text or message.caption or "").lower()
    violation = None

    now = asyncio.get_event_loop().time()
    MESSAGES_COUNT[user_id] = [t for t in MESSAGES_COUNT.get(user_id, []) if now - t < 5]
    MESSAGES_COUNT[user_id].append(now)
    if len(MESSAGES_COUNT[user_id]) > 5: violation = "Flood Spamming"
    elif any(w in text for w in BANNED_WORDS): violation = "Abusive Language"
    elif re.search(URL_PATTERN, text): violation = "Link Sharing"
    elif await check_bio_optimized(user_id): violation = "Link in Bio"

    if violation:
        try: await message.delete()
        except: pass
        warn_data = warns_db.find_one({"u": user_id, "c": chat_id})
        count = (warn_data["n"] if warn_data else 0) + 1
        if count >= 3:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
            warns_db.delete_one({"u": user_id, "c": chat_id})
            await message.reply(f"🚫 **ᴍᴜᴛᴇᴅ ꜰᴏʀᴇᴠᴇʀ**\n👤 **ᴜsᴇʀ:** {message.from_user.mention}\n⚠️ **ʀᴇᴀsᴏɴ:** {violation}\n📊 **ᴡᴀʀɴs:** 3/3")
        else:
            warns_db.update_one({"u": user_id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
            await message.reply(f"⚠️ **sᴇᴄᴜʀɪᴛʏ ᴡᴀʀɴɪɴɢ**\n👤 {message.from_user.mention}\n🛡️ **ᴡᴀʀɴ:** {count}/3\n🚫 **ʀᴇᴀsᴏɴ:** {violation}")

@app.on_message(filters.command(["ban", "mute", "unban", "unmute"]) & filters.group)
async def admin_actions(client, message):
    if not await is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return await message.reply("Reply to a user!")
    target = message.reply_to_message.from_user
    cmd = message.command[0]
    try:
        if cmd == "ban": await client.ban_chat_member(message.chat.id, target.id)
        elif cmd == "mute": await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=False))
        elif cmd == "unmute": await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True))
        await message.reply(f"✅ **ᴀᴄᴛɪᴏɴ:** `{cmd.upper()}`\n👤 **ᴜsᴇʀ:** {target.mention}")
        await client.send_message(LOG_GROUP_ID, f"📝 **#LOG**\nAction: {cmd}\nTarget: {target.mention}\nBy: {message.from_user.mention}")
    except Exception as e: await message.reply(f"Error: {e}")

@app.on_message(filters.command("info"))
async def info_cmd(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.reply_text(f"👤 **ᴜsᴇʀ ɪɴꜰᴏ**\n\n**ɴᴀᴍᴇ:** {user.first_name}\n**ɪᴅ:** `{user.id}`\n**ᴜsᴇʀɴᴀᴍᴇ:** @{user.username}")

@app.on_message(filters.command("guide"))
async def guide_cmd(client, message):
    await message.reply_text("📖 **sᴇᴛᴜᴘ ɢᴜɪᴅᴇ**\n\n1. Bot ko Admin banayein.\n2. MongoDB link sahi daalein.\n3. Log Group ID add karein.\n4. Requirements.txt upload karein.")

app.run()
