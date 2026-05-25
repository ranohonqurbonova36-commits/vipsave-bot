import telebot
import yt_dlp
import sqlite3
import os
import re

TOKEN = "8582825147:AAG5NHt2W8wIjZT3ze5s79gECeASm2-s0-o"
ADMIN_ID = 123456789

bot = telebot.TeleBot(TOKEN)

# ---------------- DB ----------------
conn = sqlite3.connect("vipsave.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    premium INTEGER DEFAULT 0
)
""")
conn.commit()

# ---------------- FOLDER ----------------
os.makedirs("downloads", exist_ok=True)

# ---------------- DB FUNCS ----------------
def add_user(uid):
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()

def add_coin(uid, amount):
    cur.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (amount, uid))
    conn.commit()

def set_premium(uid):
    cur.execute("UPDATE users SET premium = 1 WHERE user_id=?", (uid,))
    conn.commit()

def get_user(uid):
    cur.execute("SELECT coins, premium FROM users WHERE user_id=?", (uid,))
    return cur.fetchone()

# ---------------- DOWNLOAD ----------------
def download(url):
    opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(title).40s.%(ext)s",
        "merge_output_format": "mp4",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id)

    bot.send_message(
        message.chat.id,
        "🔥 VIPSAVE BOT 🔥\n\n"
        "📥 Link yuboring\n"
        "🎥 Video yuklaydi\n"
        "💰 Coin yig‘adi\n\n"
        "/balance - balans"
    )

# ---------------- BALANCE ----------------
@bot.message_handler(commands=['balance'])
def balance(message):
    add_user(message.chat.id)
    data = get_user(message.chat.id)

    bot.reply_to(message, f"💰 Coins: {data[0]} | 👑 Premium: {data[1]}")

# ---------------- MAIN ----------------
@bot.message_handler(func=lambda m: True)
def handle(message):
    url = message.text.strip()

    if not re.search(r'http', url):
        return

    add_user(message.chat.id)

    bot.reply_to(message, "⏳ Yuklanmoqda...")

    try:
        file = download(url)

        with open(file, "rb") as f:
            bot.send_video(message.chat.id, f)

        os.remove(file)

        add_coin(message.chat.id, 1)

        bot.send_message(message.chat.id, "💰 +1 coin")

    except:
        bot.reply_to(message, "❌ Yuklab bo‘lmadi")

# ---------------- ADMIN ----------------
@bot.message_handler(commands=['addcoins'])
def addcoins(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        uid = int(message.text.split()[1])
        amount = int(message.text.split()[2])

        add_coin(uid, amount)
        bot.reply_to(message, "💰 coins qo‘shildi")
    except:
        bot.reply_to(message, "❌ /addcoins id amount")

@bot.message_handler(commands=['addpremium'])
def premium(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        uid = int(message.text.split()[1])
        set_premium(uid)
        bot.reply_to(message, "👑 premium berildi")
    except:
        bot.reply_to(message, "❌ /addpremium id")

# ---------------- RUN ----------------
bot.infinity_polling()