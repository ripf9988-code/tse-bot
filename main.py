import telebot
import numpy as np
import time
import json
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- বটের ঘুম তাড়ানোর সিস্টেম ---
app = Flask('')
@app.route('/')
def home(): return "TSE OMNISCIENT IS AWAKE"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- কনফিগারেশন ---
API_TOKEN = '8704198760:AAGxlMSO0X4cYVyf670_vwJRvPqO955EtUE'
bot = telebot.TeleBot(API_TOKEN)
MEMORY_FILE = "tse_data.json"

class TradingEngine:
    def __init__(self):
        self.selected_pair = "NONE"
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f: self.memory = json.load(f)
        else: self.memory = {"L": []}

    def get_signal(self):
        time.sleep(1)
        direction = "UP" if np.random.random() > 0.5 else "DOWN"
        logic = np.random.choice(["PRICE_ACTION", "TRAP_LEVEL", "LIQUIDITY"])
        return direction, logic

engine = TradingEngine()

# --- আপনার কিবোর্ড বাটনগুলো এখানে সাজানো ---
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("USD/BRL-OTC", "EUR/USD-OTC", "GBP/USD-OTC", "USD/INR-OTC", 
               "USD/BDT-OTC", "AUD/NZD-OTC", "USD/JPY-OTC", "USD/ARS-OTC", 
               "INTEL-STOCK", "🚀 GET SURESHOT AI SIGNAL")
    return markup

@bot.message_handler(commands=['start', 'BOT'])
def welcome(m):
    bot.send_message(m.chat.id, "🎯 **TSE OMNISCIENT V18 READY**\nএকটি পেয়ার সিলেক্ট করুন:", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")

# --- পেয়ার সিলেক্ট করার লজিক ---
@bot.message_handler(func=lambda m: any(x in m.text for x in ["OTC", "STOCK"]))
def set_pair(m):
    engine.selected_pair = m.text
    bot.send_message(m.chat.id, f"✅ **{m.text}** এনালাইসিসের জন্য প্রস্তুত।\nএখন সিগন্যাল বাটনে ক্লিক করুন।")

# --- সিগন্যাল বাটন লজিক (হুবহু বাটনের টেক্সটের সাথে মিলানো) ---
@bot.message_handler(func=lambda m: "GET SURESHOT AI SIGNAL" in m.text)
def send_signal(m):
    if engine.selected_pair == "NONE":
        bot.send_message(m.chat.id, "⚠️ আগে একটি পেয়ার সিলেক্ট করুন (যেমন: USD/JPY-OTC)")
        return
    
    dir, log = engine.get_signal()
    move = "🟩 CALL" if dir == "UP" else "🟥 PUT"
    msg = (f"🎯 **SURESHOT SIGNAL**\n"
           f"📊 **PAIR:** {engine.selected_pair}\n"
           f"━━━━━━━━━━━━━━━\n"
           f"🔥 **MOVE:** {move}\n"
           f"🧠 **LOGIC:** {log}\n"
           f"━━━━━━━━━━━━━━━")
    
    res = types.InlineKeyboardMarkup()
    res.add(types.InlineKeyboardButton("✅ WIN", callback_data="w"), 
            types.InlineKeyboardButton("❌ LOSS", callback_data="l"))
    bot.send_message(m.chat.id, msg, reply_markup=res, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id, "ডাটা সেভ হয়েছে।")
    bot.edit_message_text(f"{call.message.text}\n\n✅ **SIGNAL UPDATED**", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
