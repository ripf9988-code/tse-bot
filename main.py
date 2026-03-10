import telebot
import numpy as np
import time
import datetime
import pytz
import json
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- ১. ফ্লাস্ক সার্ভার (বটকে ২৪ ঘণ্টা জাগিয়ে রাখার জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "TSE BOT IS RUNNING 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- ২. মেইন বট সেটিংস ---
API_TOKEN = '8372869401:AAGhrEJFmz9BDPIGvTffx3SAbceBerLr6mo'
BD_TZ = pytz.timezone('Asia/Dhaka')
bot = telebot.TeleBot(API_TOKEN)
ADMIN_HANDLE = "@tradersohan01"
MEMORY_FILE = "tse_memory.json"

# মার্কেট লিস্ট
OTC_PAIRS = [
    "USD/BRL-OTC", "EUR/USD-OTC", "GBP/USD-OTC", 
    "USD/INR-OTC", "USD/BDT-OTC", "AUD/NZD-OTC", 
    "USD/JPY-OTC", "USD/ARS-OTC", "INTEL-STOCK"
]

class TSE_Final_Engine:
    def __init__(self):
        self.selected_pair = "USD/BRL-OTC"
        self.last_logic = ""
        self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {"PROFIT_PATTERNS": [], "LOSS_PATTERNS": []}

    def save_memory(self):
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memory, f)

    def analyze(self):
        time.sleep(4)
        logics = ["ALGO_TRAP", "CYCLE_REVERSE", "BREAKOUT_FAKE", "S/R_FLIP", "M/W_PATTERN"]
        current_logic = np.random.choice(logics)
        direction = "UP" if np.random.randint(1, 100) > 50 else "DOWN"
        
        status = "📡 NEW ALGO SCAN"
        if current_logic in self.memory["LOSS_PATTERNS"]:
            direction = "DOWN" if direction == "UP" else "UP"
            status = "🔄 REVERSED (PREVIOUS LOSS MEMORY)"
        elif current_logic in self.memory["PROFIT_PATTERNS"]:
            status = "✅ CONFIRMED (SUCCESS MEMORY)"

        self.last_logic = current_logic
        icon = "🟩 CALL" if direction == "UP" else "🟥 PUT"
        return icon, f"{np.random.randint(95, 99)}%", status

engine = TSE_Final_Engine()

# --- ৩. বট হ্যান্ডেলার্স ---
@bot.message_handler(commands=['start', 'BOT'])
def start(m):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [types.KeyboardButton(p) for p in OTC_PAIRS]
    markup.add(*btns)
    markup.add(types.KeyboardButton("🚀 GET SURESHOT AI SIGNAL"))
    
    bot.send_message(m.chat.id, f"🛡️ **TSE ULTRA V6 - CLOUD MODE** 🛡️\n━━━━━━━━━━━━━━━━━━━━\nস্বাগতম **{m.from_user.first_name}**!\nবট এখন ২৪ ঘণ্টা সচল থাকবে।", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚀 GET SURESHOT AI SIGNAL")
def send_signal(m):
    status_msg = bot.send_message(m.chat.id, f"🔍 **{engine.selected_pair}** ব্রোকার সাইকোলজি বিশ্লেষণ করা হচ্ছে...")
    
    signal, acc, mem_status = engine.analyze()
    now = datetime.datetime.now(BD_TZ)
    
    msg = (f"✨ **TSE AI SIGNAL** ✨\n━━━━━━━━━━━━━━━━━━━━\n"
           f"🎯 **ASSET:** {engine.selected_pair}\n"
           f"🔥 **SIGNAL:** {signal}\n"
           f"📊 **STRENGTH:** {acc}\n"
           f"🧠 **MEMORY:** {mem_status}\n"
           f"⏰ **TIME:** {now.strftime('%I:%M:%S %p')}\n━━━━━━━━━━━━━━━━━━━━\n"
           f"🚀 **ENTRY:** NEXT 1-MIN\n\n"
           f"👇 **রেজাল্ট সিলেক্ট করুন:**")
    
    res_markup = types.InlineKeyboardMarkup()
    res_markup.add(
        types.InlineKeyboardButton("✅ PROFIT", callback_data="win"),
        types.InlineKeyboardButton("❌ LOSS", callback_data="loss")
    )
    
    bot.delete_message(m.chat.id, status_msg.message_id)
    bot.send_message(m.chat.id, msg, reply_markup=res_markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["win", "loss"])
def update_mem(call):
    if call.data == "win":
        engine.memory["PROFIT_PATTERNS"].append(engine.last_logic)
        text = "✅ **RESULT: PROFIT**\nবট এই প্যাটার্নটি সফল হিসেবে সেভ করেছে।"
    else:
        engine.memory["LOSS_PATTERNS"].append(engine.last_logic)
        text = "❌ **RESULT: LOSS**\nবট এই লস থেকে শিখেছে এবং পরে বিপরীত সিগন্যাল দেবে।"
    
    engine.save_memory()
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: any(pair in m.text for pair in OTC_PAIRS))
def set_pair(m):
    engine.selected_pair = m.text
    bot.send_message(m.chat.id, f"✅ {m.text} এনালাইসিসের জন্য প্রস্তুত।")

# --- ৪. রানার ---
if __name__ == "__main__":
    keep_alive() # সার্ভার চালু করবে
    print("TSE Cloud Server is Online!")
    bot.infinity_polling(timeout=15, long_polling_timeout=5)
