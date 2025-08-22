import os
import requests
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
import subprocess
import time

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

RETRY_COUNT = 3
RETRY_WAIT = 5
STATUS_FILE = "stock_status.txt"

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
    try:
        with open(STATUS_FILE, "r") as f:
            return f.read().strip() == "1"
    except FileNotFoundError:
        return False

def save_status(stock_status):
    with open(STATUS_FILE, "w") as f:
        f.write("1" if stock_status else "0")

def commit_status_file():
    """GitHubリポジトリに状態をコミットして保存"""
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "add", STATUS_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Update stock status"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("stock_status.txt をコミット・プッシュしました")
    except subprocess.CalledProcessError as e:
        print(f"Gitコミット失敗: {e}")

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
    current_stock_status = False if status_tag is None else "ご注文できない商品" not in status_tag.text

    last_stock_status = get_last_status()

    if not last_stock_status and current_stock_status:
        send_line(f"{product_name} 在庫復活！ {url}")
    else:
        print(f"{product_name} 在庫状態変化なし → 通知なし")

    save_status(current_stock_status)
    commit_status_file()

if __name__ == "__main__":
    check_stock()
