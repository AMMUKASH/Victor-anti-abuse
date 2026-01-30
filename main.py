from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from config import API_ID, API_HASH, BOT_TOKEN, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_LINK, OWNER_ID
import asyncio

app = Client("AntiAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Aap yahan gande words add kar sakte hain
BAD_WORDS = ["gali1", "gali2", "abuse", "mc", "bc"] 
warns_db = {}

# Buttons Setup
REPLY_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📢 Updates", url=SUPPORT_CHANNEL),
        InlineKeyboardButton("👥 Support", url=SUPPORT_CHAT)
    ],
    [InlineKeyboardButton("👨‍💻 Owner", url=OWNER_LINK)]
])

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"👋 **Hello {message.from_user.mention}!**\n\n"
        "Main aapke group ko abuse se bachane ke liye ek professional **Anti-Abuse Bot** hoon.\n\n"
        "मुझे ग्रुप में एडमिन बनाएँ और 'Delete Messages' की परमिशन दें।",
        reply_markup=REPLY_MARKUP
    )

@app.on_message(filters.group & filters.text & ~filters.service)
async def filter_bad_words(client, message):
    # Admin aur Owner ko ignore karein
    user_id = message.from_user.id
    user_member = await client.get_chat_member(message.chat.id, user_id)
    
    if user_member.status in ("administrator", "creator") or user_id == OWNER_ID:
        return

    msg_text = message.text.lower()
    if any(word in msg_text for word in BAD_WORDS):
        try:
            await message.delete()
            
            warns_db[user_id] = warns_db.get(user_id, 0) + 1
            count = warns_db[user_id]
            
            if count >= 3:
                await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_text(
                    f"🚫 **Muted!**\n\n{message.from_user.mention} को 3 बार चेतावनी मिलने के बाद म्यूट कर दिया गया है।",
                    reply_markup=REPLY_MARKUP
                )
                warns_db[user_id] = 0
            else:
                warn_msg = await message.reply_text(
                    f"⚠️ **Warning ({count}/3)**\n\n{message.from_user.mention}, गाली देना मना है! अगली बार म्यूट कर दिया जाएगा।",
                    reply_markup=REPLY_MARKUP
                )
                await asyncio.sleep(10)
                await warn_msg.delete()
        except Exception as e:
            print(f"Error: {e}")

print("Bot is started successfully!")
app.run()
