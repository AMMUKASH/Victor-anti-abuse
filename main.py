from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from config import API_ID, API_HASH, BOT_TOKEN, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_LINK, OWNER_ID
import asyncio

app = Client("XenoAntiAbuseBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- Sabse Badi Abuse List ---
BAD_WORDS = [
    "mc", "bc", "mlc", "abc", "bsdk", "bhosadike", "bhosdike", "chutiya", "lodu", "gaandu", "gandu", 
    "saala", "sala", "kamine", "kamina", "harami", "haramzada", "bhadwa", "bhadwe", "bhadwi",
    "mkl", "bkl", "gl", "mc-bc", "pilla", "kutta", "suar", "pig", "madarchod", "maderchod", 
    "madrchod", "bhenchod", "behenchod", "randi", "randwa", "rondi", "tatte", "jhaat", 
    "lavda", "lawda", "lauda", "mutthal", "raand", "raandi", "betichod", "baapchod", 
    "bakchod", "bakchodi", "pichwada", "gaand", "gand", "chut", "chutiye", "chutiyapa", 
    "lund", "land", "lundfakir", "lode", "laude", "lawde", "pussy", "dick", "tits", 
    "boobs", "asshole", "bitch", "bastard", "fuck", "fucker", "fucking", "गाली", 
    "चूतिया", "लौडा", "लौड़े", "गाँडू", "भोसड़ीके", "मादरचोद", "बहनचोद", "बेंचो", "साला",
    "teri maa ki", "maa chuda", "behen chuda", "behen k lode", "bhen k lode", "gand mara", 
    "chudaap", "randaap", "randi rona"
]

# Warnings Store
warns_db = {}

# Professional Buttons
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
        "Main ek powerful **Anti-Abuse Bot** hoon jo aapke group ko gandi bhasha se saaf rakhta hai.\n\n"
        "🛡️ **Kaise use karein?**\n"
        "1. Mujhe group mein add karein.\n"
        "2. Admin banayein (Delete & Restrict permission).\n"
        "3. Bas, baki kaam mera hai!",
        reply_markup=REPLY_MARKUP
    )

@app.on_message(filters.group & filters.text & ~filters.service)
async def handle_abuse(client, message):
    # Admin/Owner check
    try:
        user_id = message.from_user.id
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status in ("administrator", "creator") or user_id == OWNER_ID:
            return
    except Exception:
        pass

    # Smart Filter: Spaces aur symbols hata kar check karna
    raw_text = message.text.lower()
    clean_text = raw_text.replace(" ", "").replace(".", "").replace("@", "a").replace("*", "")

    # Check if any bad word is in the message
    if any(word in raw_text or word in clean_text for word in BAD_WORDS):
        try:
            await message.delete()
            
            # Update Warnings
            warns_db[user_id] = warns_db.get(user_id, 0) + 1
            count = warns_db[user_id]

            if count >= 3:
                # 3 Warns = Mute
                await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions(can_send_messages=False))
                await message.reply_text(
                    f"🚫 **Action: Muted**\n\nUser: {message.from_user.mention}\nReason: 3/3 Warnings (Abuse)",
                    reply_markup=REPLY_MARKUP
                )
                warns_db[user_id] = 0
            else:
                # Warning Message
                warn_msg = await message.reply_text(
                    f"⚠️ **Warning ({count}/3)**\n\n{message.from_user.mention}, kripya gandi bhasha ka use na karein!",
                    reply_markup=REPLY_MARKUP
                )
                await asyncio.sleep(10)
                await warn_msg.delete()
        except Exception as e:
            print(f"Error: {e}")

print("✅ Anti-Abuse Bot is Started!")
app.run()
