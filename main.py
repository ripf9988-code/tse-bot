import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# --- কনফিগারেশন ---
TOKEN = '8704198760:AAE9WUqLFDXRC-yYqg4mz5q_tZa-JwykrQg'

# টাইমজোন সেটআপ (বাংলাদেশ সময় অনুযায়ী)
tz = pytz.timezone('Asia/Dhaka')

def check_market_result(pair, signal_time, direction):
    try:
        # পেয়ার নাম কনভার্ট (যেমন: Silver -> XAGUSD=X)
        ticker_symbol = "XAGUSD=X" if "SILVER" in pair.upper() else f"{pair}=X"
        ticker = yf.Ticker(ticker_symbol)
        
        # ১ মিনিটের ডাটা সংগ্রহ (interval="1m")
        data = ticker.history(period="1d", interval="1m")
        
        if data.empty:
            return "ERROR"

        # সিগন্যাল টাইম প্রসেসিং
        now = datetime.now(tz)
        # ইউজারের দেওয়া সময়কে আজকের তারিখের সাথে যুক্ত করা
        target_time_obj = datetime.strptime(signal_time, "%H:%M").time()
        target_dt = tz.localize(datetime.combine(now.date(), target_time_obj))

        # সময় এখনও না হলে
        if target_dt > now:
            return "PENDING"

        # ডাটা ইনডেক্সকে লোকাল টাইমজোনে কনভার্ট
        data.index = data.index.tz_convert(tz)

        def get_candle_color(dt):
            # ১ মিনিটের উইন্ডো চেক করার জন্য ফ্লোর করা (যাতে সেকেন্ডের পার্থক্য না থাকে)
            dt_lookup = dt.replace(second=0, microsecond=0)
            if dt_lookup in data.index:
                row = data.loc[dt_lookup]
                # ক্লোজ প্রাইস ওপেন থেকে বেশি হলে গ্রিন, কম হলে রেড
                return "GREEN" if row['Close'] > row['Open'] else "RED"
            return None

        # ডিরেকশন অনুযায়ী প্রত্যাশিত কালার
        expected_color = "GREEN" if direction.upper() == "CALL" else "RED"
        
        # ১. ডিরেক্ট উইন চেক (প্রথম ১ মিনিট)
        actual_color = get_candle_color(target_dt)
        if actual_color == expected_color:
            return "DIRECT_WIN"
        
        # ২. MTG চেক (পরবর্তী ১ মিনিট - ১ মিনিটের ক্যান্ডেলের জন্য)
        mtg_dt = target_dt + timedelta(minutes=1) 
        
        # যদি MTG টাইম এখনও না আসে
        if mtg_dt > now:
            return "PENDING"
            
        mtg_color = get_candle_color(mtg_dt)
        
        if mtg_color == expected_color:
            return "MTG_WIN"
        else:
            return "LOSS"

    except Exception as e:
        print(f"Error: {e}")
        return "ERROR"

async def process_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if ';' not in user_text:
        return

    await update.message.reply_text("একটু অপেক্ষা করুন, ১ মিনিটের ক্যান্ডেল ডাটা চেক করা হচ্ছে...")
    
    lines = user_text.split('\n')
    result_list = []
    
    for line in lines:
        if ';' in line:
            parts = [p.strip() for p in line.split(';')]
            if len(parts) >= 3:
                pair, time_str, direction = parts[0], parts[1], parts[2]
                
                status = check_market_result(pair, time_str, direction)
                
                if status == "DIRECT_WIN":
                    result_list.append(f"{line} ✅ (Direct)")
                elif status == "MTG_WIN":
                    result_list.append(f"{line} ✅ (MTG-1)")
                elif status == "LOSS":
                    result_list.append(f"{line} ❌ (Loss)")
                elif status == "PENDING":
                    result_list.append(f"{line} 👀 (Wait)")
                else:
                    result_list.append(f"{line} ⚠️ (Error/No Data)")

    final_message = "\n".join(result_list)
    await update.message.reply_text(f"📊 ফলাফল (১ মিনিট ক্যান্ডেল):\n\n{final_message}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_list))
    print("1-Min Result Checker Bot is running...")
    app.run_polling()
