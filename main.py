import os, asyncio, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatType
from pymongo import MongoClient

# --- 📁 CONFIG IMPORT (OR DEFAULTS) ---
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
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Victor Advanced Bot is Live!")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 🛠 DB & BOT SETUP ---
mongo = MongoClient(MONGO_URL)
db = mongo.AntuAbuseBot
warns_db = db.warns
app = Client("VictorAdminBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🖼 VIP ASSETS ---
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+|@[a-zA-Z0-9_]+)"

# 🔥 MEGA MASTER BANNED LIST (200+ Words: Abuse, Spam, Bio-Links & Adult Protection)
BANNED_WORDS = [
    # --- ABUSE & SLANGS (HINGLISH) ---
    "randi", "randwa", "gandu", "madarchod", "maderchod", "madhrchod", "mc", "bc", "bhenchod", "behenchod", 
    "bhnchod", "bahanchod", "bhosdike", "bhosadi", "bsdk", "lund", "loda", "lowda", "lauda", "louda", "loude", 
    "lowde", "lode", "chut", "chutiya", "chutmarika", "gaand", "gand", "gandmare", "gandmareu", "muth", 
    "muthiya", "muthal", "behen k lode", "behen ke lode", "behen k takke", "tattu", "tatte", "jhant", "jhaant",
    "harami", "kamina", "kamine", "najaiz", "raand", "saala", "sala", "saali", "sali", "gnd", "bhosda", 
    "bhosdi", "aukaat", "aukat", "motherchodo", "motherchod", "bur", "burr", "burrr", "bacho", 
    "behen ki lowdii", "teri behen ko chodu", "teri amaa ka bhosraa", "behen ko chod", "bhn ko chodke", 
    "bahan ko chodke", "randibaaz", "kalap", "klp", "kalpo", "kalapo", "kalp", "chud", "chudi", "baap", "biz", "bizz",

    # --- SEXUAL, NSFW & ADULT CONTENT ---
    "sex", "porn", "xxx", "xxxx", "xxxxxx", "xvideo", "chudai", "chodo", "chodas", "rape", "gangbang", 
    "condom", "bra", "panty", "nude", "nudes", "pic dalo", "video call", "vc krlo", "muthi", "hastmaithun", 
    "tharak", "tharki", "lund topa", "vagina", "penis", "boobs", "bobe", "boob", "suck", "pussy", "aah", "ah", 
    "pornograpy", "mia khalifa", "sunny leone", "sexy", "sexx", "sexxx", "sexxxxx", "chikni", "chikna", 
    "call girl", "call boy", "videocall", "voicecall", "sexual", "pornograpy",

    # --- FAMILY TARGETED ABUSE ---
    "randi ke bache", "randi ka bacha", "randi ki bachi", "maiya rand", "maa chuda", "behen chuda", 
    "baap ko mat sikha", "teri ma ki", "teri bhen ki", "maa ki chut", "bhen ki chut", "ma na chudaya", 
    "chudata", "chudwa", "teri maa chodunga", "chodunga", "chodungi", "chod", "bahan ki chut", 
    "chod dalunga", "choddalunga", "chod daalunga", "choddaalunga",

    # --- SPAM, PROMOTION & LINKS ---
    "join my channel", "sub4sub", "promotion", "paid promotion", "earn money", "free recharge", "loot", 
    "join fast", "invest money", "trading bot", "telegram bot", "follow me", "subscribe", "dm for", 
    "contact for", "whatsapp group", "join my bio", "massage kro", "dm karo", "dmm karo", "whatsapp", 
    "call", "join", "buy", "sell", "join my bioo", "biooo", "bio", "bioo", "bioooo", "biooooo", "biooooo", 
    "needs group", "10k", "8k", "need groups", "buyer", "seller", "selling", "paid", "rs", "charge", 
    "aajao baby", "baby", "boys come", "girls come", "boy's come", "girl's come", "massage kro",

    # --- SCAM, HACKING & HARMFUL ---
    "hack", "mod apk", "mod", "injector", "carding", "hacking", "hacker", "data", "number", "photo", 
    "video", "malware", "drug", "ganja", "naseela", "nasila", "nasela", "drugs", "copyright", "harm",

    # --- RELIGIOUS & TOXIC SLANGS ---
    "katwa", "mulla", "bhakt", "andhbhakt", "atankwadi", "terrorist", "kafir", "kaffir", "suar", 
    "suar ki aulad", "dog", "kutta", "kutte ka bacha",

    # --- ENGLISH ABUSE ---
    "fuck", "fucker", "fucking", "bitch", "asshole", "bastard", "dick", "pussy", "slut", "whore", 
    "motherfucker", "shutup", "stfu", "dumbass", "idiot"
]

# --- 🔘 BUTTONS REUSABLE ---
async def get_vip_buttons(client):
    me = await client.get_me()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/radhesupport"), InlineKeyboardButton("🎧 sᴜᴘᴘᴏʀᴛ", url="https://t.me/+PKYLDIEYiTljMzMx")]
    ])

# --- 🛡 HELPERS ---
async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

async def check_user_bio(user_id):
    try:
        user = await app.get_users(user_id)
        if user and user.bio:
            bio_text = user.bio.lower()
            if any(x in bio_text for x in ["http", "t.me", "@", "www"]):
                return True
        return False
    except: return False

# --- 🏠 START COMMAND ---
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = await get_vip_buttons(client)
    caption = (
        f"✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴠɪᴄᴛᴏʀ ᴀᴅᴠᴀɴᴄᴇᴅ** ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **ʜᴇʟʟᴏ:** {message.from_user.mention}\n"
        f"🛡️ **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ | 🤖 **ᴠᴇʀsɪᴏɴ:** 𝟸.𝟶 (ᴠɪᴘ)\n\n"
        f"ᴍᴀɪɴ ᴀᴀᴘᴋᴇ ɢʀᴏᴜᴘ ᴋᴏ ᴀʙᴜsᴇ, sᴘᴀᴍ, ᴀᴜʀ ꜰᴀʟᴛᴜ ʟɪɴᴋs sᴇ ᴘʀᴏᴛᴇᴄᴛ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ ᴅᴇsɪɢɴ ᴋɪʏᴀ ɢᴀʏᴀ ʜᴏᴏɴ.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_photo(photo=START_IMG, caption=caption, reply_markup=buttons)
    try:
        await client.send_photo(LOG_GROUP_ID, photo=START_IMG, caption=f"🚀 **#sᴛᴀʀᴛ_ʟᴏɢ**\n\n👤 **ᴜsᴇʀ:** {message.from_user.mention}\n🆔 **ɪᴅ:** `{message.from_user.id}`")
    except: pass

# --- ⚙️ SECURITY & BIO CHECK ---
@app.on_message(filters.group & ~filters.service)
async def security_manager(client, message):
    if not message.from_user or await is_admin(message.chat.id, message.from_user.id): return
    
    user_id, chat_id = message.from_user.id, message.chat.id
    text = (message.text or message.caption or "").lower()
    violation = None

    if any(w in text for w in BANNED_WORDS): violation = "ᴀʙᴜsɪᴠᴇ ʟᴀɴɢᴜᴀɢᴇ"
    elif re.search(URL_PATTERN, text): violation = "ᴜɴᴡᴀɴᴛᴇᴅ ʟɪɴᴋs"
    elif await check_user_bio(user_id): violation = "🔞 ᴀᴅᴠᴇʀᴛɪsᴇᴍᴇɴᴛ ɪɴ ʙɪᴏ"

    if violation:
        try: await message.delete()
        except: pass
        
        warn_data = warns_db.find_one({"u": user_id, "c": chat_id})
        count = (warn_data["n"] if warn_data else 0) + 1
        
        if count >= 3:
            try:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                warns_db.delete_one({"u": user_id, "c": chat_id})
                cap = (
                    f"🚫 **ғɪɴᴀʟ ᴀᴄᴛɪᴏɴ : ᴍᴜᴛᴇᴅ**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **ᴜsᴇʀ:** {message.from_user.mention}\n"
                    f"⚠️ **ʀᴇᴀsᴏɴ:** {violation}\n"
                    f"📊 **ᴡᴀʀɴs:** 𝟹/𝟹\n\n"
                    f"**🛑 ᴀᴄᴛɪᴏɴ:** ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ᴍᴜᴛᴇᴅ ꜰᴏʀᴇᴠᴇʀ."
                )
                await message.reply_photo(photo=START_IMG, caption=cap)
                await client.send_photo(LOG_GROUP_ID, photo=START_IMG, caption=f"🔇 **#ᴀᴜᴛᴏ_ᴍᴜᴛᴇ**\n\n👤 **User:** {message.from_user.mention}\n🚫 **Reason:** {violation}")
            except: pass
        else:
            warns_db.update_one({"u": user_id, "c": chat_id}, {"$set": {"n": count}}, upsert=True)
            cap = (
                f"⚠️ **ᴠɪᴄᴛᴏʀ sᴇᴄᴜʀɪᴛʏ ᴡᴀʀɴɪɴɢ**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **ᴜsᴇʀ:** {message.from_user.mention}\n"
                f"🛡️ **ᴡᴀʀɴ:** {count}/3\n"
                f"🚫 **ʀᴇᴀsᴏɴ:** {violation}\n\n"
                f"‼️ **ɴᴏᴛᴇ:** ᴀᴘɴɪ ʙɪᴏ sᴇ ʟɪɴᴋ ʜᴀᴛᴀʏᴇɪɴ ʏᴀ ɢᴀᴀʟɪ ᴍᴀᴛ ᴅᴇɪɴ."
            )
            await message.reply_photo(photo=START_IMG, caption=cap)

# --- ⚒ PUBLIC ADMIN COMMANDS ---
@app.on_message(filters.command(["ban", "mute", "unban", "unmute", "resetwarns"]) & filters.group)
async def admin_actions(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ **Aap admin nahi hain!**")

    if not message.reply_to_message:
        return await message.reply("👤 **Reply to a user!**")
    
    target = message.reply_to_message.from_user
    if target.id == OWNER_ID or target.id == (await client.get_me()).id:
        return await message.reply("❌ **Main is user par action nahi le sakta!**")

    cmd = message.command[0].lower()
    try:
        status = ""
        if cmd == "ban":
            await client.ban_chat_member(message.chat.id, target.id)
            status = "ʙᴀɴɴᴇᴅ"
        elif cmd == "mute":
            await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=False))
            status = "ᴍᴜᴛᴇᴅ"
        elif cmd in ["unmute", "unban"]:
            await client.unban_chat_member(message.chat.id, target.id)
            await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True))
            status = "ᴜɴ-ʀᴇsᴛʀɪᴄᴛᴇᴅ"
        elif cmd == "resetwarns":
            warns_db.delete_one({"u": target.id, "c": message.chat.id})
            status = "ᴡᴀʀɴs ʀᴇsᴇᴛ"

        cap = (
            f"✅ **ᴠɪᴘ ᴀᴄᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **ᴜsᴇʀ:** {target.mention}\n"
            f"🔧 **ᴀᴄᴛɪᴏɴ:** `{cmd.upper()}`\n"
            f"📊 **sᴛᴀᴛᴜs:** {status}\n"
            f"👮 **ᴀᴅᴍɪɴ:** {message.from_user.mention}"
        )
        await message.reply_photo(photo=START_IMG, caption=cap)
        try:
            await client.send_photo(LOG_GROUP_ID, photo=START_IMG, caption=f"📝 **#ᴀᴅᴍɪɴ_ʟᴏɢ**\n\n**Action:** {cmd.upper()}\n**Target:** {target.id}\n**By:** {message.from_user.id}")
        except: pass
    except Exception as e:
        await message.reply(f"❌ **Error:** `{str(e)}`")

# --- 👤 INFO & HELP ---
@app.on_message(filters.command(["info", "help", "guide"]))
async def info_cmds(client, message):
    cmd = message.command[0].lower()
    buttons = await get_vip_buttons(client)
    if cmd == "info":
        user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        cap = (f"👤 **ᴠɪᴘ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs**\n━━━━━━━━━━━━━━━━━━━━\n✨ **ɴᴀᴍᴇ:** {user.first_name}\n🆔 **ɪᴅ:** `{user.id}`\n🔗 **ᴜsᴇʀɴᴀᴍᴇ:** @{user.username or 'None'}")
    elif cmd == "help":
        cap = ("🛠 **ᴠɪᴄᴛᴏʀ ᴀᴅᴠᴀɴᴄᴇᴅ ʜᴇʟᴘ**\n━━━━━━━━━━━━━━━━━━━━\n● `/ban` | `/mute` | `/unmute` \n● `/resetwarns` - Reset warnings\n● `/info` - User details\n● `/guide` - Setup guide")
    else:
        cap = ("📖 **ᴠɪᴄᴛᴏʀ sᴇᴛᴜᴘ ɢᴜɪᴅᴇ**\n━━━━━━━━━━━━━━━━━━━━\n1. Bot ko admin banayein.\n2. Permissions allow karein.\n3. Anti-link/Anti-abuse auto active hai.")

    await message.reply_photo(photo=START_IMG, caption=cap, reply_markup=buttons)

if __name__ == "__main__":
    app.run()
