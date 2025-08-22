import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
import time

# 環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# リトライ回数と待機秒数
RETRY_COUNT = 3
RETRY_WAIT = 5  # 秒

# 前回の在庫状態を保存するファイル
STOCK_FILE = "stock_status.txt"

def send_line(message_text):
    try:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text=message_text)
        )
        print(f"LINE通知送信: {message_text}")
    except Exception as e:
        print(f"LINE通知失敗: {e}")

def get_last_stock_status():
    try:
        with open(STOCK_FILE, "r") as f:
            return f.read().strip() == "1"
    except FileNotFoundError:
        return False  # 初回は在庫なし扱い

def save_current_stock_status(status):
    with open(STOCK_FILE, "w") as f:
        f.write("1" if status else "0")

def check_stock():
    product_name = "Nintendo Switch 2"
    url = "https://books.rakuten.co.jp/rb/18210481/"

    # 在庫情報取得
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

    # 在庫判定（statusがNoneの場合も在庫なし扱い）
    status_text = status_tag.text.strip() if status_tag else ""
    if any(keyword in status_text for keyword in ["ご注文できません", "在庫なし"]):
        current_stock_status = False
    else:
        current_stock_status = True

    last_stock_status = get_last_stock_status()

    # 前回在庫なし → 今回在庫あり の場合のみ通知
    if not last_stock_status and current_stock_status:
        send_line(f"{product_name} 在庫復活！ {url}")
    else:
        print(f"{product_name} 在庫状態変化なし → 通知なし")

    # 現在の在庫状態を保存
    save_current_stock_status(current_stock_status)

if __name__ == "__main__":
    check_stock()
