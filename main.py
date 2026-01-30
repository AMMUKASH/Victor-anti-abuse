from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from config import API_ID, API_HASH, BOT_TOKEN, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_USERNAME
import asyncio

app = Client("AntiAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Galiyon ki list
BAD_WORDS = ["gali1", "gali2", "abuse", "ganda_word"] 

# Warnings count ke liye database
warns_db = {}

# Common Buttons
REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📢 Channel", url=SUPPORT_CHANNEL),
        InlineKeyboardButton("👥 Support Group", url=SUPPORT_CHAT)
    ],
    [InlineKeyboardButton("👤 Owner", url=f"https://t.me/{OWNER_USERNAME}")]
])

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        f"Hello {message.from_user.mention}!\n\nMain ek **Anti-Abuse Bot** hoon. Mujhe apne group mein admin banayein aur main wahan galiyan delete karke users ko mute karunga.",
        reply_markup=REPLY_MARKUP
    )

@app.on_message(filters.group & filters.text & ~filters.service)
async def filter_bad_words(client, message):
    # Admin ko ignore karne ke liye logic
    user = await client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status in ("administrator", "creator"):
        return

    msg_text = message.text.lower()
    if any(word in msg_text for word in BAD_WORDS):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        await message.delete() # Gali delete karein

        warns_db[user_id] = warns_db.get(user_id, 0) + 1
        count = warns_db[user_id]
        
        if count >= 3:
            try:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_text(
                    f"🚫 {message.from_user.mention} ko 3 baar gali dene par **Mute** kar diya gaya hai.",
                    reply_markup=REPLY_MARKUP
                )
                warns_db[user_id] = 0
            except Exception as e:
                print(f"Error: {e}")
        else:
            warn_msg = await message.reply_text(
                f"⚠️ {message.from_user.mention}, gali mat do! (Warning: {count}/3)",
                reply_markup=REPLY_MARKUP
            )
            await asyncio.sleep(8)
            await warn_msg.delete()

print("Bot Start Ho Gaya Hai!")
app.run()
