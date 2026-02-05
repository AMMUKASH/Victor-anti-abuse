import os
import asyncio
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, InputMediaPhoto
from pyrogram.enums import ChatMemberStatus, ChatType
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT, SUPPORT_CHANNEL, MONGO_URL

# --- DATABASE SETUP ---
mongo = MongoClient(MONGO_URL)
db = mongo.AntuAbuseBot
users_db = db.users
groups_db = db.groups
warns_db = db.warns
settings_db = db.settings

# --- BOT SETUP ---
app = Client("AntuAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- CONFIGURATION (Images) ---
LOG_IMG = "https://graph.org/file/fcc36307f247bbfc623cd-e736a75b263077982a.jpg" 
START_IMG = "https://graph.org/file/735dcfd2ce185f9973958-ae4e93ef6832223ada.jpg"
HELP_IMG = "https://graph.org/file/41d3fd1a4182030eb519c-fd35dff2f1f579d076.jpg"
WARN_IMG = "https://graph.org/file/41d3fd1a4182030eb519c-fd35dff2f1f579d076.jpg"
WELCOME_IMG = "https://graph.org/file/dd6f52b9da84901f05cea-57225089b205ccf939.jpg"

LOG_GROUP = -1003867805165  
URL_PATTERN = r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+)"

# 🔥 MASTER BANNED LIST
BANNED_WORDS = [
    "randi ke bache", "randi ka bacha", "gandu", "maiya rand", "madhrchod", "bhosdike", "lund", "louda", "loda", "chut", "gand",
    "mc", "bc", "bsdk", "sex", "porn", "xxx", "join my bio", "bio link", "check my bio", "whatsapp"
]

def get_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url=SUPPORT_CHANNEL), InlineKeyboardButton("👥 ꜱᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)],
        [InlineKeyboardButton("✨ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ✨", url="https://t.me/AntuAbusebot?startgroup=true")]
    ])

# --- HELPER: BIO SCANNER ---
async def has_link_in_bio(client, user_id):
    try:
        user = await client.get_users(user_id)
        bio = user.bio.lower() if user.bio else ""
        if re.search(URL_PATTERN, bio) or any(x in bio for x in ["t.me/", "bio link", "check bio"]):
            return True
    except: pass
    return False

# 1️⃣ START COMMAND
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    if message.chat.type == ChatType.PRIVATE:
        if not users_db.find_one({"user_id": message.from_user.id}):
            users_db.insert_one({"user_id": message.from_user.id})
            await client.send_photo(LOG_GROUP, photo=LOG_IMG, caption=f"👤 #NewUser: {message.from_user.mention}")
    
    start_text = f"👋 **ʜᴇʟʟᴏ {message.from_user.mention},**\n\nɪ ᴀᴍ **ᴀɴᴛᴜ ᴀʙᴜꜱᴇ ʙᴏᴛ**.\nɪ ᴡɪʟʟ ᴋᴇᴇᴘ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴄʟᴇᴀɴ ꜰʀᴏᴍ ᴀʙᴜꜱᴇ & ʟɪɴᴋꜱ!"
    btn = get_main_buttons()
    btn.inline_keyboard.append([InlineKeyboardButton("🛠 ʜᴇʟᴘ", callback_data="help_menu")])
    await message.reply_photo(photo=START_IMG, caption=start_text, reply_markup=btn)

# 2️⃣ WELCOME SYSTEM
@app.on_message(filters.new_chat_members)
async def welcome_handler(client, message):
    config = settings_db.find_one({"chat_id": message.chat.id}) or {"welcome": True}
    if config.get("welcome"):
        for member in message.new_chat_members:
            await message.reply_photo(photo=WELCOME_IMG, caption=f"✨ **ᴡᴇʟᴄᴏᴍᴇ** {member.mention}!")

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_toggle(client, message):
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text("❌ Admins only!")
    
    state = message.command[1].lower() if len(message.command) > 1 else "on"
    settings_db.update_one({"chat_id": message.chat.id}, {"$set": {"welcome": (state == "on")}}, upsert=True)
    await message.reply_text(f"✅ Welcome set to **{state.upper()}**")

# 3️⃣ CORE FILTER (Abuse + Link + Bio)
@app.on_message(filters.group & ~filters.command(["start", "help"]), group=-1)
async def main_filter(client, message):
    if not message.from_user: return
    
    # Skip Admins
    try:
        user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]: return
    except: return

    text = (message.text or message.caption or "").lower()
    user_id = message.from_user.id
    violation = None

    if any(word in text for word in BANNED_WORDS): violation = "Abusive Words"
    elif re.search(URL_PATTERN, text): violation = "Links/Ads"
    elif await has_link_in_bio(client, user_id): violation = "Link in Bio"

    if violation:
        warn_data = warns_db.find_one({"user_id": user_id, "chat_id": message.chat.id})
        count = (warn_data["count"] if warn_data else 0) + 1
        
        try:
            await message.delete()
            if count >= 3:
                await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_photo(photo=WARN_IMG, caption=f"🚫 **ᴍᴜᴛᴇᴅ!**\n**User:** {message.from_user.mention}\n**Reason:** {violation} (3/3)")
                warns_db.delete_one({"user_id": user_id, "chat_id": message.chat.id})
            else:
                warns_db.update_one({"user_id": user_id, "chat_id": message.chat.id}, {"$set": {"count": count}}, upsert=True)
                w_msg = await message.reply_text(f"⚠️ **ᴡᴀʀɴɪɴɢ {count}/3**\n{message.from_user.mention}, {violation} is not allowed!")
                await asyncio.sleep(5); await w_msg.delete()
        except: pass

# 4️⃣ OWNER COMMANDS
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 **STATS:**\nUsers: {users_db.count_documents({})}\nGroups: {groups_db.count_documents({})}")

@app.on_callback_query(filters.regex("help_menu"))
async def help_menu_cb(client, cb):
    help_msg = "🛠 **Commands:**\n• /welcome on/off\n• Anti-Abuse (Auto)\n• Anti-Link (Auto)\n• Bio-Scan (Auto)"
    await cb.message.edit_caption(help_msg, reply_markup=get_main_buttons())

# --- RUN BOT ---
print("Bot Started Successfully!")
app.run()
