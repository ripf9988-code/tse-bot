import logging
import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# --- Flask Server for Render Port Binding ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running perfectly!", 200

def run_flask():
    # Render-এর দেওয়া পোর্ট ব্যবহার করবে, না থাকলে ৮০৮০
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- মূল বট কনফিগারেশন ---
TOKEN = '8704198760:AAE9WUqLFDXRC-yYqg4mz5q_tZa-JwykrQg'
tz = pytz.timezone('Asia/Dhaka')

def check_market_result(pair, signal_time, direction):
    try:
        # পেয়ার নাম কনভার্ট
        ticker_symbol = "XAGUSD=X" if "SILVER" in pair.upper() else f"{pair}=X"
        ticker = yf.Ticker(ticker_symbol)
        
        # ১ মিনিটের ডাটা সংগ্রহ
        data = ticker.history(period="1d", interval="1m")
        
        if data.empty:
            return "ERROR"

        now = datetime.now(tz)
        target_time_obj = datetime.strptime(signal_time, "%H:%M").time()
        target_dt = tz.localize(datetime.combine(now.date(), target_time_obj))

        if target_dt > now:
            return "PENDING"

        data.index = data.index.tz_convert(tz)

        def get_candle_color(dt):
            dt_lookup = dt.replace(second=0, microsecond=0)
            if dt_lookup in data.index:
                row = data.loc[dt_lookup]
                return "GREEN" if row['Close'] > row['Open'] else "RED"
            return None

        expected_color = "GREEN" if direction.upper() == "CALL" else "RED"
        
        # ১. ডিরেক্ট ১ মিনিট চেক
        actual_color = get_candle_color(target_dt)
        if actual_color == expected_color:
            return "DIRECT_WIN"
        
        # ২. MTG (পরবর্তী ১ মিনিট) চেক
        mtg_dt = target_dt + timedelta(minutes=1)
        
        if mtg_dt > now:
            return "PENDING"
            
        mtg_color = get_candle_color(mtg_dt)
        if mtg_color == expected_color:
            return "MTG_WIN"
        else:
            return "LOSS"

    except Exception as e:
        print(f"Error logic: {e}")
        return "ERROR"

async def process_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if ';' not in user_text:
        return

    await update.message.reply_text("ফলাফল চেক করা হচ্ছে (১ মিনিট টাইমফ্রেম)...")
    
    lines = user_text.split('\n')
    result_list = []
    
    for line in lines:
        if ';' in line:
            parts = [p.strip() for p in line.split(';')]
            if len(parts) >= 3:
                pair, time_str, direction = parts[0], parts[1], parts[2]
                status = check_market_result(pair, time_str, direction)
                
                if status == "DIRECT_WIN":
                    result_list.append(f"{line} ✅")
                elif status == "MTG_WIN":
                    result_list.append(f"{line} ✅₁")
                elif status == "LOSS":
                    result_list.append(f"{line} ❌")
                elif status == "PENDING":
                    result_list.append(f"{line} 👀")
                else:
                    result_list.append(f"{line} ⚠️")

    final_message = "\n".join(result_list)
    await update.message.reply_text(f"📊 ফলাফল:\n\n{final_message}")

def main():
    # Flask সার্ভার আলাদা থ্রেডে চালানো
    Thread(target=run_flask).start()
    
    # টেলিগ্রাম বট স্টার্ট
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_list))
    
    print("Bot & Flask Server is running...")
    bot_app.run_polling()

if __name__ == '__main__':
    main()
