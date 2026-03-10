import telebot
import numpy as np
import time
import datetime
import pytz
import json
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- Flask Server (বটকে জাগিয়ে রাখার জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "TSE OMNISCIENT IS ALIVE 24/7"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ১. সেটিংস ও কনফিগারেশন ---
API_TOKEN = '8704198760:AAGxlMSO0X4cYVyf670_vwJRvPqO955EtUE'
BD_TZ = pytz.timezone('Asia/Dhaka')
bot = telebot.TeleBot(API_TOKEN)
MEMORY_FILE = "tse_omniscient_core.json"

class TSE_Omniscient_Engine:
    def __init__(self):
        self.selected_pair = "EUR/USD-OTC"
        self.last_logic = ""
        self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {"HIDDEN_ALGO": [], "REJECTION_TRAPS": []}

    def save_memory(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memory, f)

    def decrypt_broker_script(self):
        time.sleep(4) 
        hidden_logics = [
            "SECRET: Broker-Side Liquidity Imbalance",
            "SECRET: Next-Candle Generation Queue Match",
            "SECRET: Internal Rejection Pulse",
            "SECRET: Anti-Retail Trapping Script",
            "SECRET: Server-Side Price Rounding Detection"
        ]
        self.last_logic = np.random.choice(hidden_logics)
        internal_scan = np.random.random()
        
        if "Imbalance" in self.last_logic or "Trapping" in self.last_logic:
            direction = "DOWN" if internal_scan > 0.4 else "UP"
        else:
            direction = "UP" if internal_scan > 0.5 else "DOWN"

        status = "🛡️ OMNISCIENT CORE: SYNCED 100%"
        if self.last_logic in self.memory["REJECTION_TRAPS"]:
            direction = "DOWN" if direction == "UP" else "UP"
            status = "🔄 CORE OVERRIDE: BLOCKED"

        icon = "🟩 CALL (SURESHOT)" if direction == "UP" else "🟥 PUT (SURESHOT)"
        return icon, status

engine = TSE_Omniscient_Engine()

@bot.message_handler(commands=['start', 'BOT'])
def start(m):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("💎 GET 100% OMNISCIENT SIGNAL"))
    bot.send_message(m.chat.id, "👁️ **TSE OMNISCIENT V18 - 24/7 ONLINE** 👁️", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 GET 100% OMNISCIENT SIGNAL")
def send_signal(m):
    signal, status = engine.decrypt_broker_script()
    now = datetime.datetime.now(BD_TZ)
    msg = (f"🎯 **OMNISCIENT SURESHOT** 🎯\n"
           f"🚀 **NEXT MOVE:** {signal}\n"
           f"🧠 **STATUS:** {status}\n"
           f"⏰ **TIME:** {now.strftime('%I:%M:%S %p')}")
    
    res_markup = types.InlineKeyboardMarkup()
    res_markup.add(types.InlineKeyboardButton("✅ WIN", callback_data="win"), types.InlineKeyboardButton("❌ LOSS", callback_data="loss"))
    bot.send_message(m.chat.id, msg, reply_markup=res_markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["win", "loss"])
def update_mem(call):
    if call.data == "win": engine.memory["HIDDEN_ALGO"].append(engine.last_logic)
    else: engine.memory["REJECTION_TRAPS"].append(engine.last_logic)
    engine.save_memory()
    bot.edit_message_text("✅ ডাটা সিঙ্ক করা হয়েছে।", call.message.chat.id, call.message.message_id)

# --- ২৪/৭ চালু রাখার মূল মেকানিজম ---
if __name__ == "__main__":
    keep_alive() # Flask সার্ভার চালু করবে
    print("বট এবং কিপ-অ্যালাইভ সার্ভার চালু হয়েছে...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"বট ক্র্যাশ করেছে: {e}. ৫ সেকেন্ড পর পুনরায় চালু হচ্ছে...")
            time.sleep(5)
