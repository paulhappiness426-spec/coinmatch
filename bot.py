import telebot, sqlite3, os

TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)
GAME_URL = "https://yourgame.onrender.com"

def db():
    conn = sqlite3.connect('game.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT, coins INTEGER DEFAULT 0, best_score INTEGER DEFAULT 0, level INTEGER DEFAULT 1, referred_by TEXT)')
    return conn

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.first_name
    parts = message.text.split()
    referred_by = parts[1] if len(parts) > 1 else None

    conn = db(); cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    is_new = cur.fetchone() is None

    if is_new:
        cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?)', (user_id, username, 100, 0, 1, referred_by))
        conn.commit()
        if referred_by and referred_by != user_id:
            try:
                cur.execute('UPDATE users SET coins = coins + 50 WHERE user_id=?', (referred_by,))
                conn.commit()
                bot.send_message(referred_by, f"🎉 Your friend {username} just joined!\n\n+50 coins added to you! 🪙\nYour balance is growing. Keep inviting!")
            except:
                pass
    conn.close()

    bot.send_message(message.chat.id,
        f"🍬 Welcome {username} to Candy Match!\n\n"
        f"🪙 You got +100 coins to start\n"
        f"🎮 Match candies, beat levels\n"
        f"👥 Invite friends = +50 coins each\n\n"
        f"Tap PLAY below to start!",
        reply_markup=telebot.types.InlineKeyboardMarkup([
            [telebot.types.InlineKeyboardButton("▶ Play Game", web_app=telebot.types.WebAppInfo(GAME_URL))],
            [telebot.types.InlineKeyboardButton("👥 Invite Friends", switch_inline_query=f"Join Candy Match!")]
        ])
    )

@bot.message_handler(commands=['coins', 'balance'])
def balance(message):
    conn = db()
    row = conn.execute('SELECT coins, level FROM users WHERE user_id=?', (str(message.from_user.id),)).fetchone()
    conn.close()
    if row:
        bot.send_message(message.chat.id, f"🪙 Your balance: {row[0]} coins\n⭐ Level: {row[1]}")
    else:
        bot.send_message(message.chat.id, "Play the game first to create your account!")

@bot.message_handler(commands=['invite'])
def invite(message):
    uid = str(message.from_user.id)
    bot.send_message(message.chat.id,
        f"👥 Your invite link:\nhttps://t.me/{bot.get_me().username}?start={uid}\n\nShare it! Each friend = +50 coins")

print("Bot is running...")
bot.infinity_polling()
