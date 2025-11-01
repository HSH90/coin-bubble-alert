import os
import re
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
UPPER_LIMIT = float(os.getenv("UPPER_LIMIT", 15))
LOWER_LIMIT = float(os.getenv("LOWER_LIMIT", 10))

def calculate_bubble(coin_price, dollar_rate, ounce_price):
    pure_gold_grams = 8.133 * 0.9
    gold_per_gram_dollar = ounce_price / 31.1035
    gold_coin_value_toman = gold_per_gram_dollar * dollar_rate * pure_gold_grams
    bubble_percent = (coin_price / gold_coin_value_toman - 1) * 100
    return round(bubble_percent, 2)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def get_last_channel_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    res = requests.get(url).json()
    messages = res.get("result", [])
    for msg in reversed(messages):
        text = msg.get("channel_post", {}).get("text", "")
        if "سکه امامی" in text and "اونس طلا" in text:
            return text
    return None

def process_message(msg):
    try:
        coin_price = int(re.search(r"سکه امامی\s([\d,]+)", msg).group(1).replace(",", ""))
        dollar_rate = int(re.search(r"دلار آمریکا\s([\d,]+)", msg).group(1).replace(",", ""))
        ounce_price = float(re.search(r"اونس طلا\s([\d,]+(?:\.\d+)?)", msg).group(1))
    except Exception as e:
        send_message(f"⚠️ خطا در تجزیه پیام کانال: {e}")
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
    elif bubble < LOWER_LIMIT:
        alert = f"⚠️ <b>هشدار!</b> حباب کمتر از حد پایین ({LOWER_LIMIT}%) شد!"
    else:
        alert = f"✅ در محدوده‌ی نرمال است."

    send_message(base_text + "\n\n" + alert)

def main():
    msg = get_last_channel_message()
    if msg:
        process_message(msg)
    else:
        send_message("⚠️ پیامی از کانال یافت نشد یا ساختار آن تغییر کرده است.")

if __name__ == "__main__":
    main()
