import os
import asyncio
import threading
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_LINK

# --- RENDER PORT FIX (For 24/7 Hosting) ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Xeno Anti-Abuse is Online!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), RenderServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BOT SETUP ---
app = Client("XenoStrictBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# IMAGES
LOG_IMG = "https://graph.org/file/d362450dd7d5eb0f750a1-039a8d9258f7c6e681.jpg" 
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"

users_db = set(); warns_db = {} 
LOG_GROUP = -1003867805165  

# BANNED WORDS LIST
BANNED_WORDS = [
    "randi", "rand", "gandu", "madhrchod", "bhosdike", "lund", "louda", "loda",
    "chut", "gand", "gaand", "gnd", "bhnchod", "bahanchod", "bsdk", "mc", "bc",
    "randibaz", "randibaaz", "motherfucker", "motherchod", "motherchodo", 
    "chudai", "chud", "chudi", "chudata", "chudwa", "choda", "chodunga", 
    "chodungi", "chod", "bhosda", "bhosdi", "lowda", "lowde", "loude", "lode",
    "behen ko chod", "bhn ko chodke", "bahan ko chodke", "teri maa chodunga",
    "bahan ki chut", "behen ki lowdii", "teri behen ko chodu", "teri amaa ka bhosraa",
    "kutta", "pilla", "harami", "kamine", "bhadwa", "mkl", "bkl", "gl", "sala", 
    "saala", "betichod", "baapchod", "jhaat", "lavda", "mutthal", "raand", 
    "bakchodi", "pichwada", "randaap", "randwa", "kaminey", "bitch", "asshole", "dick",
    "porn", "xxx", "sexy", "fuck", "pussy", "rape", "drugs", "dm karo"
]

# --- REUSABLE BUTTONS ---
def get_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)],
        [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url=f"https://t.me/XenoStrictBot?startgroup=true")],
        [InlineKeyboardButton("🛠 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_menu")]
    ])

# 1️⃣ START & HELP COMMANDS
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.chat.id not in users_db:
        users_db.add(message.chat.id)
        try: await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=f"👤 **#ɴᴇᴡ_ᴜꜱᴇʀ**\n**ɴᴀᴍᴇ:** {message.from_user.mention}\n**ɪᴅ:** `{message.from_user.id}`")
        except: pass
    await message.reply_photo(photo=START_IMG, caption="🛡️ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ xᴇɴᴏ ᴀɴᴛɪ-ᴀʙᴜꜱᴇ**\n\nMain aapke groups ko gaaliyon aur links se bachaunga. Bas mujhe admin banayein!", reply_markup=get_main_buttons())

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text("🛠 **xᴇɴᴏ ꜱᴛʀɪᴄᴛ ʜᴇʟᴘ ᴍᴇɴᴜ**", reply_markup=get_main_buttons())

# 2️⃣ CALLBACK HANDLERS (Help Menu)
@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client, callback_query):
    help_text = (
        "🛡️ **ꜰᴇᴀᴛᴜʀᴇꜱ & ᴄᴏᴍᴍᴀɴᴅꜱ:**\n\n"
        "🚀 **User Commands:**\n"
        "• `/start` - Bot chalu karein\n"
        "• `/help` - Ye menu dekhein\n\n"
        "⚙️ **Admin Features:**\n"
        "• **Anti-Abuse:** Bad words delete karega.\n"
        "• **Anti-Link:** Saare links block karega.\n"
        "• **Warn System:** 3 warns = Auto Mute.\n\n"
        "👑 **Owner Only:**\n"
        "• `/broadcast` - Sabhi users ko msg bhejein."
    )
    await callback_query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back_start")]]))

@app.on_callback_query(filters.regex("back_start"))
async def back_callback(client, callback_query):
    await callback_query.edit_message_text("🛡️ **xᴇɴᴏ ᴀɴᴛɪ-ᴀʙᴜꜱᴇ ᴍᴇɴᴜ**", reply_markup=get_main_buttons())

# 3️⃣ ANTI-ABUSE + ANTI-LINK + WARN LOGIC
@app.on_message(filters.group & (filters.text | filters.caption) & ~filters.service)
async def filter_logic(client, message):
    if not message.from_user: return
    
    # Bypass Admins/Owner
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] or message.from_user.id == OWNER_ID:
            return
    except: pass

    raw_text = (message.text or message.caption or "").lower()
    clean_text = "".join(e for e in raw_text if e.isalnum()) 
    
    is_link = re.search(r"(http|https)://|t\.me/|[a-z0-9]+\.[a-z]{2,}", raw_text)
    is_abuse = any(re.search(rf"\b{re.escape(word)}\b", raw_text) or word in clean_text for word in BANNED_WORDS)

    if is_abuse or is_link:
        user_id = message.from_user.id
        reason = "Abuse" if is_abuse else "Link"
        warns_db[user_id] = warns_db.get(user_id, 0) + 1
        curr_warns = warns_db[user_id]

        try:
            # LOG TO LOG GROUP
            log_txt = (
                f"🚨 **{reason.upper()} ᴅᴇᴛᴇᴄᴛᴇᴅ**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **ᴜꜱᴇʀ:** {message.from_user.mention}\n"
                f"👥 **ɢʀᴏᴜᴘ:** {message.chat.title}\n"
                f"⚠️ **ᴡᴀʀɴ:** {curr_warns}/3\n"
                f"💬 **ᴍꜱɢ:** `{raw_text[:100]}`"
            )
            await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=log_txt)
            
            await message.delete()
            
            if curr_warns >= 3:
                await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
                warns_db[user_id] = 0
                await message.reply_text(f"🚫 {message.from_user.mention} **ᴍᴜᴛᴇᴅ!** (3rd Warning)", reply_markup=get_main_buttons())
            else:
                w_msg = await message.reply_text(f"⚠️ {message.from_user.mention}, **ɴᴏ {reason.upper()}!** ({curr_warns}/3)", reply_markup=get_main_buttons())
                await asyncio.sleep(8); await w_msg.delete()
        except: pass

# 4️⃣ OWNER BROADCAST
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to a message to broadcast!")
    
    sent = 0
    msg = await message.reply_text("🚀 Broadcasting...")
    for user in list(users_db):
        try:
            await message.reply_to_message.copy(user)
            sent += 1
            await asyncio.sleep(0.3)
        except: pass
    await msg.edit(f"✅ **Broadcast Done!** Sent to {sent} users.")

print("🔥 Xeno Strict Bot is Fully Active!")
app.run()
