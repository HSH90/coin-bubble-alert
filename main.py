import re
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
UPPER_LIMIT = float(os.getenv("UPPER_LIMIT", 15))
LOWER_LIMIT = float(os.getenv("LOWER_LIMIT", 10))

# تابع برای گرفتن آخرین پیام از گروه (توسط ربات)
def get_latest_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url)
        data = res.json()

        if "result" not in data or not data["result"]:
            return None

        messages = data["result"]
        # جدیدترین پیام
        for msg in reversed(messages):
            if "message" in msg and "text" in msg["message"]:
                text = msg["message"]["text"]
                if "سکه امامی" in text and "اونس طلا" in text:
                    return text
        return None
    except Exception as e:
        print(f"خطا در دریافت پیام: {e}")
        return None


# تابع محاسبه حباب سکه
def calculate_bubble(coin_price, dollar_rate, ounce_price):
    # وزن طلای سکه امامی (8.133 گرم) و خلوص 0.9
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


# اجرای اصلی
def main():
    msg = get_latest_message()
    if not msg:
        send_message("⚠️ خطا در دریافت داده‌ها از گروه!")
        return

    # استخراج داده‌ها با regex
    try:
        coin_price = int(re.search(r"سکه امامی\s([\d,]+)", msg).group(1).replace(",", ""))
        dollar_rate = int(re.search(r"دلار آمریکا\s([\d,]+)", msg).group(1).replace(",", ""))
        ounce_price = float(re.search(r"انس طلا\s([\d,]+(?:\.\d+)?)", msg).group(1))
    except Exception:
        send_message("⚠️ خطا در تجزیه اطلاعات از پیام اخیر.")
        return

    bubble = calculate_bubble(coin_price, dollar_rate, ounce_price)

    # متن نهایی پیام
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


if __name__ == "__main__":
    main()
