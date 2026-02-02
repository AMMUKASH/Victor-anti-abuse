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
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Antu Abuse Bot is Online!")

def run_dummy_server():
    try:
        server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer)
        server.serve_forever()
    except Exception as e:
        print(f"Server Error: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT SETUP ---
app = Client("AntuAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- CONFIGURATION ---
LOG_IMG = "https://graph.org/file/fcc36307f247bbfc623cd-e736a75b263077982a.jpg" 
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
HELP_IMG = "https://graph.org/file/41d3fd1a4182030eb519c-fd35dff2f1f579d076.jpg"
INFO_IMG = "https://graph.org/file/fcc36307f247bbfc623cd-e736a75b263077982a.jpg"

LOG_GROUP = -1003867805165  
warns_db = {} 

# 🔥 MASTER BANNED LIST (Added your full list)
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

async def is_admin(client, chat_id, user_id):
    if user_id == OWNER_ID: return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except: return False

# 1️⃣ START & HELP
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply_photo(photo=START_IMG, caption="🛡️ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**", reply_markup=get_main_buttons())

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    h_txt = (
        "🛡️ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ᴄᴏᴍᴍᴀɴᴅꜱ**\n\n"
        "• `/mute` | `/unmute` - Silence/Speak\n"
        "• `/ban` | `/unban` - Remove/Restore\n"
        "• `/info` - User Details"
    )
    await message.reply_photo(photo=HELP_IMG, caption=h_txt, reply_markup=get_main_buttons())

# 2️⃣ ADMIN ACTIONS (FULLY WORKING)
@app.on_message(filters.command(["mute", "ban", "unmute", "unban"]) & filters.group)
async def admin_actions(client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Aap admin nahi ho!")
    if not message.reply_to_message:
        return await message.reply_text("❌ User ke message par reply karein!")

    user = message.reply_to_message.from_user
    cmd = message.command[0]
    try:
        if cmd == "mute":
            await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
            act = "ᴍᴜᴛᴇᴅ 🚫"
        elif cmd == "ban":
            await client.ban_chat_member(message.chat.id, user.id)
            act = "ʙᴀɴɴᴇᴅ 🚷"
        elif cmd == "unmute" or cmd == "unban":
            await client.unban_chat_member(message.chat.id, user.id)
            await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions(
                can_send_messages=True, can_send_media_messages=True, 
                can_send_other_messages=True, can_add_web_page_previews=True
            ))
            act = "ʀᴇʟᴇᴀꜱᴇᴅ ✅"
            warns_db[user.id] = 0

        await message.reply_photo(
            photo=HELP_IMG, 
            caption=f"🛠 **ᴀᴅᴍɪɴ ᴀᴄᴛɪᴏɴ**\n━━━━━━━━━━━━━\n👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n👤 **ᴜꜱᴇʀ:** {user.mention}\n⚡ **ᴀᴄᴛɪᴏɴ:** {act}\n👮 **ᴀᴅᴍɪɴ:** {message.from_user.mention}",
            reply_markup=get_main_buttons()
        )
        
        log_txt = f"🛠 **#ᴀᴅᴍɪɴ_ᴀᴄᴛɪᴏɴ**\n━━━━━━━━━━━━━\n👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n👤 **ᴜꜱᴇʀ:** {user.mention}\n⚡ **ᴀᴄᴛɪᴏɴ:** {act}"
        await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# 3️⃣ CORE FILTER (AUTO-DELETE & LOGS)
@app.on_message(filters.group & (filters.text | filters.caption), group=-1)
async def main_filter(client, message):
    if not message.from_user or await is_admin(client, message.chat.id, message.from_user.id):
        return

    text = (message.text or message.caption or "").lower()
    is_link = re.search(r"(http|https)://|t\.me/", text)
    is_abuse = any(word in text for word in BANNED_WORDS)

    if is_abuse or is_link:
        user_id = message.from_user.id
        reason = "ᴀʙᴜꜱᴇ/ɢᴀᴀʟɪ" if is_abuse else "ʟɪɴᴋ/ꜱᴘᴀᴍ"
        warns_db[user_id] = warns_db.get(user_id, 0) + 1
        w = warns_db[user_id]
        
        try:
            await message.delete()
            log_txt = f"🚨 **#ᴀᴜᴛᴏ_ᴅᴇʟᴇᴛᴇ**\n━━━━━━━━━━━━━\n👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n👤 **ᴜꜱᴇʀ:** {message.from_user.mention}\n📝 **ʀᴇᴀꜱᴏɴ:** {reason}\n⚠️ **ᴡᴀʀɴꜱ:** {w}/3"
            await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)

            if w >= 3:
                await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_photo(photo=HELP_IMG, caption=f"🚫 **ᴜꜱᴇʀ ᴍᴜᴛᴇᴅ!**\n━━━━━━━━━━━━━\n👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n👤 **ᴜꜱᴇʀ:** {message.from_user.mention}\n📝 **ʀᴇᴀꜱᴏɴ:** 3/3 Warns exceeded.")
                warns_db[user_id] = 0
            else:
                bar = "🟥" * w + "⬜" * (3 - w)
                w_msg = await message.reply_photo(photo=HELP_IMG, caption=f"🛡️ **ᴀɴᴛɪ-ᴀʙᴜꜱᴇ**\n━━━━━━━━━━━━━\n👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n⚠️ **ʜᴇʏ** {message.from_user.mention},\n📵 **ɴᴏ {reason} ᴀʟʟᴏᴡᴇᴅ!**\n\n📊 **ᴘʀᴏɢʀᴇꜱꜱ:** {bar} ({w}/3)")
                await asyncio.sleep(12); await w_msg.delete()
        except: pass

print("🚀 Antu Abuse Bot (Full & Final) is Online!")
app.run()
