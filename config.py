import os

# --- Bot Credentials ---
API_ID = int(os.getenv("API_ID", "34135757")) 
API_HASH = os.getenv("API_HASH", "d3d5548fe0d98eb1fb793c2c37c9e5c8")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8508791428:AAEVP8eN8H4yE1AVwSs15KpNV3TamY4hXB8")

# --- Database Setup ---
# Naye cluster link ke saath updated password
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://misssqn:VICTOR01@cluster0.3otqmso.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# --- Community & Identity ---
OWNER_ID = int(os.getenv("OWNER_ID", "8482447535"))
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1003867805165"))
OWNER_LINK = os.getenv("OWNER_LINK", "https://t.me/XenoEmpir")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/radhesupport")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/+PKYLDIEYiTljMzMx")
