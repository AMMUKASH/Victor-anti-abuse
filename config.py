import os

# --- Bot Credentials ---
API_ID = int(os.getenv("API_ID", "34135757")) 
API_HASH = os.getenv("API_HASH", "d3d5548fe0d98eb1fb793c2c37c9e5c8")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8508791428:AAEVP8eN8H4yE1AVwSs15KpNV3TamY4hXB8")

# --- Database Setup ---
# Password 'VICTOR01' ke sath Mongo URL
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://Victor:VICTOR01@cluster0.mongodb.net/?retryWrites=true&w=majority")

# --- Community & Identity ---
OWNER_ID = int(os.getenv("OWNER_ID", "8482447535"))
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1003867805165"))
OWNER_LINK = os.getenv("OWNER_LINK", "https://t.me/XenoEmpir")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/radhesupport")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/+PKYLDIEYiTljMzMx")
