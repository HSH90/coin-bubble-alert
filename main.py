import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
UPPER_LIMIT = float(os.getenv("UPPER_LIMIT") or 15)
LOWER_LIMIT = float(os.getenv("LOWER_LIMIT") or 10)

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

def fetch_data():
    # Replace with real scraping or API call later
    coin_price = 110_600_000
    dollar_rate = 106_750
    ounce_price = 4008
    return coin_price, dollar_rate, ounce_price

def main():
    coin_price, dollar_rate, ounce_price = fetch_data()
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

if __name__ == "__main__":
    main()
