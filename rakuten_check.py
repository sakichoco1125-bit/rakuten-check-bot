import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

RETRY_COUNT = 3
RETRY_WAIT = 5  # 秒

def send_line(message_text):
    try:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=message_text)
        )
        print(f"LINE通知送信: {message_text}")
    except Exception as e:
        print(f"LINE通知失敗: {e}")

def check_stock():
    product_name = "Nintendo Switch 2"
    url = "https://books.rakuten.co.jp/rb/18210481/"

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            res = requests.get(url, timeout=20)
            res.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt == RETRY_COUNT:
                send_line(f"{product_name} の在庫情報取得失敗 → 通知スキップ ({e})")
                return
            import time
            time.sleep(RETRY_WAIT)

    soup = BeautifulSoup(res.text, "html.parser")
    status_tag = soup.find("span", class_="salesStatus")
    status_text = status_tag.text.strip() if status_tag else ""

    # 「ご注文できない商品」がなければ在庫あり
    if "ご注文できない商品" not in status_text:
        send_line(f"{product_name} 在庫あり！ {url}")
    else:
        print(f"{product_name} 在庫なし → 通知なし")

if __name__ == "__main__":
    check_stock()
