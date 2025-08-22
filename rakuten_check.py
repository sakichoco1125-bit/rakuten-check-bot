import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
import time

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

RETRY_COUNT = 3
RETRY_WAIT = 5  # 秒
STATUS_FILE = "stock_status.txt"
NOTIFY_COOLDOWN = 3600  # 1時間以内の重複通知を防ぐ

def send_line(message_text):
    try:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=message_text)
        )
        print(f"LINE通知送信: {message_text}")
    except Exception as e:
        print(f"LINE通知失敗: {e}")

def get_last_status():
    """前回の在庫状態と通知時刻を取得"""
    try:
        with open(STATUS_FILE, "r") as f:
            line = f.read().strip()
            status, ts = line.split(",")
            return status == "1", float(ts)
    except FileNotFoundError:
        return False, 0  # 初回は在庫なし、通知なし
    except Exception:
        return False, 0

def save_status(stock_status):
    """在庫状態と現在時刻を保存"""
    with open(STATUS_FILE, "w") as f:
        f.write(f"{'1' if stock_status else '0'},{time.time()}")

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
            time.sleep(RETRY_WAIT)

    soup = BeautifulSoup(res.text, "html.parser")
    status_tag = soup.find("span", class_="salesStatus")
    status_text = status_tag.text.strip() if status_tag else ""

    # 「ご注文できない商品」だけで判定
    current_stock_status = not ("ご注文できない商品" in status_text)

    last_stock_status, last_notify_time = get_last_status()

    # 在庫復活 & 前回通知から一定時間経過している場合のみ通知
    now = time.time()
    if not last_stock_status and current_stock_status:
        if now - last_notify_time > NOTIFY_COOLDOWN:
            send_line(f"{product_name} 在庫復活！ {url}")
            save_status(current_stock_status)
        else:
            print(f"{product_name} 在庫復活だけど通知抑制中")
    else:
        print(f"{product_name} 在庫状態変化なし → 通知なし")
        save_status(current_stock_status)

if __name__ == "__main__":
    check_stock()
