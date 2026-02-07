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

# --- 🌐 AUTO-HOST SERVER (For Render/Koyeb) ---
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
WELCOME_IMG = "https://graph.org/file/4c5f6f721550cee5255f7-4391f4d3496ba37dfe.jpg"
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+|@[a-zA-Z0-9_]+)"

# 🔥 MEGA MASTER BANNED LIST (Added your full list)
BANNED_WORDS = [
    "randi", "randwa", "gandu", "madarchod", "maderchod", "madhrchod", "mc", "bc", "bhenchod", "behenchod", 
    "bhnchod", "bahanchod", "bhosdike", "bhosadi", "bsdk", "lund", "loda", "lowda", "lauda", "louda", "loude", 
    "lowde", "lode", "chut", "chutiya", "chutmarika", "gaand", "gand", "gandmare", "gandmareu", "muth", 
    "muthiya", "muthal", "behen k lode", "behen ke lode", "behen k takke", "tattu", "tatte", "jhant", "jhaant",
    "harami", "kamina", "kamine", "najaiz", "raand", "saala", "sala", "saali", "sali", "gnd", "bhosda", 
    "bhosdi", "aukaat", "aukat", "motherchodo", "motherchod", "bur", "burr", "burrr", "bacho", 
    "behen ki lowdii", "teri behen ko chodu", "teri amaa ka bhosraa", "behen ko chod", "bhn ko chodke", 
    "bahan ko chodke", "randibaaz", "kalap", "klp", "kalpo", "kalapo", "kalp", "chud", "chudi", "baap", "biz", "bizz",
    "sex", "porn", "xxx", "xxxx", "xxxxxx", "xvideo", "chudai", "chodo", "chodas", "rape", "gangbang", 
    "condom", "bra", "panty", "nude", "nudes", "pic dalo", "video call", "vc krlo", "muthi", "hastmaithun", 
    "tharak", "tharki", "lund topa", "vagina", "penis", "boobs", "bobe", "boob", "suck", "pussy", "aah", "ah", 
    "pornograpy", "mia khalifa", "sunny leone", "sexy", "sexx", "sexxx", "sexxxxx", "chikni", "chikna", 
    "call girl", "call boy", "videocall", "voicecall", "sexual", "pornograpy",
    "randi ke bache", "randi ka bacha", "randi ki bachi", "maiya rand", "maa chuda", "behen chuda", 
    "baap ko mat sikha", "teri ma ki", "teri bhen ki", "maa ki chut", "bhen ki chut", "ma na chudaya", 
    "chudata", "chudwa", "teri maa chodunga", "chodunga", "chodungi", "chod", "bahan ki chut", 
    "chod dalunga", "choddalunga", "chod daalunga", "choddaalunga",
    "join my channel", "sub4sub", "promotion", "paid promotion", "earn money", "free recharge", "loot", 
    "join fast", "invest money", "trading bot", "telegram bot", "follow me", "subscribe", "dm for", 
    "contact for", "whatsapp group", "join my bio", "massage kro", "dm karo", "dmm karo", "whatsapp", 
    "call", "join", "buy", "sell", "join my bioo", "biooo", "bio", "bioo", "bioooo", "biooooo", "biooooo", 
    "needs group", "10k", "8k", "need groups", "buyer", "seller", "selling", "paid", "rs", "charge", 
    "aajao baby", "baby", "boys come", "girls come", "boy's come", "girl's come", "massage kro",
    "hack", "mod apk", "mod", "injector", "carding", "hacking", "hacker", "data", "number", "photo", 
    "video", "malware", "drug", "ganja", "naseela", "nasila", "nasela", "drugs", "copyright", "harm",
    "katwa", "mulla", "bhakt", "andhbhakt", "atankwadi", "terrorist", "kafir", "kaffir", "suar", 
    "suar ki aulad", "dog", "kutta", "kutte ka bacha",
    "fuck", "fucker", "fucking", "bitch", "asshole", "bastard", "dick", "pussy", "slut", "whore", 
    "motherfucker", "shutup", "stfu", "dumbass", "idiot"
]

# --- 🔘 REUSABLE BUTTONS ---
async def get_vip_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("♻ 𝐀ᴅᴅ 𝐌𝝴 𝝸𝝶 𝐘𝞂𝞄𝐑 𝐆𝐑𝞂𝞄𝞀 ♻", url="https://t.me/AntuAbusebot?startgroup=true")],
        [InlineKeyboardButton("❂ 𝐔𝛒ᴅ𝛂𝛕𝛆 ❂", url="https://t.me/radhesupport"), 
         InlineKeyboardButton("❂ 𝐒𝛖𝛒𝛒𝛔ʀ𝛕 ❂", url="https://t.me/+PKYLDIEYiTljMzMx")]
    ])

# --- 🛡 HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

async def get_setting(chat_id, key):
    res = settings_db.find_one({"c": chat_id})
    return res.get(key, True) if res else True

async def check_user_bio(user_id):
    try:
        user = await app.get_users(user_id)
        if user and user.bio:
            return bool(re.search(URL_PATTERN, user.bio.lower()))
    except: pass
    return False

# --- 🏠 START COMMAND ---
@app.on_message(filters.command("start"))
async def start(client, message):
    if not users_db.find_one({"u": message.from_user.id}):
        users_db.insert_one({"u": message.from_user.id})
    if message.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
        if not chats_db.find_one({"c": message.chat.id}):
            chats_db.insert_one({"c": message.chat.id})

    buttons = await get_vip_buttons()
    caption = (
        f"👋 **ʜᴇʟʟᴏ** {message.from_user.mention}\n\n"
        f"ɪ ᴀᴍ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**.\n\n"
        f"✨ **ᴍᴀɪɴ ꜰᴇᴀᴛᴜʀᴇꜱ:**\n"
        f"┌─🚀 **ᴀʙᴜꜱɪᴠᴇ ᴡᴏʀᴅꜱ ꜰɪʟᴛᴇʀ**\n"
        f"├─🚀 **ʙɪᴏ ʟɪɴᴋᴇʀ ʙʟᴏᴄᴋᴇʀ**\n"
        f"└─🚀 **ᴀɴᴛɪ-ᴄʜᴀɴɴᴇʟ ᴍᴏᴅᴇ**\n\n"
        f"ᴍᴜᴊʜᴇ ᴀᴅᴍɪɴ ʙᴀɴᴀᴏ ᴀᴜʀ ɢʀᴏᴜᴘ ꜱᴀᴀꜰ ʀᴀᴋʜᴏ!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_photo(photo=START_IMG, caption=caption, reply_markup=buttons)

# --- 👋 WELCOME MESSAGE ---
@app.on_message(filters.new_chat_members)
async def welcome_member(client, message):
    for member in message.new_chat_members:
        if member.is_self: continue
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("♻ 𝐀ᴅᴅ 𝐌𝝴 𝝸𝝶 𝐘𝞂𝞄𝐑 𝐆𝐑𝞂𝞄𝞀 ♻", url="https://t.me/AntuAbusebot?startgroup=true")],
            [InlineKeyboardButton("📜 𝐆𝐑𝐎𝐔𝐏 𝐑𝐔𝐋𝐄𝐒", callback_data="show_rules")],
            [InlineKeyboardButton("❂ 𝐔𝛒ᴅ𝛂𝛕𝛆 ❂", url="https://t.me/radhesupport"), 
             InlineKeyboardButton("❂ 𝐒𝛖𝛒𝛒𝛔ʀ𝛕 ❂", url="https://t.me/+PKYLDIEYiTljMzMx")]
        ])
        caption = (f"✨ **𝐖𝐄𝐋𝐂𝐎𝐌𝐄** {member.mention}\n━━━━━━━━━━━━━━━━━━━━\n"
                   f"🌐 **ɢʀᴏᴜᴘ:** {message.chat.title}\n🛡️ **ɪ ᴀᴍ ᴀɴᴛᴜ ᴀʙᴜsᴇ ʙᴏᴛ**\n\n"
                   f"ᴍᴀɪɴ ɪs ɢʀᴏᴜᴘ ᴋᴏ ᴀʙᴜsᴇ ᴀᴜʀ ʟɪɴᴋs sᴇ sᴀғ ʀᴀᴋʜᴜɴɢᴀ!")
        await message.reply_photo(photo=WELCOME_IMG, caption=caption, reply_markup=buttons)

# --- 📜 RULES CALLBACK ---
@app.on_callback_query(filters.regex("show_rules"))
async def rules_cb(client, cb):
    rules = ("📜 **𝐆𝐑𝐎𝐔𝐏 𝐑𝐔𝐋𝐄𝐒**\n━━━━━━━━━━━━━━━━━━━━\n"
             "1️⃣ **ɴᴏ ᴀʙᴜsᴇ:** ɢᴀᴀʟɪ ᴅᴇɴᴇ ᴘᴀʀ ᴡᴀʀɴɪɴɢ ᴍɪʟᴇɢɪ.\n"
             "2️⃣ **ɴᴏ ʟɪɴᴋs:** ᴋᴏɪ ʙʜɪ ʟɪɴᴋ ᴀʟʟᴏᴡ ɴᴀʜɪ ʜᴀɪ.\n"
             "3️⃣ **ʙɪᴏ ᴄʜᴇᴄᴋ:** ᴀᴘɴɪ ʙɪᴏ sᴇ ᴀᴅᴠᴇʀᴛɪsᴇᴍᴇɴᴛ ʜᴀᴛᴀʏᴇɪɴ.\n\n"
             "⚠️ **3 Warns = Permanent Mute!**")
    await cb.answer("Rules Updated!", show_alert=True)
    await cb.message.edit_caption(caption=rules, reply_markup=cb.message.reply_markup)

# --- ⚙️ SETTINGS PANEL ---
@app.on_message(filters.command("settings") & filters.group)
async def settings_panel(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Aap admin nahi hain!")
    
    res = settings_db.find_one({"c": message.chat.id}) or {}
    l_st = "✅ ON" if res.get("link", True) else "❌ OFF"
    a_st = "✅ ON" if res.get("abuse", True) else "❌ OFF"
    
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔗 Link: {l_st}", callback_data="set_link"),
         InlineKeyboardButton(f"🤬 Abuse: {a_st}", callback_data="set_abuse")],
        [InlineKeyboardButton("🗑 Close Panel", callback_data="close_panel")]
    ])
    await message.reply_photo(photo=START_IMG, caption="⚙️ **𝐀𝐍𝐓𝐔 𝐀𝐁𝐔𝐒𝐄 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒**\n━━━━━━━━━━━━━━━━━━━━", reply_markup=btns)

@app.on_callback_query(filters.regex(r"^set_"))
async def update_settings(client, cb):
    if not await is_admin(cb.message.chat.id, cb.from_user.id):
        return await cb.answer("Admin Only!", show_alert=True)
    
    action = cb.data.split("_")[1]
    curr = settings_db.find_one({"c": cb.message.chat.id}) or {}
    new_val = not curr.get(action, True)
    settings_db.update_one({"c": cb.message.chat.id}, {"$set": {action: new_val}}, upsert=True)
    
    res = settings_db.find_one({"c": cb.message.chat.id})
    l_st = "✅ ON" if res.get("link", True) else "❌ OFF"
    a_st = "✅ ON" if res.get("abuse", True) else "❌ OFF"
    
    await cb.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔗 Link: {l_st}", callback_data="set_link"),
         InlineKeyboardButton(f"🤬 Abuse: {a_st}", callback_data="set_abuse")],
        [InlineKeyboardButton("🗑 Close Panel", callback_data="close_panel")]
    ]))
    await cb.answer("Settings Updated!")

@app.on_callback_query(filters.regex("close_panel"))
async def close_panel_cb(client, cb):
    await cb.message.delete()

# --- 🛡 SECURITY MANAGER ---
@app.on_message(filters.group & ~filters.service)
async def security_manager(client, message):
    if not message.from_user or await is_admin(message.chat.id, message.from_user.id): return
    
    chat_id, user_id = message.chat.id, message.from_user.id
    text = (message.text or message.caption or "").lower()
    violation = None

    link_on = await get_setting(chat_id, "link")
    abuse_on = await get_setting(chat_id, "abuse")

    # Violation Checks
    if abuse_on and any(w in text for w in BANNED_WORDS): violation = "ᴀʙᴜsɪᴠᴇ ᴡᴏʀᴅs"
    elif link_on and re.search(URL_PATTERN, text): violation = "ᴜɴᴡᴀɴᴛᴇᴅ ʟɪɴᴋs"
    elif await check_user_bio(user_id): violation = "🔞 ᴀᴅᴠᴇʀᴛɪsᴇᴍᴇɴᴛ ɪɴ ʙɪᴏ"

    if violation:
        try: await message.delete()
        except: pass
        
        warn_data = warns_db.find_one({"u": user_id, "c": chat_id})
        count = (warn_data["n"] if warn_data else 0) + 1
        btns = await get_vip_buttons()

        if count >= 3:
            try:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                warns_db.delete_one({"u": user_id, "c": chat_id})
                cap = (f"🚫 **ғɪɴᴀʟ ᴀᴄᴛɪᴏɴ : ᴍᴜᴛᴇᴅ**\n━━━━━━━━━━━━━━━━━━━━\n"
                       f"👤 **ᴜsᴇʀ:** {message.from_user.mention}\n⚠️ **ʀᴇᴀsᴏɴ:** {violation}\n📊 **ᴡᴀʀɴs:** 3/3")
                await message.reply_photo(photo=START_IMG, caption=cap, reply_markup=btns)
            except: pass
        else:
            warns_db.update_one({"u": user_id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
            cap = (f"🛡️ **ᴀɴᴛᴜ ᴀʙᴜsᴇ ᴡᴀʀɴɪɴɢ**\n━━━━━━━━━━━━━━━━━━━━\n"
                   f"👤 **ᴜsᴇʀ:** {message.from_user.mention}\n🚫 **ᴠɪᴏʟᴀᴛɪᴏɴ:** {violation}\n⚠️ **ᴡᴀʀɴɪɴɢ:** {count}/3")
            await message.reply_photo(photo=START_IMG, caption=cap, reply_markup=btns)

# --- 📊 STATS & BROADCAST ---
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    u = users_db.count_documents({})
    c = chats_db.count_documents({})
    await message.reply_photo(photo=START_IMG, caption=f"📊 **ᴀɴᴛᴜ sᴛᴀᴛs**\n━━━━━━━━━━━━\n👤 **ᴜsᴇʀs:** `{u}`\n🌐 **ᴄʜᴀᴛs:** `{c}`")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast!")
    
    ex = await message.reply("🚀 **Broadcast Starting...**")
    count = 0
    # Broadcast to all tracked groups
    for chat in chats_db.find():
        try:
            await message.reply_to_message.copy(chat["c"])
            count += 1
            await asyncio.sleep(0.3)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except (ChatAdminRequired, PeerIdInvalid, UserIsBlocked):
            chats_db.delete_one({"c": chat["c"]})
        except Exception:
            pass
        
    await ex.edit(f"✅ **Broadcast Done!**\nTotal Reached: `{count}`")

if __name__ == "__main__":
    app.run()
