import re
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
UPPER_LIMIT = float(os.getenv("UPPER_LIMIT") or 15)
LOWER_LIMIT = float(os.getenv("LOWER_LIMIT") or 10)

# آخرین update_id خوانده شده
last_update_id = None

# تابع محاسبه حباب سکه
def calculate_bubble(coin_price, dollar_rate, ounce_price):
    pure_gold_grams = 8.133 * 0.9
    gold_per_gram_dollar = ounce_price / 31.1035
    gold_coin_value_toman = gold_per_gram_dollar * dollar_rate * pure_gold_grams
    bubble_percent = (coin_price / gold_coin_value_toman - 1) * 100
    return round(bubble_percent, 2)

# ارسال پیام در تلگرام
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

# تابع دریافت آخرین پیام حاوی سکه و اونس
def get_latest_coin_message():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1} if last_update_id else {}
    try:
        res = requests.get(url, params=params).json()
        updates = res.get("result", [])
        for update in updates:
            last_update_id = update["update_id"]
            msg = update.get("message", {})
            text = msg.get("text", "")
            if "سکه امامی" in text and "اونس طلا" in text:
                return text
        return None
    except Exception as e:
        print(f"خطا در دریافت پیام: {e}")
        return None

# پردازش پیام و ارسال حباب
def process_message(msg):
    try:
        coin_price = int(re.search(r"سکه امامی\s([\d,]+)", msg).group(1).replace(",", ""))
        dollar_rate = int(re.search(r"دلار آمریکا\s([\d,]+)", msg).group(1).replace(",", ""))
        ounce_price = float(re.search(r"انس طلا\s([\d,]+(?:\.\d+)?)", msg).group(1))
    except Exception:
        send_message("⚠️ خطا در تجزیه اطلاعات از پیام اخیر.")
        return

    bubble = calculate_bubble(coin_price, dollar_rate, ounce_price)

    base_text = (
        f"💰 <b>گزارش حباب سکه</b>\n\n"
        f"💵 دلار: {dollar_rate:,}\n"
        f"🌕 سکه امامی: {coin_price:,}\n"
        f"🏆 اونس طلا: {ounce_price}$\n\n"
        f"📊 <b>حباب فعلی:</b> {bubble}%"
    )

    if bubble > UPPER_LIMIT:
        alert = f"🚨 <b>هشدار!</b> حباب از حد بالا ({UPPER_LIMIT}%) عبور کرد!"
        send_message(base_text + "\n\n" + alert)
    elif bubble < LOWER_LIMIT:
        alert = f"⚠️ <b>هشدار!</b> حباب کمتر از حد پایین ({LOWER_LIMIT}%) شد!"
        send_message(base_text + "\n\n" + alert)
    else:
        send_message(base_text + "\n\n✅ در محدوده‌ی نرمال است.")

# حلقه اصلی
def main():
    print("🤖 بات شروع شد...")
    while True:
        msg = get_latest_coin_message()
        if msg:
            process_message(msg)
        time.sleep(3)  # هر ۳ ثانیه بررسی پیام‌های جدید

if __name__ == "__main__":
    main()
