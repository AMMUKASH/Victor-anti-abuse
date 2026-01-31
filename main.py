import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
LOG_GROUP = -1003867805165  # <--- Sahi ID Check kar lena

# 🔥 ABUSE LIST
BAD_WORDS = [
    "mc", "bc", "bsdk", "bhosadike", "chutiya", "lodu", "gandu", "madarchod", "bhenchod", 
    "randi", "lund", "lauda", "kutta", "pilla", "harami", "kamine", "bhadwa", "mkl", "bkl", 
    "gl", "sala", "saala", "betichod", "baapchod", "jhaat", "lavda", "mutthal", "raand", 
    "bakchodi", "pichwada", "gaand", "chut", "chutiye", "randaap", "randwa", "kaminey",
    "bitch", "fuck", "asshole", "dick", "pussy", "गाली", "साला", "हरामी", "मादरचोद"
]

# --- KEYBOARDS ---
START_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)],
    [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url=f"https://t.me/{(app.name if hasattr(app, 'name') else 'bot')}?startgroup=true")],
    [InlineKeyboardButton("🛠 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_back")]
])

# 1️⃣ START COMMAND + LOGS
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.chat.id not in users_db:
        users_db.add(message.chat.id)
        log_txt = (
            "👤 **#ɴᴇᴡ_ᴜꜱᴇʀ**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"**ɴᴀᴍᴇ:** {message.from_user.mention}\n"
            f"**ɪᴅ:** `{message.from_user.id}`\n"
            f"**ᴜꜱᴇʀ:** @{message.from_user.username if message.from_user.username else 'None'}"
        )
        await client.send_message(LOG_GROUP, log_txt)

    VIP_CAPTION = (
        "🛡️ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ xᴇɴᴏ ᴀɴᴛɪ-ᴀʙᴜꜱᴇ**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"ʜᴇʟʟᴏ {message.from_user.mention} ✨\n\n"
        "ᴍᴀɪɴ ᴀᴘᴋᴇ ɢʀᴏᴜᴘꜱ ᴋᴏ ɢᴀʟɪʏᴏɴ ᴀᴜʀ ꜱᴘᴀᴍ ꜱᴇ ʙᴀᴄʜᴀɴᴇ ᴋᴇ ʟɪʏᴇ ʙᴀɴᴀ ʜᴏᴏɴ. "
        "ᴍᴜᴊʜᴇ ᴀᴅᴍɪɴ ʙᴀɴᴀᴏ ᴀᴜʀ ʙᴇꜰɪᴋᴀʀ ʜᴏ ᴊᴀᴏ! 😎\n\n"
        "🚀 **ꜰᴇᴀᴛᴜʀᴇꜱ:**\n"
        "✨ ᴀᴜᴛᴏ ᴀʙᴜꜱᴇ ᴅᴇʟᴇᴛɪᴏɴ\n"
        "✨ ɪɴꜱᴛᴀɴᴛ ꜱᴘᴀᴍ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
        "✨ ᴜʟᴛʀᴀ-ꜰᴀꜱᴛ ꜱᴘᴇᴇᴅ"
    )

    await message.reply_photo(photo=START_IMG, caption=VIP_CAPTION, reply_markup=START_MARKUP)

# 2️⃣ STYLISH HELP MENU
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    HELP_TEXT = (
        "🛡️ **『 𝚇𝙴𝙽𝙾 𝚂𝚃𝚁𝙸𝙲𝚃 𝙱𝙾𝚃 𝙷𝙴𝙻𝙿 』**\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 **ᴜꜱᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ:**\n"
        "• `/start` - ʙᴏᴛ ᴋᴏ ᴊɪɴᴅᴀ ᴋᴀʀᴇɪɴ\n"
        "• `/help` - ʏᴇ ᴍᴇɴᴜ ᴅᴇᴋʜᴇɪɴ\n\n"
        "⚙️ **ᴀᴅᴍɪɴ ꜰᴇᴀᴛᴜʀᴇꜱ:**\n"
        "• `ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ` - ɢᴀʟɪ ᴅᴇᴛᴇᴄᴛ ʜᴏᴛᴇ ʜɪ ᴍꜱɢ ᴋʜᴀᴛᴀᴍ\n"
        "• `/ban` - ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ ᴜꜱᴇʀ ᴋᴏ ʙᴀɴ ᴋᴀʀᴇɪɴ\n\n"
        "👑 **ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ:**\n"
        "• `/broadcast` - ꜱᴀᴀʀᴇ ᴜꜱᴇʀꜱ ᴋᴏ ᴍꜱɢ ʙʜᴇᴊᴇɪɴ\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 **ᴛɪᴘ:** ʙᴏᴛ ᴋᴏ ɢʀᴏᴜᴘ ᴍᴇɪɴ ꜰᴜʟʟ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ ᴅᴇɪɴ!"
    )
    
    HELP_BUTTONS = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)],
        [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=OWNER_LINK)]
    ])

    await message.reply_text(text=HELP_TEXT, reply_markup=HELP_BUTTONS)

# 3️⃣ NEW GROUP LOG
@app.on_message(filters.new_chat_members)
async def welcome_and_log(client, message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            log_txt = (
                "👥 **#ᴀᴅᴅᴇᴅ_ᴛᴏ_ɴᴇᴡ_ɢʀᴏᴜᴘ**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"**ɢʀᴏᴜᴘ:** {message.chat.title}\n"
                f"**ɪᴅ:** `{message.chat.id}`\n"
                f"**ᴀᴅᴅᴇᴅ ʙʏ:** {message.from_user.mention if message.from_user else 'Unknown'}"
            )
            await client.send_message(LOG_GROUP, log_txt)
            await message.reply_text(f"✨ **ɴᴀᴍᴀꜱᴛᴇ!**\nᴍᴀɪɴ ᴀɢᴀʏᴀ {message.chat.title} ᴋᴏ ꜱᴀꜰᴇ ʀᴀᴋʜɴᴇ! 😎")

# 4️⃣ BROADCAST
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
    await ex.edit(f"✅ **ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ!**\nSent to {count} users.")

# 5️⃣ THE BEAST ABUSE FILTER
@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_abuse(client, message):
    users_db.add(message.chat.id)
    raw_text = message.text.lower()
    clean_text = "".join(e for e in raw_text if e.isalnum()) 

    if any(word in raw_text or word in clean_text for word in BAD_WORDS):
        try:
            await message.delete()
            log_text = (
                "🚨 **ᴀʙᴜꜱᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **ᴜꜱᴇʀ:** {message.from_user.mention}\n"
                f"🆔 **ɪᴅ:** `{message.from_user.id}`\n"
                f"👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n"
                f"💬 **ᴍꜱɢ:** `{message.text}`"
            )
            await client.send_message(LOG_GROUP, log_text)
            
            warn = await message.reply_text(f"⚠️ {message.from_user.mention}, **ɴᴏ ᴀʙᴜꜱᴇ!** ᴍꜱɢ ᴅᴇʟᴇᴛᴇᴅ.")
            await asyncio.sleep(4)
            await warn.delete()
        except: pass

print("🔥 Xeno Beast is Active with Stylish Menus!")
app.run()
