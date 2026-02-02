import os
import asyncio
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, InputMediaPhoto
from pyrogram.enums import ChatMemberStatus
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_LINK

# --- RENDER PORT FIX ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Antu Abuse Bot is Online!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT SETUP ---
app = Client("AntuAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- CONFIGURATION ---
LOG_IMG = "https://graph.org/file/fcc36307f247bbfc623cd-e736a75b263077982a.jpg" 
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
HELP_IMG = "https://graph.org/file/41d3fd1a4182030eb519c-fd35dff2f1f579d076.jpg"

LOG_GROUP = -1003867805165  
users_db = set(); warns_db = {}; groups_db = set()

# 🔥 FULL MASTER BANNED LIST
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

def get_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)],
        [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url="https://t.me/AntuAbusebot?startgroup=true")],
        [InlineKeyboardButton("🛠 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_menu")]
    ])

# 1️⃣ START COMMAND + LOG
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.chat.id not in users_db:
        users_db.add(message.chat.id)
        log_txt = (
            f"👤 **#ɴᴇᴡ_ᴜꜱᴇʀ_ꜱᴛᴀʀᴛᴇᴅ**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"**ɴᴀᴍᴇ:** {message.from_user.mention}\n"
            f"**ɪᴅ:** `{message.from_user.id}`\n"
            f"**ᴜꜱᴇʀɴᴀᴍᴇ:** @{message.from_user.username}\n"
            f"━━━━━━━━━━━━━━━"
        )
        await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)
    
    start_caption = (
        f"👋 **ʜᴇʟʟᴏ {message.from_user.mention}!**\n\n"
        f"ɪ ᴀᴍ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**, ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛᴏʀ.\n\n"
        f"🛡️ **ɪ ᴄᴀɴ:**\n"
        f"• ᴅᴇʟᴇᴛᴇ ᴀʙᴜꜱɪᴠᴇ ᴡᴏʀᴅꜱ\n"
        f"• ʀᴇᴍᴏᴠᴇ ꜱᴘᴀᴍ ʟɪɴᴋꜱ\n"
        f"• ᴍᴜᴛᴇ ʀᴇᴘᴇᴀᴛᴇᴅ ᴏꜰꜰᴇɴᴅᴇʀꜱ\n\n"
        f"**ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏ!**"
    )
    await message.reply_photo(photo=START_IMG, caption=start_caption, reply_markup=get_main_buttons())

# 2️⃣ HELP COMMAND (MESSAGE & CALLBACK)
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    help_text = (
        "🛠 **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ - ʜᴇʟᴘ ᴍᴇɴᴜ**\n\n"
        "• `/mute` - Mute a user (Reply)\n"
        "• `/unmute` - Unmute a user (Reply)\n"
        "• `/ban` - Ban a user (Reply)\n"
        "• `/unban` - Unban a user (Reply)\n"
        "• `/info` - Get user details\n\n"
        "🛡️ **ᴀᴜᴛᴏ ꜱʏꜱᴛᴇᴍ:**\n"
        "• 3 Warns = Auto Mute.\n"
        "• slurs/Links = Auto Delete + Warn."
    )
    await message.reply_photo(photo=HELP_IMG, caption=help_text, reply_markup=get_main_buttons())

@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client, callback_query):
    help_text = (
        "🛠 **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ - ʜᴇʟᴘ ᴍᴇɴᴜ**\n\n"
        "• `/mute` - Mute a user\n"
        "• `/unmute` - Unmute a user\n"
        "• `/info` - User details\n\n"
        "🛡️ **ꜱʏꜱᴛᴇᴍ:**\n"
        "Bot automatically deletes bad words and links. If a user gets 3 warnings, I will mute them automatically."
    )
    await callback_query.edit_message_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_start")]])
    )

@app.on_callback_query(filters.regex("back_start"))
async def back_callback(client, callback_query):
    start_caption = f"👋 **ʜᴇʟʟᴏ!**\n\nɪ ᴀᴍ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**. ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴛᴏ ᴋᴇᴇᴘ ɪᴛ ᴄʟᴇᴀɴ ᴀɴᴅ ꜱᴀꜰᴇ!"
    await callback_query.edit_message_caption(caption=start_caption, reply_markup=get_main_buttons())

# 3️⃣ INFO COMMAND
@app.on_message(filters.command("info"))
async def info_cmd(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    info_cap = (
        f"👤 **ᴜꜱᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"**ɴᴀᴍᴇ:** {user.mention}\n"
        f"**ɪᴅ:** `{user.id}`\n"
        f"**ᴜꜱᴇʀɴᴀᴍᴇ:** @{user.username if user.username else 'None'}\n"
        f"**ʟɪɴᴋ:** [ᴘᴇʀᴍᴀʟɪɴᴋ](tg://user?id={user.id})\n"
        f"━━━━━━━━━━━━━━━"
    )
    await message.reply_photo(photo=HELP_IMG, caption=info_cap)

# 4️⃣ BOT ADDED TO GROUP LOG
@app.on_message(filters.new_chat_members)
async def bot_added_handler(client, message):
    if any(m.id == (await client.get_me()).id for m in message.new_chat_members):
        chat = message.chat
        groups_db.add(chat.id)
        try: link = await client.export_chat_invite_link(chat.id)
        except: link = "No Permission"

        log_txt = (
            f"📥 **#ʙᴏᴛ_ᴀᴅᴅᴇᴅ_ᴛᴏ_ɢᴄ**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"**ᴛɪᴛʟᴇ:** {chat.title}\n"
            f"**ɪᴅ:** `{chat.id}`\n"
            f"**ʟɪɴᴋ:** {link}\n"
            f"**ᴀᴅᴅᴇᴅ ʙʏ:** {message.from_user.mention}\n"
            f"━━━━━━━━━━━━━━━"
        )
        await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)

# 5️⃣ CORE FILTER (SLURS + LINKS) & LOGS
@app.on_message(filters.group & (filters.text | filters.caption) & ~filters.command(["help", "start", "info", "welcome", "stats", "mute", "unmute"]), group=-1)
async def main_filter(client, message):
    if not message.from_user: return
    
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or message.from_user.id == OWNER_ID:
            return
    except: pass

    text = (message.text or message.caption or "").lower()
    clean_text = re.sub(r'[^a-z0-9\s]', '', text)
    is_link = re.search(r"(http|https)://|t\.me/|[a-z0-9]+\.[a-z]{2,}", text)
    is_abuse = any(word in text or word in clean_text for word in BANNED_WORDS)

    if is_abuse or is_link:
        user = message.from_user
        chat = message.chat
        reason = "ᴀʙᴜꜱᴇ/ɢᴀᴀʟɪ" if is_abuse else "ʟɪɴᴋ/ꜱᴘᴀᴍ"
        warns_db[user.id] = warns_db.get(user.id, 0) + 1
        w = warns_db[user.id]
        
        await message.delete()

        if w >= 3:
            await client.restrict_chat_member(chat.id, user.id, ChatPermissions(can_send_messages=False))
            log_tag = "#ᴜꜱᴇʀ_ᴍᴜᴛᴇᴅ"
            warns_db[user.id] = 0
            rep_text = f"🚫 {user.mention} has been **Muted**! (Reason: 3/3 Warns for {reason})"
        else:
            log_tag = "#ᴜꜱᴇʀ_ᴡᴀʀɴᴇᴅ"
            rep_text = f"⚠️ {user.mention}, don't use **{reason}**! [{w}/3]"

        log_txt = (
            f"🚨 **{log_tag}**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"**👤 ᴜꜱᴇʀ:** {user.mention}\n"
            f"**🆔 ɪᴅ:** `{user.id}`\n"
            f"**👥 ɢʀᴏᴜᴘ:** {chat.title}\n"
            f"**📝 ʀᴇᴀꜱᴏɴ:** {reason}\n"
            f"**📊 ꜱᴛᴀᴛᴜꜱ:** {w}/3\n"
            f"━━━━━━━━━━━━━━━"
        )
        await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)
        
        msg = await message.reply_text(rep_text)
        await asyncio.sleep(10)
        await msg.delete()

print("🚀 Antu Abuse Bot (Full Menu & Logs) is Online!")
app.run()
