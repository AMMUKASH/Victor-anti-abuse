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
INFO_IMG = "https://graph.org/file/fcc36307f247bbfc623cd-e736a75b263077982a.jpg"
WARN_IMG = "https://graph.org/file/41d3fd1a4182030eb519c-fd35dff2f1f579d076.jpg"

LOG_GROUP = -1003867805165  
users_db = set(); warns_db = {}; welcome_enabled = {}; groups_db = set()

# 🔥 MASTER BANNED LIST
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
        [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url="https://t.me/AntuAbusebot?startgroup=true")]
    ])

# 1️⃣ START COMMAND
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.chat.id not in users_db:
        users_db.add(message.chat.id)
        try:
            log_txt = f"👤 **#ɴᴇᴡ_ᴜꜱᴇʀ**\n━━━━━━━━━━━━━\n**ɴᴀᴍᴇ:** {message.from_user.mention}\n**ɪᴅ:** `{message.from_user.id}`"
            await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)
        except: pass
    
    start_text = (
        f"👋 **ʜᴇʟʟᴏ {message.from_user.mention},**\n\n"
        "ɪ ᴀᴍ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**, ᴛʜᴇ ᴍᴏꜱᴛ ᴘᴏᴡᴇʀꜰᴜʟ ᴛᴇʟᴇɢʀᴀᴍ "
        "ɢʀᴏᴜᴘ ᴍᴏᴅᴇʀᴀᴛᴏʀ ʙᴏᴛ.\n\n"
        "✨ **ɪ ᴄᴀɴ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ:**\n"
        "┌─🚀 **ᴀʙᴜꜱɪᴠᴇ ᴡᴏʀᴅꜱ**\n"
        "├─🚀 **ꜱᴘᴀᴍ ʟɪɴᴋꜱ**\n"
        "└─🚀 **ᴜɴᴡᴀɴᴛᴇᴅ ᴀᴅꜱ**\n\n"
        "ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴꜱ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ!"
    )
    
    start_btn = get_main_buttons()
    start_btn.inline_keyboard.append([InlineKeyboardButton("🛠 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_menu")])
    await message.reply_photo(photo=START_IMG, caption=start_text, reply_markup=start_btn)

# 2️⃣ HELP HANDLER (CALLBACK & COMMAND)
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await help_logic(message)

@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client, callback_query):
    await help_logic(callback_query.message, edit=True)

async def help_logic(message, edit=False):
    help_text = (
        "🛠 **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ᴍᴇɴᴜ**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 **/start** - ᴛᴏ ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.\n"
        "🔹 **/help** - ᴛᴏ ɢᴇᴛ ᴛʜɪꜱ ᴍᴇɴɢ.\n"
        "🔹 **/info** - ɢᴇᴛ ᴜꜱᴇʀ ᴅᴇᴛᴀɪʟꜱ (ʀᴇᴘʟʏ).\n"
        "🔹 **/welcome on/off** - ᴛᴏɢɢʟᴇ ᴡᴇʟᴄᴏᴍᴇ.\n"
        "🔹 **/stats** - ᴄʜᴇᴄᴋ ʙᴏᴛ ᴅᴀᴛᴀ (ᴏᴡɴᴇʀ).\n\n"
        "🛡 **ꜰᴇᴀᴛᴜʀᴇꜱ:**\n"
        "• **ᴀɴᴛɪ-ʟɪɴᴋ:** ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ʟɪɴᴋꜱ.\n"
        "• **ᴀɴᴛɪ-ᴀʙᴜꜱᴇ:** ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ʙᴀᴅ ᴡᴏʀᴅꜱ.\n"
        "• **ᴡᴀʀɴ ꜱʏꜱᴛᴇᴍ:** 3 ᴡᴀʀɴꜱ = ᴀᴜᴛᴏ ᴍᴜᴛᴇ.\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    buttons = get_main_buttons()
    buttons.inline_keyboard.append([InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_start")])
    
    if edit:
        await message.edit_caption(caption=help_text, reply_markup=buttons)
    else:
        await message.reply_photo(photo=HELP_IMG, caption=help_text, reply_markup=buttons)

@app.on_callback_query(filters.regex("back_start"))
async def back_callback(client, callback_query):
    start_text = (
        f"👋 **ʜᴇʟʟᴏ {callback_query.from_user.mention},**\n\n"
        "ɪ ᴀᴍ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**! ɪ ᴀᴍ ʜᴇʀᴇ ᴛᴏ ᴋᴇᴇᴘ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴄʟᴇᴀɴ."
    )
    start_btn = get_main_buttons()
    start_btn.inline_keyboard.append([InlineKeyboardButton("🛠 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_menu")])
    await callback_query.edit_message_caption(caption=start_text, reply_markup=start_btn)

# 3️⃣ INFO COMMAND
@app.on_message(filters.command("info"))
async def info_cmd(client, message):
    user = message.from_user if not message.reply_to_message else message.reply_to_message.from_user
    status = "ᴏᴡɴᴇʀ 👑" if user.id == OWNER_ID else "ᴜꜱᴇʀ 👤"
    info_text = (
        f"🌟 **ᴜꜱᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ** 🌟\n━━━━━━━━━━━━━━━━━━━\n"
        f"📝 **ɴᴀᴍᴇ:** {user.mention}\n🆔 **ɪᴅ:** `{user.id}`\n"
        f"👤 **ᴜꜱᴇʀɴᴀᴍᴇ:** @{user.username if user.username else 'None'}\n"
        f"🛡️ **ꜱᴛᴀᴛᴜꜱ:** {status}\n━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_photo(photo=INFO_IMG, caption=info_text, reply_markup=get_main_buttons())

# 4️⃣ WELCOME TOGGLE
@app.on_message(filters.command("welcome") & filters.group)
async def welcome_toggle(client, message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] and message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ!")
    except: return
    state = message.command[1].lower() if len(message.command) > 1 else ""
    if state == "on":
        welcome_enabled[message.chat.id] = True
        await message.reply_text("✅ **ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴜʀɴᴇᴅ ᴏɴ!**")
    elif state == "off":
        welcome_enabled[message.chat.id] = False
        await message.reply_text("❌ **ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴜʀɴᴇᴅ ᴏꜰꜰ!**")

@app.on_message(filters.new_chat_members)
async def welcome_handler(client, message):
    groups_db.add(message.chat.id)
    if welcome_enabled.get(message.chat.id, True):
        for member in message.new_chat_members:
            await message.reply_text(f"👋 **ɴᴀᴍᴀꜱᴛᴇ {member.mention}!**\nᴡᴇʟᴄᴏᴍᴇ ᴛᴏ **{message.chat.title}**.", reply_markup=get_main_buttons())

# 5️⃣ CORE FILTER (Antu Abuse System)
@app.on_message(filters.group & (filters.text | filters.caption) & ~filters.command(["help", "start", "info", "welcome", "stats"]), group=-1)
async def main_filter(client, message):
    if not message.from_user: return
    groups_db.add(message.chat.id)
    
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
        user_id = message.from_user.id
        reason_type = "ᴀʙᴜꜱɪᴠᴇ ʟᴀɴɢᴜᴀɢᴇ 🤬" if is_abuse else "ʟɪɴᴋ / ꜱᴘᴀᴍ 🚫"
        warns_db[user_id] = warns_db.get(user_id, 0) + 1
        w = warns_db[user_id]
        
        # Stylish Caption for Warning
        alert_text = (
            f"🛡️ **ᴀɴᴛɪ-ᴀʙᴜꜱᴇ ꜱʏꜱᴛᴇᴍ ᴀʟᴇʀᴛ**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **ᴜꜱᴇʀ:** {message.from_user.mention}\n"
            f"🆔 **ᴜꜱᴇʀ ɪᴅ:** `{user_id}`\n"
            f"👥 **ɢʀᴏᴜᴘ:** `{message.chat.title}`\n"
            f"🚫 **ʀᴇᴀꜱᴏɴ:** {reason_type}\n"
            f"⚠️ **ᴡᴀʀɴɪɴɢꜱ:** `{w}/3`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 **ᴀᴄᴛɪᴏɴ:** Message Deleted Automatically!"
        )

        try:
            await message.delete()
            
            if w >= 3:
                mute_text = (
                    f"🚫 **ᴜꜱᴇʀ ᴍᴜᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **ᴜꜱᴇʀ:** {message.from_user.mention}\n"
                    f"🆔 **ɪᴅ:** `{user_id}`\n"
                    f"👥 **ɢʀᴏᴜᴘ:** `{message.chat.title}`\n"
                    f"⚠️ **ʀᴇᴀꜱᴏɴ:** ᴇxᴄᴇᴇᴅᴇᴅ ᴍᴀx ᴡᴀʀɴɪɴɢꜱ (3/3)\n"
                    f"🛠 **ꜱᴛᴀᴛᴜꜱ:** ᴍᴜᴛᴇᴅ ʙʏ ᴀɴᴛᴜ ᴀʙᴜꜱᴇ\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_photo(photo=WARN_IMG, caption=mute_text, reply_markup=get_main_buttons())
                warns_db[user_id] = 0
            else:
                w_msg = await message.reply_photo(photo=WARN_IMG, caption=alert_text, reply_markup=get_main_buttons())
                await asyncio.sleep(15) 
                await w_msg.delete()
        except: pass

# 6️⃣ OWNER COMMANDS
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 **ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ**\n━━━━━━━━━━━━━\n👤 **ᴜꜱᴇʀꜱ:** {len(users_db)}\n👥 **ɢʀᴏᴜᴘ|ꜱ:** {len(groups_db)}")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def owner_broadcast(client, message):
    if not message.reply_to_message: return
    sent = 0
    for user in list(users_db):
        try:
            await message.reply_to_message.copy(user); sent += 1
            await asyncio.sleep(0.3)
        except: pass
    await message.reply_text(f"✅ **ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴇɴᴛ ᴛᴏ {sent} ᴜꜱᴇʀꜱ.**")

print("🚀 Antu Abuse Bot (Stylish Edition) is Online!")
app.run()
