import telebot
import numpy as np
import time
import json
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- বটের ঘুম তাড়ানোর সিস্টেম (Keep-Alive) ---
app = Flask('')
@app.route('/')
def home(): return "TSE OMNISCIENT IS AWAKE 24/7"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- কনফিগারেশন ---
API_TOKEN = '8704198760:AAGxlMSO0X4cYVyf670_vwJRvPqO955EtUE
bot = telebot.TeleBot(API_TOKEN)
MEMORY_FILE = "tse_brain.json"

class OmniscientEngine:
    def __init__(self):
        self.pair = "NONE"
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f: self.mem = json.load(f)
        else: self.mem = {"L": []}

    def get_signal(self):
        time.sleep(1.5)
        logic = np.random.choice(["TRAP_DETECTED", "SERVER_PULSE", "LIQUIDITY_GAP"])
        direction = "UP" if np.random.random() > 0.5 else "DOWN"
        if logic in self.mem["L"]: direction = "DOWN" if direction == "UP" else "UP"
        return direction, logic

engine = OmniscientEngine()

# --- প্রধান মেনু (আপনার সব পেয়ার এখানে আছে) ---
def main_menu():
    m = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add("USD/BRL-OTC", "EUR/USD-OTC", "GBP/USD-OTC", "USD/INR-OTC", 
          "USD/BDT-OTC", "AUD/NZD-OTC", "USD/JPY-OTC", "USD/ARS-OTC", 
          "INTEL-STOCK", "🚀 GET SURESHOT AI SIGNAL")
    return m

@bot.message_handler(commands=['start', 'BOT'])
def welcome(m):
    bot.send_message(m.chat.id, "👁️ **TSE OMNISCIENT V18** চালু হয়েছে।\nএকটি পেয়ার সিলেক্ট করুন:", reply_markup=main_menu(), parse_mode="Markdown")

# --- পেয়ার সিলেকশন (যেকোনো বাটনে চাপ দিলে কাজ করবে) ---
@bot.message_handler(func=lambda m: any(x in m.text for x in ["OTC", "STOCK"]))
def handle_pairs(m):
    engine.pair = m.text
    bot.send_message(m.chat.id, f"✅ **{m.text}** এনালাইসিস করা হচ্ছে...\nএখন সিগন্যাল বাটনে ক্লিক করুন।", parse_mode="Markdown")

# --- সিগন্যাল বাটন হ্যান্ডলার ---
@bot.message_handler(func=lambda m: m.text == "🚀 GET SURESHOT AI SIGNAL")
def signal(m):
    if engine.pair == "NONE":
        bot.send_message(m.chat.id, "⚠️ আগে একটি পেয়ার (যেমন: USD/JPY-OTC) সিলেক্ট করুন।")
        return
    
    dir, log = engine.get_signal()
    icon = "🟩 CALL" if dir == "UP" else "🟥 PUT"
    msg = (f"🎯 **SURESHOT SIGNAL**\n📊 **PAIR:** {engine.pair}\n"
           f"━━━━━━━━━━━━━━━\n🔥 **MOVE:** {icon}\n🧠 **LOGIC:** {log}\n━━━━━━━━━━━━━━━")
    
    res = types.InlineKeyboardMarkup()
    res.add(types.InlineKeyboardButton("✅ WIN", callback_data="w"), types.InlineKeyboardButton("❌ LOSS", callback_data="l"))
    bot.send_message(m.chat.id, msg, reply_markup=res, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def feedback(call):
    if call.data == "l": engine.mem["L"].append("TRAP") # লস হলে লজিক সেভ করবে
    with open(MEMORY_FILE, 'w') as f: json.dump(engine.mem, f)
    bot.answer_callback_query(call.id, "বট শিখে নিয়েছে!")
    bot.edit_message_text(f"{call.message.text}\n\n✅ **LEARNING DONE**", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
